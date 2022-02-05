from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

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

    path('api/', views.api, name="api"),

    # Api URLS
    path('api/login/', views.login, name="login"),
    path('api/order-list/', views.order_list, name="order-list"),
    path('api/order-detail/<str:pk>/', views.orderDetail, name="order-detail"),
    path('api/order-create/', views.orderCreate, name="order-create"),
    path('api/order-update/<str:pk>/', views.orderUpdate, name="order-update"),
    path('api/order-delete/<str:pk>/', views.orderDelete, name="order-delete"),
    path('api/customer-list/', views.customer_list, name="customer-list"),
    path('api/product-list/', views.product_list, name="product-list"),
    path('api/logout/', views.logout, name="logout"),

    # Api's Class based views
    path('api/class_order_list/', views.ClassOrderList.as_view(), name="class_order_list"),

]


'''
1 - Submit email form                         //PasswordResetView.as_view()
2 - Email sent success message                //PasswordResetDoneView.as_view()
3 - Link to password Rest form in email       //PasswordResetConfirmView.as_view()
4 - Password successfully changed message     //PasswordResetCompleteView.as_view()
'''