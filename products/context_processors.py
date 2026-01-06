# context_processors.py
from .models import Wishlist

def wishlist_context(request):
    context = {}
    if request.user.is_authenticated:
        # جلب IDs جميع المنتجات في مفضلة المستخدم
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)
        context['wishlist_ids'] = list(wishlist_ids)
    else:
        context['wishlist_ids'] = []
    return context



from .models import Cart, CartItem

def cart_counter(request):
    cart_count = 0

    cart_id = request.session.get('cart_id')

    if cart_id:
        cart_count = CartItem.objects.filter(cart_id=cart_id).count()

    return {'cart_count': cart_count}
