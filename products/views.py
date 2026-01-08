from decimal import Decimal
import os 
key = os.environ.get("STRIPE_SECRET_KEY")
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, ShippingAddress, Order
from .forms import ShippingAddressForm

import stripe

from .models import (
    Product, Category, Order, OrderItem,
    ShippingAddress, Payment
)
from .serializers import (
    ProductSerializer, CategorySerializer,
    OrderSerializer
)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required  
from products.models import Order
stripe.api_key = settings.STRIPE_SECRET_KEY

#####
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem

@login_required
def add_to_cart(request, slug):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':

        product = get_object_or_404(Product, slug=slug)

        # جلب أو إنشاء الكارت
        cart, created = Cart.objects.get_or_create(customer=request.user)

        # جلب أو إنشاء عنصر الكارت
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        # لو المنتج موجود قبل كده نزود الكمية
        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1

        cart_item.save()

        # عدد العناصر في الكارت
        cart_count = CartItem.objects.filter(cart=cart).count()

        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'message': 'Product added to cart'
        })

    return JsonResponse({'success': False}, status=400)





@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_items = cart.items.all()
    total = cart.total_price

    return render(request, "base/cart.html", {
        "cart_items": cart_items,
        "total": total
    })

from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

@login_required
def create_order_view(request):
    cart = get_object_or_404(Cart, customer=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        return JsonResponse({"error": "Cart is empty"})

    # إنشاء Order جديد
    order = Order.objects.create(
        customer=request.user,
        customer_name=request.user.email
    )

    # تحويل CartItems لـ OrderItems
    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    # إرسال رسالة الإيميل
    if request.user.order_updates:  # بدل 'user' استخدم request.user
        subject = f"Order Confirmation - #{order.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [request.user.email]

        # بناء تفاصيل المنتجات في جدول HTML
        items_html = ""
        for item in order.items.all():
            items_html += f"""
            <tr>
                <td style="padding:8px; border:1px solid #ddd;">{item.product.name}</td>
                <td style="padding:8px; border:1px solid #ddd; text-align:center;">{item.quantity}</td>
                <td style="padding:8px; border:1px solid #ddd; text-align:right;">${item.product.final_price:.2f}</td>
                <td style="padding:8px; border:1px solid #ddd; text-align:right;">${item.product.final_price * item.quantity:.2f}</td>
            </tr>
            """

        # حساب المجموع الكلي
        total_price = sum(item.product.final_price * item.quantity for item in order.items.all())

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height:1.5;">
                <h2 style="color:#2c3e50;">Hi {request.user.first_name},</h2>
                <p>Thank you for your order! Your order <strong>#{order.id}</strong> has been created successfully on {order.created_at.strftime('%d %b, %Y %H:%M')}.</p>
                
                <h3>Order Details:</h3>
                <table style="border-collapse: collapse; width:100%; max-width:600px;">
                    <thead>
                        <tr>
                            <th style="padding:8px; border:1px solid #ddd; text-align:left;">Product</th>
                            <th style="padding:8px; border:1px solid #ddd; text-align:center;">Quantity</th>
                            <th style="padding:8px; border:1px solid #ddd; text-align:right;">Price</th>
                            <th style="padding:8px; border:1px solid #ddd; text-align:right;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                        <tr>
                            <td colspan="3" style="padding:8px; border:1px solid #ddd; text-align:right; font-weight:bold;">Total</td>
                            <td style="padding:8px; border:1px solid #ddd; text-align:right; font-weight:bold;">${total_price:.2f}</td>
                        </tr>
                    </tbody>
                </table>

                <p>We will notify you once your order is shipped. Thank you for shopping with us!</p>
                
                <p style="color:#7f8c8d; font-size:12px;">If you have any questions, contact our support at support@example.com</p>
            </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, "", from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

    # امسح الـ cart بعد التحويل
    cart.items.all().delete()

    # حفظ order_id للخطوات الجاية
    request.session["order_id"] = order.id
    return redirect("add_shipping", order_id=order.id)

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def order_detail_page(request, order_id):
    # جلب الطلب والتأكد من أنه يخص المستخدم الحالي
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    items = order.items.select_related("product")
    total_price = 0

    # حساب الإجمالي فقط (من غير ما نكتب subtotal)
    for item in items:
        total_price += item.subtotal

    return render(request, 'base/order_detail.html', {
        'order': order,
        'items': items,
        'total_price': total_price
    })



@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'base/my_orders.html', {'orders': orders})

