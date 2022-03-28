from datetime import datetime
from urllib import request
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
 
# Create your views here.
from .models import *
from .models import Customer, Order, User_Balance
from .forms import OrderForm, CreateUserForm, CustomerForm
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import OrderSerializer, CustomerSerializer, OrderCreateSerializer, OrderUpdateSerializer, ProductSerializer, UserSerializer

from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .pagination import PaginationPage
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator, EmptyPage
from rest_framework import status
from rest_framework import viewsets
from django.http import Http404
from rest_framework.permissions import IsAdminUser, BasePermission, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from faker import Faker
from .thread import CreateProductThread
import pandas as pd
from django.conf import settings
from .forms import Payment
import decimal
from django.db import transaction
from django.http import HttpResponseRedirect
from rest_framework.throttling import ScopedRateThrottle
from django.db.models import Count

# Simple Token base login..
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    user_id = Token.objects.get(key=token.key).user_id
    user = User.objects.get(id=user_id)
    serializer = UserSerializer(user)
    return Response({'token': token.key, "user": serializer.data},
                    status=HTTP_200_OK)

# Simple Token based logout..
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def logout(request):
    request.user.auth_token.delete()
    return Response(status=HTTP_200_OK)


# JWT LOGOUT
# class LogoutView(APIView):
#     permission_classes = (IsAuthenticated,)

#     def post(self, request, *args, **kwargs):
#         try:
#             user_id = request.user.id  
#             token = request.auth
#             # print(user_id)
#             get_token = OutstandingToken.objects.filter(user_id = user_id).order_by('-id')[0]
#             # print(get_token.id)
#             create = BlacklistedToken.objects.create(user_id=user_id, token_id = get_token.id, tk = token, blacklisted_at = datetime.now() )
           
#             return Response(status=status.HTTP_205_RESET_CONTENT)
#         except Exception as e:
#             return Response(status=status.HTTP_400_BAD_REQUEST)



@unauthenticated_user
def registerPage(request):

    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='customer')
            user.groups.add(group)

            Customer.objects.create(
                user=user,
                name=user.username,
            )

            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
       
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)


def logoutPage(request):
    auth_logout(request)
    return redirect('login_web')


@login_required(login_url='login_web')
@admin_only
def home(request):

    # Threading is concept to run operation in the background because some tasks will take more to complete that time we can use threading concept.. 
    # count = 5
    # CreateProductThread(count).start()

    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='pending').count()

    context = {'orders': orders, 'customers': customers,
               'total_orders': total_orders, 'delivered': delivered,
               'pending': pending}

    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login_web')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.customer_order.all()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders': orders, 'total_orders': total_orders,
               'delivered': delivered, 'pending': pending}
    return render(request, 'accounts/user.html', context)


@login_required(login_url='login_web')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login_web')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()

    return render(request, 'accounts/products.html', {'products': products})


@login_required(login_url='login_web')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.customer_order.all()
    order_count = orders.count()

    # print(orders[0].customer)

    context = {'customer': customer,
               'orders': orders, 'order_count': order_count}
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login_web')
@allowed_users(allowed_roles=['admin'])
def products_details(request, pk_test):
    product = Product.objects.get(id=pk_test)
    orders = product.product_order.all()
    order_count = orders.count()

    context = {'product': product, 'orders': orders,
               'order_count': order_count}
    return render(request, 'accounts/product_details.html', context)


@login_required(login_url='login_web')
@allowed_users(allowed_roles=['admin'])
def createOrder(request):
    form = OrderForm()
    if request.method == 'POST':
        #print('Printing POST:', request.POST)
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order created successfully!')
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login_web')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):

    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated successfully!')
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login_web')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('/')

    context = {'item': order}
    return render(request, 'accounts/delete.html', context)


