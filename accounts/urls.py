from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from rest_framework.routers import DefaultRouter

# snippet_detail = views.OrderViewSetr.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


order_list = views.OrderViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

order_detail = views.OrderViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [

    path('register/', views.registerPage, name="register"),
    path('login_web/', views.loginPage, name="login_web"),  
    path('logout_web/', views.logoutPage, name="logout_web"),

    path('', views.home, name="home"),
    path('user/', views.userPage, name="user-page"),
    path('products/', views.products, name='products'),
    path('products_details/<str:pk_test>/', views.products_details, name="products_details"),
    path('customer/<str:pk_test>/', views.customer, name="customer"),
    path('account/', views.accountSettings, name="account"),

    path('create_order/', views.createOrder, name="create_order"),
    path('update_order/<str:pk>/', views.updateOrder, name="update_order"),
    path('delete_order/<str:pk>/', views.deleteOrder, name="delete_order"),

    path('create_customer/', views.createCustomer, name="create_customer"),
    path('update_customer/<str:pk>/', views.accountSettings, name="update_customer"),
    path('delete_customer/<str:pk>/', views.deleteCustomer, name="delete_customer"),

    path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
     name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"), 
     name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"), 
        name="password_reset_complete"),

    path('change_password/', views.change_password, name='change_password'),

    # Import and Export
    path('export/', views.export, name = "export"),
    path('import/', views.importing, name = "import"),

    #Transations
    path('trans/', views.trans, name = "trans"),

    # Api starts here...
    path('api/', views.api, name="api"),

    # JWT based login..
    # path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/logout/', views.LogoutView.as_view(), name='auth_logout'),

    # Simple Token based login..
    path('api/login/', views.login, name="login"),
    path('api/logout/', views.logout, name="logout"),

    # Api URLS (Fucntion Based)
    path('api/order-list/', views.order_list, name="order-list"),
    path('api/order-create/', views.orderCreate, name="order-create"),
    path('api/order-detail/<str:pk>/', views.orderDetail, name="order-detail"),
    path('api/order-update/<str:pk>/', views.orderUpdate, name="order-update"),
    path('api/order-delete/<str:pk>/', views.orderDelete, name="order-delete"),
    path('api/customer-list/', views.customer_list, name="customer-list"),
    path('api/product-list/', views.product_list, name="product-list"),

    # Api URLS (ApiView)
    path('api/order-list-apiview/', views.ClassOrderList.as_view(), name="order-list-apiview"),
    path('api/order-create-apiview/', views.ClassOrderList.as_view(), name="order-create-apiview"),
    path('api/order-detail-apiview/<str:pk>/', views.ClassOrderDetail.as_view(), name="order-detail-apiview"),
    path('api/order-update-apiview/<str:pk>/', views.ClassOrderDetail.as_view(), name="order-update-apiview"),
    path('api/order-delete-apiview/<str:pk>/', views.ClassOrderDetail.as_view(), name="order-delete-apiview"),

    # Api URLS (GenericView)
    path('api/class_order_list/', views.ClassOrderListGen.as_view(), name="class_order_list"),

    # Api URLS (ViewSet)
    path('api/order_list/', order_list, name='order_list'),
    path('api/order_detail/<int:pk>/', order_detail, name='order_detail'),

    
]


'''
1 - Submit email form                         //PasswordResetView.as_view()
2 - Email sent success message                //PasswordResetDoneView.as_view()
3 - Link to password Rest form in email       //PasswordResetConfirmView.as_view()
4 - Password successfully changed message     //PasswordResetCompleteView.as_view()
'''