################





######

@api_view(['POST'])
def create_order(request):
    if not request.user.is_authenticated:
        return Response({"error": "You must be logged in to place an order"}, status=403)

    items_data = request.data.get('items', [])
    order = Order.objects.create(customer=request.user)

    for item in items_data:
        product_id = item.get('product')
        quantity = item.get('quantity', 1)
        OrderItem.objects.create(order=order, product_id=product_id, quantity=quantity)

    return Response({"message": "Order created", "order_id": order.id})

######




def add_shipping_view(request,order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping_address, created = ShippingAddress.objects.update_or_create( 
                order=order,
                defaults=form.cleaned_data,
            )
            return redirect("checkout")  # روح لصفحة الدفع أو الملخص
    else:
        form = ShippingAddressForm()

    return render(request, "base/add_shipping.html", {"form": form, "order": order})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Order, OrderItem, Payment, Product
from .paymob import authenticate, create_order, generate_payment_key

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Cart, CartItem, Order, OrderItem, Payment, Product
from .paymob import authenticate, create_order, generate_payment_key
from decimal import Decimal

from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import Cart, Order, OrderItem, Payment
from .paymob import authenticate, create_order, generate_payment_key


@login_required
def checkout_view(request):
    try:
        # 1️⃣ جلب الطلب أو إنشاؤه
        order_id = request.session.get("order_id")
        cart = None

        if order_id:
            order = get_object_or_404(Order, id=order_id, customer=request.user)
        else:
            cart, _ = Cart.objects.get_or_create(customer=request.user)

            if not cart.items.exists():
                return JsonResponse({"error": "Cart is empty"}, status=400)

            order = Order.objects.create(
                customer=request.user,
                customer_name=request.user.username,
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            request.session["order_id"] = order.id

        # 2️⃣ حساب الإجمالي بالجنيه (صح)
        total_amount = Decimal("0.00")
        for item in order.items.all():
            total_amount += Decimal(item.product.final_price) * item.quantity

        if total_amount <= 0:
            return JsonResponse({"error": "Invalid order amount"}, status=400)

        # 3️⃣ إنشاء Payment
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=total_amount,
            status="pending",
            payment_method="paymob",
        )

        # 4️⃣ PayMob
        auth_token = authenticate()

        paymob_order = create_order(
            auth_token=auth_token,
            order_id=str(payment.id),          # لازم string
            total_amount=float(total_amount)   # float فقط
        )

        payment_token = generate_payment_key(
            auth_token=auth_token,
            order_id=paymob_order["id"],
            total_amount=float(total_amount),  # float فقط
            email=request.user.email,
            billing_data={
                "first_name": request.user.first_name or "Customer",
                "last_name": request.user.last_name or "User",
                "phone_number": "+201000000000",
                "city": "Cairo",
                "country": "EG",
                "state": "Cairo"
            }
        )

        # 5️⃣ مسح الكارت
        if cart:
            cart.items.all().delete()

        # 6️⃣ التحويل لـ iframe
        iframe_url = (
            f"https://accept.paymobsolutions.com/api/acceptance/iframes/"
            f"{settings.IFRAME_ID}?payment_token={payment_token}"
        )

        return redirect(iframe_url)

    except Exception as e:
        print("⚠️ PayMob Error:", str(e))
        return JsonResponse({"error": str(e)}, status=500)

















########## REST API Views





class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def index(request):    
    return render(request, 'base/index.html')


############################

# HTML Views
def categories_page(request):
    categories = Category.objects.all()  # بدل requests
    return render(request, 'products/categories.html', {'categories': categories})

def category_detail_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)  # بدل requests
    return render(request, 'products/category_detail.html', {
        'category': category,
        'products': products
    })

##################################
@api_view(['GET','post'])
def mens_clothing_api(request):
    try:
        category = Category.objects.get(name="Men's clothing")
    except Category.DoesNotExist:
        return Response({"error": "Category 'Men's clothing' not found"}, status=404)

    products = Product.objects.filter(category=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)   # JSON


    
@api_view(['GET','post'])
def Accessories_api(request):
    try:
        category = Category.objects.get(name="Accessories")
    except Category.DoesNotExist:
        return Response({"error": "Category Accessories not found"}, status=404)

    products = Product.objects.filter(category=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)   # JSON

