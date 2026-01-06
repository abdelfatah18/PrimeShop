from django.urls import path 

from . import views

urlpatterns = [
    path('support/', views.support, name='support'), 
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'), 
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.tos, name='tos'),
    path('return-policy/', views.return_policy, name='return_policy'),
    path('shipping-info/', views.shiping_info, name='shiping_info'),
    path('account/', views.account, name='my_account'),
    path('add-all-wishlist-to-cart/', views.add_all_wishlist_to_cart, name='add_all_wishlist_to_cart'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('test',views.test,name='test'),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('size-guide/', views.size_guide, name='size_guide'),

]
