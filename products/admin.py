from django.contrib import admin
from .models import (
    Product, Category, Order, OrderItem, Cart, CartItem,
    ProductImage, ProductVideo, ProductSize, Review, Wishlist , OrderTracking , TrackingStep ,ShippingAddress
)

# تسجيل كل الموديلات بشكل عادي بدون تخصيص
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ProductImage)
admin.site.register(ProductVideo)
admin.site.register(ProductSize)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(TrackingStep)
admin.site.register(OrderTracking)
admin.site.register(ShippingAddress)

from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    site_header = "My Admin"
    index_title = "Dashboard Home"
    site_title = "Admin Panel"

admin_site = MyAdminSite(name='myadmin')