from django.shortcuts import render

from django.shortcuts import render, redirect
from .forms import ContactForm

from django.contrib.auth.decorators import login_required

# Create your views here.
def support(request):
    return render(request, 'plus/support.html')

from django.shortcuts import render
from .forms import ContactForm

from django.shortcuts import render, redirect
from .forms import ContactForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Your message has been sent. Thank you!')
            return redirect('contact')  # بعد الحفظ، اعملي redirect
    else:
        form = ContactForm()

    return render(request, 'plus/contact.html', {'form': form})




def about(request):
    return render(request,'plus/about.html')


def privacy_policy(request):
    return render(request, 'plus/privacy.html')


def tos(request):
    return render(request, 'plus/tos.html')


def return_policy(request):
    return render(request, 'plus/return-policy.html')

def shiping_info(request):
    return render(request, 'plus/shiping-info.html')

def size_guide(request):
    return render(request, 'plus/size_guide.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserUpdateForm, EmailPreferencesForm

from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserUpdateForm, EmailPreferencesForm
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator



@login_required
def account(request):
    
    user = request.user 
  
    # =======================

    # =======================
    # Wishlist Items
    # =======================
    wishlist_items = user.wishlist_items.select_related('product').all()
    for item in wishlist_items:
        item.out_of_stock = item.product.sizes.filter(in_stock=True).count() == 0

    # =======================
    # Personal info form
    # =======================
    user_form = UserUpdateForm(instance=user)
    if request.method == 'POST' and 'update_info' in request.POST:
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Your changes have been saved successfully!")
            return redirect('/app/account/#personal')  # يرجع لنفس التبويب

    # =======================
    # Email preferences form
    # =======================
    pref_form = EmailPreferencesForm(initial={
        'order_updates': getattr(user, 'order_updates', False),
        'promotions': getattr(user, 'promotions', False),
        'newsletter': getattr(user, 'newsletter', False),
    })

    if request.method == 'POST' and 'update_preferences' in request.POST:
        pref_form = EmailPreferencesForm(request.POST)
        if pref_form.is_valid():
            # حفظ التفضيلات في الـ user
            user.order_updates = pref_form.cleaned_data['order_updates']
            user.promotions = pref_form.cleaned_data['promotions']
            user.newsletter = pref_form.cleaned_data['newsletter']
            user.save()

            messages.success(request, "Preferences updated successfully!")

            # إرسال إيميلات حسب التفضيلات
            if user.order_updates:
                send_mail(
                    'Order Updates Enabled',
                    'You will now receive notifications about your orders.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            if user.promotions:
                send_mail(
                    'Promotions Enabled',
                    'You will now receive emails about new promotions and deals.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            if user.newsletter:
                send_mail(
                    'Newsletter Subscription Enabled',
                    'You are now subscribed to our weekly newsletter.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

            return redirect('/app/account/#preferences')  # يرجع للتبويب نفسه

    # =======================
    # Password form
    # =======================
    password_form = PasswordChangeForm(user=user)
    if request.method == 'POST' and 'update_password' in request.POST:
        password_form = PasswordChangeForm(user=user, data=request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            return redirect('/app/account/#security')  # يرجع لتبويب الباسورد
    
    orders = request.user.orders.all().order_by('-id')
    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # =======================
    # Context & Render
    # =======================
    context = {
        'wishlist_items': wishlist_items,
        'user_form': user_form,
        'pref_form': pref_form,
        'password_form': password_form,
        'page_obj': page_obj

    }

    return render(request, "plus/account.html", context)



from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from products.models import Wishlist, Cart, CartItem

@login_required
def add_all_wishlist_to_cart(request):
    wishlist_items = request.user.wishlist_items.all()
    cart, created = Cart.objects.get_or_create(customer=request.user)

    for item in wishlist_items:
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=item.product,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()

    return redirect('my_account')  # ارجع لنفس صفحة الحساب بعد الإضافة



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    item.delete()
    return redirect('my_account')

def test(request):
    return render (request,"plus/test.html")



# views.py
from django.shortcuts import render
from products.models import Order
from django.db.models import Q

def orders_list(request):
    query = request.GET.get('q')
    orders = Order.objects.all()

    if query:
        # نبحث في customer_name أو رقم الطلب أو اسم المنتج داخل كل Order
        orders = orders.filter(
            Q(customer_name__icontains=query) |
            Q(id__icontains=query) |
            Q(items__product__name__icontains=query)
        ).distinct()  # distinct مهم عشان لو نفس الطلب فيه أكتر من منتج متطابق، يظهر مرة واحدة بس

    return render(request, 'orders_list.html', {'orders': orders})



from django.shortcuts import render, get_object_or_404, redirect
from products.models import Review
from django.contrib.auth.decorators import login_required
from products.forms import ReviewForm  # لو عندك Form

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('my_account')  # عدّل حسب صفحة الحساب عندك
    else:
        form = ReviewForm(instance=review)

    return render(request, 'edit_review.html', {'form': form})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        review.delete()
        return redirect('my_account')  # عدّل حسب الصفحة اللي ترجع لها
    return render(request, 'delete_review.html', {'review': review})



# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, EmailPreferencesForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def account_settings(request):
    user = request.user

    if request.method == 'POST':
        if 'update_info' in request.POST:
            user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Your changes have been saved successfully!")
                return redirect('account_settings')

        elif 'update_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # لمنع تسجيل الخروج بعد تغيير الباس
                messages.success(request, "Your password has been updated successfully!")
                return redirect('account_settings')

        elif 'update_preferences' in request.POST:
            pref_form = EmailPreferencesForm(request.POST)
            if pref_form.is_valid():
                # هنا تحفظ القيم في الموديل الخاص بالإعدادات
                messages.success(request, "Preferences updated successfully!")
                return redirect('account_settings')

    else:
        user_form = UserUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)
        pref_form = EmailPreferencesForm(initial={
            'order_updates': True, 
            'promotions': False, 
            'newsletter': True
        })

    context = {
        'user_form': user_form,
        'password_form': password_form,
        'pref_form': pref_form
    }

    return render(request, 'account_settings.html', context)




