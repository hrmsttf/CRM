from django.db import models
from django.contrib.auth.models import User
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True, unique=True)
    profile_pic = models.ImageField(default="User_Profile.png", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.PositiveIntegerField(null=True, default=1)

    BlacklistedToken.add_to_class('tk', models.CharField(max_length=500,null=True))
    BlacklistedToken.add_to_class('user', models.ForeignKey(User,blank=True, null=True, related_name='user_id_jwt', on_delete= models.SET_NULL))
   
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):

    CATEGORY = (
                ('Indoor', 'Indoor'),
                ('Out Door', 'Out Door'),
        )

    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(null=True)
    category = models.CharField(max_length=200, null=True,  choices=CATEGORY)
    description = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    tags = models.ManyToManyField(Tag)
    is_active = models.PositiveIntegerField(null=True, default=1)

    def __str__(self):
        return self.name


class Order(models.Model):

    STATUS = (
            ('pending', 'pending'),
            ('Out for delivery', 'Out for delivery'),
            ('Delivered', 'Delivered')
        )   

    customer = models.ForeignKey(Customer, null=False,  blank=False, related_name='customer_order', on_delete= models.CASCADE)
    product = models.ForeignKey(Product, null=False, blank=False, related_name='product_order', on_delete= models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200, null=False, blank=False, choices=STATUS)
    is_active = models.PositiveIntegerField(null=True, default=1)

    def __str__(self):
        return self.product.name