@api_view(['GET','post'])
def Elecrtonics_api(request):
    try:
        category = Category.objects.get(name="Electronics")
    except Category.DoesNotExist:
        return Response({"error": "Category 'Electronics' not found"}, status=404)

    products = Product.objects.filter(category=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)   # JSON



@api_view(['GET'])
def new_arrivals_api(request):
    products = Product.objects.order_by('-created_at')[:10]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def bestsellers_api(request):
    products = Product.objects.order_by('-sales_count')[:10]  # أكتر 10 مبيعًا
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

###############################################################
def mens_clothing_page(request):
    try:
        category = Category.objects.get(name="Men's clothing")
        products = Product.objects.filter(category=category)
    except Category.DoesNotExist:
        products = []

    return render(request, 'system/mens_clothing.html', {
        'name': "Men's clothing",
        'products': products
    })



def electronics_page(request):
    try:
        category = Category.objects.get(name="Electronics")
        products = Product.objects.filter(category=category)
    except Category.DoesNotExist:
        products = []

    return render(request, 'products/electronics.html', {
        'name': "Electronics",
        'products': products
    })
    
    
def Accessories_page(request):
    try:
        category = Category.objects.get(name="Accessories")
        products = Product.objects.filter(category=category)
    except Category.DoesNotExist:
        products = []

    return render(request, 'products/Accessories.html', {
        'name': "Accessories",
        'products': products
    })


    

######


def new_arrivals_page(request):
    products = Product.objects.order_by('-created_at')[:20]  # آخر 10 منتجات
    return render(request, 'system/new_arrivals.html', {
        'name': "New Arrivals",
        'products': products
    })

from django.shortcuts import render

def bestsellers_page(request):
    products = Product.objects.order_by('-sales_count')[:10]
    return render(request, 'system/bestsellers.html', {
        'name': "Bestsellers",
        'products': products
    })





# accounts/views.py







@login_required
def my_orders(request):
    # جلب الأوردرات الخاصة بالمستخدم الحالي
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'base/my_orders.html', {'orders': orders})


# views.py
from django.shortcuts import render
from .models import Category, Product

def women_products_page(request):
    # هنا بنجيب كل التصنيفات اللي تخص Women (ممكن تستخدم فلتر لو عندك حقل gender أو بس افتراضياً)
    categories = Category.objects.filter(name__in=[
        "Skin care"
    ])
    
    # نجمع المنتجات لكل تصنيف
    category_products = {}
    for category in categories:
        products = category.products.all()  # مرتبط بـ related_name="products"
        category_products[category] = products

    context = {
        "category_products": category_products
    }
    return render(request, "system/women_products.html", context)



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Wishlist
import json

def product_list(request):
    products = Product.objects.all().prefetch_related('category')
    
    filter_type = request.GET.get('filter', 'all')
    sort = request.GET.get('sort', 'price_asc')

    # Filter
    if filter_type == 'popular':
        products = products.filter(is_popular=True)
    elif filter_type == 'new':
        products = products.order_by('-created_at')
    elif filter_type == 'sale':
        products = products.filter(on_sale=True)

    # Sort
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    # إضافة حالة المفضلة لكل منتج
    for product in products:
        if request.user.is_authenticated:
            product.is_in_wishlist = Wishlist.objects.filter(
                user=request.user, 
                product=product
            ).exists()
        else:
            product.is_in_wishlist = False
    
    # باقي المنطق...
    context = {
        'products': products,
        'filter': filter_type,
        'sort': sort
    }
    return render(request, 'products/product_list.html', context)