@login_required(login_url='login_web')
@admin_only
def createCustomer(request):
    form = CustomerForm()
    QueryDict = request.POST
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():

            username = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            # print(username);

            user = User.objects.create_user(
                username=username, email=email, password='admin@123')
            group = Group.objects.get(name='customer')
            user.groups.add(group)

            customer = form.save(commit=False)
            customer.user = user
            customer.save()

            # Customer.objects.create(
            #     user=user,
            #     name=user.username,
            #     email = email,
            #     phone = phone,
            # )

            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/customer_form.html', context)


@login_required(login_url='login_web')
@admin_only
def updateCustomer(request, pk):

    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/customer_form.html', context)


@login_required(login_url='login_web')
@admin_only
def deleteCustomer(request, pk):
    customer = Customer.objects.get(id=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('/')

    context = {'item': customer}
    return render(request, 'accounts/delete_customer.html', context)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('/api/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

def export(request):
    objs = Product.objects.all()
    data =[]

    for obj in objs:
        data.append({
            "product_name": obj.name,
            "price": obj.price,
            "category": obj.category,
            "description": obj.description

        })

    pd.DataFrame(data).to_excel('output.xlsx')
    return JsonResponse({
        'status': 200
    })


def importing(request):
    if request.method == 'POST':
        file = request.FILES['files']
        obj = Import.objects.create(
            files = file
        )
        path = file.file
        # print(f'{settings.BASE_DIR}/{path}')
        
        header_list = ['product_name','price','category','description']
        df = pd.read_excel(path)
        # df = pd.DataFrame(data, columns= header_list)
        
        # print(df)

        for d in df.index:
            # print(df['product_name'][d])
            Product.objects.create(
                name = df['product_name'][d],
                price = df['price'][d],
                category = df['category'][d],
                description = df['description'][d]
            )

    return render(request, 'excel.html')


def trans(request):
    if request.method == 'POST':
        form = Payment(request.POST)
        if form.is_valid():
            try:
                x = form.cleaned_data['payor']
                y = form.cleaned_data['payee']
                z = decimal.Decimal(form.cleaned_data['amount'])

                with transaction.atomic():
                    # payor = User_Balance.objects.select_for_update().get(name=x)
                    # payee = User_Balance.objects.select_for_update().get(name=y)

                    payor = User_Balance.objects.get(name=x)
                    payor.balance -= z
                    payor.save()

                    payee = User_Balance.objects.get(name=y)
                    payee.balance += z
                    payee.save()

                return redirect(request.META.get('HTTP_REFERER'))

            except Exception as e:
                return HttpResponse(e)


    else:
        form = Payment()
    return render(request, 'accounts/transactions.html', {'form': form})
 
@api_view(['GET'])
def api(request):

    api_urls = {
        'List': '/order-list/',
        'Detail View': '/task-detail/<str:pk>/',
        'Create': '/task-create/',
        'Update': '/task-update/<str:pk>/',
        'Delete': '/task-delete/<str:pk>/',
    }

    return Response(api_urls)

# JWT permission check..
# class IsTokenValid(BasePermission):
#     def has_permission(self, request, view):
#         user_id = request.user.id            
#         is_allowed_user = True
#         # token = request.auth
#         token = request.auth
#         # print(token)
#         try:
#             is_blackListed = BlacklistedToken.objects.get(user=user_id, tk=token)
#             if is_blackListed:
#                 is_allowed_user = False
#         except BlacklistedToken.DoesNotExist:
#             is_allowed_user = True
#         return is_allowed_user

class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

@api_view(['GET'])
@permission_classes((IsAuthenticated, IsSuperUser ))
# def order_list(request):
#     orders = Order.objects.filter(is_active=1).order_by('-id')
#     # print(orders[0].customer.name)
#     serializer = OrderSerializer(orders, many=True)
#     return Response(serializer.data)

# Pagination in function based view - rest
def order_list(request):

    paginator = PageNumberPagination()
    paginator.page_size = 1
    orders = Order.objects.filter(is_active=1).order_by('-id')
    result_page = paginator.paginate_queryset(orders, request)
    serializer = OrderSerializer(result_page, many=True)
    # return Response(serializer.data)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def order_counts(request):

    json = {
        'total_orders': Order.objects.filter(is_active=1).count(),
        'pending_orders': Order.objects.filter(is_active=1, status="pending").count(),
        'delivered_orders': Order.objects.filter(is_active=1, status="Delivered").count(),
        'ofd_orders': Order.objects.filter(is_active=1, status="Out for delivery").count(),
      
    }

    result = Order.objects.all().values('status').annotate(total=Count('status')).order_by('status')
    # print(result)
    return Response(json)


@api_view(['GET'])
def customer_list(request):
    customers = Customer.objects.filter(is_active=1).order_by('-id')
    # print(orders[0].customer.name)
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def product_list(request):
    products = Product.objects.filter(is_active=1).order_by('-id')
    # print(orders[0].customer.name)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

    # paginator = PageNumberPagination()
    # paginator.page_size = 5
    # products = Product.objects.filter(is_active=1).order_by('-id')
    # result_page = paginator.paginate_queryset(products, request)
    # serializer = ProductSerializer(result_page, many=True)
    # # return Response(serializer.data)
    # return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def product_detail(request, pk):
    product = Product.objects.get(id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
def product_update(request, pk):
    product = Product.objects.get(id=pk)
    serializer = ProductSerializer(instance=product, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data, status= HTTP_200_OK)


@api_view(['GET'])
def orderDetail(request, pk):
    tasks = Order.objects.get(id=pk)
    serializer = OrderSerializer(tasks, many=False)
    return Response(serializer.data)
    


@api_view(['POST'])
def orderCreate(request):
    serializer = OrderCreateSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response('Order created successfully..',)

# {
#     "status": "pending",
#     "customer": "22",
#     "product": "2"
# }


@api_view(['POST'])
def orderUpdate(request, pk):
    order = Order.objects.get(id=pk)
    serializer = OrderUpdateSerializer(instance=order, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data, status= HTTP_200_OK)

# {
#     "status": "Out for delivery",
# }


@api_view(['DELETE'])
def orderDelete(request, pk):
    order = Order.objects.get(id=pk)
    order.delete()

    return Response('Item succsesfully delete!')


# Pagination with ApiView with class based
class ClassOrderList(APIView):

    def get(self, request, format=None):
        paginator = PageNumberPagination()
        paginator.page_size = 1
        order_list = Order.objects.filter(is_active=1).order_by('-id')
        results = paginator.paginate_queryset(order_list, request)
        serializer = OrderSerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Pagination with ApiView with class based
class ClassOrderDetail(APIView):

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = OrderSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        order = Order.objects.get(id=pk)
        serializer = OrderUpdateSerializer(instance=order, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        order = Order.objects.get(id=pk)
        order.delete()
        return Response('Order succsesfully deleted!', status=status.HTTP_204_NO_CONTENT)


# Pagination with GenericView with class based
class ClassOrderListGen(generics.ListAPIView):
    serializer_class = OrderSerializer
    pagination_class = PaginationPage
    permission_classes = [IsSuperUser]

    # throttle_scope = 'robots'
    # throttle_classes = (ScopedRateThrottle,)

    def get_queryset(self):
        order_list = Order.objects.filter(is_active = 1).order_by('-id')

        return order_list


# Pagination with ViewSet with class based
class OrderViewSet(viewsets.ViewSet):
  
    def list(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 1
        order_list = Order.objects.filter(is_active=1).order_by('-id')
        results = paginator.paginate_queryset(order_list, request)
        serializer = OrderSerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)
      
    def create(self, request):
        return Response('Create called!', status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk=None):
        return Response('Retrieve called!', status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        return Response('Update called!', status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None):
        return Response('Partial_update called!', status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        return Response('Destroy called!', status=status.HTTP_204_NO_CONTENT)
