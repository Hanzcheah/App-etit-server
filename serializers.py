from django.contrib.auth.models import User, Group
from rest_framework import serializers
from etwsystems.models import Menus, Restaurants, Categories, Orders, OrderDetails, Customer


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class ResSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurants
        fields = ('resno', 'name', 'resdescription', 'image','location') 

class RestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurants

        fields = '__all__'              

class MenusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menus
        fields = '__all__'          
        # fields = ('itemname', 'itemdescription', 'itemno')

class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'          

class ResPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'  

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'  

class CustomerSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('customerno','name','email','phone_number','totalspent' )

class ResPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders        
        fields = '__all__'  


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = '__all__'   
        depth = 2   

class OrderSerializer2(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = '__all__'   
