# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.index, name='index'),        
#     path('category/', views.category, name='category'),
#     path('base/', views.base, name='base'),
#     path('mens/', views.mens, name='mens'),
#     ]
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, add_review, add_shipping_view, add_to_cart,cart_view, create_order_view, men_page,my_orders,index,order_detail_page ,categories_page, category_detail_page, mens_clothing_page, mens_clothing_api, electronics_page, Elecrtonics_api, Accessories_api, Accessories_page, new_arrivals_api, new_arrivals_page, bestsellers_api, bestsellers_page, create_order, product_detail, random_beauty_products, sale_page, toggle_wishlist, update_cart_quantity, women_page
from . views import create_order ,cart_view , product_list ,checkout_view , payment_callback, payment_success, payment_fail , search_results  ,wishlist_page , women_products_page
from rest_framework.decorators import api_view  

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    
  
    path('api/', include(router.urls)),  # REST API endpoints
    path("create-order/", create_order_view, name="create_order"),
    path("add-shipping/<int:order_id>/",add_shipping_view, name="add_shipping"),

     path("checkout/", checkout_view, name="checkout"),
    ##########
     path("",index,name="index"),
    
    path('sale/', sale_page, name='sale_page'),
    path("cart/update/<slug:slug>/",update_cart_quantity, name="update_cart_quantity"),

    ######
    path('products/', product_list, name='product_list'),  # صفحة عرض المنتجات
    ######
    # API for new arrivals
    
    path('new-arrivals/', new_arrivals_page, name='new_arrivals_page'),
    path('api/bestsellers/', bestsellers_api, name='bestsellers_api'),
    path('bestsellers/', bestsellers_page, name='bestsellers_page'),  
    
    path('order-detail/<int:order_id>/',order_detail_page, name='order_detail_page'),
    path('my-orders/', my_orders, name='my_orders_page'),

    path('mens-clothing/', mens_clothing_page, name='mens_clothing'),
    path('electronics/', electronics_page, name='electronics_page'),
    path('accessories/', Accessories_page, name='accessories_page'),
    ##################
    
    path('cart/', cart_view, name='cart_view'),
    path("cart/add/<slug:slug>/", add_to_cart, name="add_to_cart"),

    
    
    
    # هنا بنربط views مباشرة
    path('categories/', categories_page, name='categories_page'),
    path('categories/<slug:slug>/', category_detail_page, name='category_detail_page'),
  
    path("payment/callback/", payment_callback, name="payment_callback"),
    path("payment/success/<int:order_id>/", payment_success, name="payment_success"),
    path("payment/fail/<int:order_id>/", payment_fail, name="payment_fail"),
    
    path('search/', search_results, name='search_results'),

  
    path('products/<slug:slug>/', product_detail, name='product_detail'),
    
    path('women/', women_page, name='women_page'),
    path('men/', men_page, name='men_page'),
    
    path('wishlist/',wishlist_page, name='wishlist_page'),
    path("wishlist/toggle/", toggle_wishlist, name="toggle_wishlist"),

# urls.py
    path('product/<slug:slug>/add_review/',add_review, name='add_review'),
    path('beauty_product/',random_beauty_products, name='beauty_product'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)