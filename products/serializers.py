from rest_framework import serializers
from .models import Category, Product
from .models import Product, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(write_only=True)   # للكتابة فقط بالاسم
    category_detail = CategorySerializer(source='category', read_only=True)  # للقراءة يعرض التفاصيل

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'category_detail']

    def create(self, validated_data):
        category_name = validated_data.pop('category')
        category, created = Category.objects.get_or_create(name=category_name)
        product = Product.objects.create(category=category, **validated_data)
        return product

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'created_at', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order