@login_required
def toggle_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        # التحقق إذا المنتج موجود في المفضلة
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'product': product}
        )
        
        if not created:
            # إذا موجود، نزيله
            wishlist_item.delete()
            return JsonResponse({'status': 'removed'})
        else:
            # إذا غير موجود، نضيفه
            return JsonResponse({'status': 'added'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
    

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Review
from .forms import ReviewForm

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # معالجة الفورم لو POST
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('product_detail', slug=product.slug)
        else:
            return redirect('login')
    else:
        form = ReviewForm()

    # المنتجات المتعلقة
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id).order_by('-sales_count')[:4]

    return render(request, "products/product_detail.html", {
        "product": product,
        "related_products": related_products,
        "form": form,  # الفورم هنا
    })





# views.py

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Payment

from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def payment_callback(request):
    """
    دالة تستقبل الـ callback من Paymob بعد الدفع (ناجح أو فاشل)
    """
    if request.method == "GET":
        data = request.GET.dict()
        print("🔔 Paymob Callback Data:", data)

        success = data.get("success") == "true"
        order_id = data.get("merchant_order_id")
        message = data.get("data.message", "")

        if success:
            # تمرير بيانات للـ template
            return render(request, "products/payment_success.html", {
                "order_id": order_id,
                "message": message
            })
        else:
            return render(request, "products/payment_fail.html", {
                "order_id": order_id,
                "message": message
            })

    return HttpResponse(status=405)  # لو مش GET



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from .models import Order, OrderItem
from django.utils import timezone

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    items = order.items.select_related("product")
    

    total_price = sum(item.subtotal for item in items)

    context = {
        "order": order,
        "items": items,
        "total_price": total_price,
    }

    return render(request, "products/payment_success.html", context)


def payment_fail(request):
    return render(request, "products/payment_fail.html")



from django.shortcuts import render
from .models import Product  # أو أي موديل عندك يعبر عن منتجات الموقع
from django.db.models import Q

def search_results(request):
    query = request.GET.get('q', '').strip()
    results = Product.objects.none()
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'base/search_results.html', context)


from decimal import Decimal

from django.shortcuts import render
from .models import Product

def sale_page(request):
    sale_products = Product.objects.filter(discount__gt=0)

    return render(request, 'products/sale.html', {
        'sale_products': sale_products
    })






@login_required
def update_cart_quantity(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    action = request.POST.get("action")

    if action == "increase":
        cart_item.quantity += 1
        cart_item.save()
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect("cart_view")




#################################

from django.shortcuts import render
from .models import Product, Category

def women_page(request):
    # تصنيفات النساء اللي عايزين نعرض منتجاتهم
    women_categories = [
        "shirt-polos",
        "boots",
        "handbags",
        "plus-size",
        "jackets-coats",
        "sandals",
        "eyewear",
        "petite",
        "heels",
        "hats",
        "wide-shoes",
        "sneakers",
        "sweatshirts",
        "loafers",
        "belt"
        "watches",
        "narrow-shoes",
        "dresses",
        "slippers",
        "jewelry",
        "swimwear",
        
    ]

    categories = Category.objects.filter(slug__in=women_categories)
    products = Product.objects.filter(category__in=categories).distinct()

    return render(request, "system/women.html", {
        "products": products,
    })


# views.py

from django.shortcuts import render
from .models import Product, Category

def men_page(request):
    # كل الكاتيجوريز الخاصة بالرجال
    men_categories = [
        "shirts-polos",
        "sneaker",
        "watch",
        "big-tall",
        "coats-outerwear",
        "boot",
        "belts",
        "slim-fit",
        "loafers",
        "ties",
        "wallets",
        "suits",
        "sandal",
        "sunglasses",
        "activewears",
        "slipper",
        "oxfords",
        "suits",
    ]

    # هات الكاتيجوريز دي من الداتا بيز
    categories = Category.objects.filter(slug__in=men_categories)

    # هات المنتجات المرتبطة بالكاتيجوريز دي
    products = Product.objects.filter(category__in=categories).distinct()

    return render(request, "men.html", {
        "products": products,
    })






from django.shortcuts import render
from .models import Wishlist

def wishlist_page(request):
    # نفترض إنك عندك موديل Wishlist مرتبط بالمستخدم
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
    else:
        wishlist_items = []

    return render(request, 'base/wishlist.html', {'wishlist_items': wishlist_items})

# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Review

@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        if not rating:
            # ممكن ترجع رسالة خطأ أو تستخدم redirect مع message
            # حاليا هنعمل redirect بدون إنشاء review
            return redirect('product_detail', slug=slug)

        Review.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            comment=comment
        )
        
    return redirect('product_detail', slug=slug)



from django.shortcuts import render
from .models import Product, Category
import random

def random_beauty_products(request, count=20):
    # جلب تصنيف Beauty Products
    products = list(Product.objects.all())
    
    # اختيار عشوائي عدد محدد من المنتجات
    random_products = random.sample(products, min(len(products), count))
    
    return render(request, 'system/beauty_products.html', {
        'products': random_products
    })










from .models import CartItem

def base_context(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    return {'cart_count': cart_count}
