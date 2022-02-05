from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

# * Notes *
# (depth: 1 or 2 or 3) used to return all the relation table value for only direct relationship not reverse relationship

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'is_staff']

# Show orders and it's customer and product details
class ProductSerializer(serializers.ModelSerializer):
    
    class ProductOrderSerializer(serializers.ModelSerializer):

        class OrderCustomerSerializers(serializers.ModelSerializer):
    
            class Meta:
                model = Customer
                fields = ['id', 'name', 'phone', 'email']

        customer = OrderCustomerSerializers()

        class Meta:
            model = Order
            fields = ['id', 'date_created', 'status','customer']

    orders = ProductOrderSerializer(source='product_order', many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'description','orders']




# Show orders and it's product and customer
class OrderSerializer(serializers.ModelSerializer):

    class ProductSerializer(serializers.ModelSerializer):
        class Meta:
            model = Product
            fields = ['id', 'name', 'price', 'category', 'description']

    
    class OrderCustomerSerializer(serializers.ModelSerializer):
   
        class Meta:
            model = Customer
            fields = ['id', 'name', 'phone', 'email']

    customer = OrderCustomerSerializer()
    product = ProductSerializer()

    class Meta:
        model = Order
        fields = ['id', 'date_created', 'status', 'customer', 'product']
        

# Show customer and their orders
class CustomerSerializer(serializers.ModelSerializer):

    class OrderSerializers(serializers.ModelSerializer):

        class ProductSerializer(serializers.ModelSerializer):
            class Meta:
                model = Product
                fields = ['id', 'name', 'price', 'category', 'description']

        product = ProductSerializer()

        class Meta:
            model = Order
            fields = ['id', 'date_created', 'status', 'product']

    orders = OrderSerializers(source='customer_order', many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'email', 'orders']
        depth = 1


# Create Order
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status', 'customer', 'product']

# Update Order
class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']