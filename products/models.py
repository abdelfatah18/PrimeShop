from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify

# models.py

from django.db import models
from django.conf import settings
from decimal import Decimal

class Cart(models.Model):
    customer = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="user_carts",  # اسم مميز عن الـ Order
)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
              return f"Cart of {self.customer.first_name} {self.customer.last_name }"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def subtotal(self):
       return Decimal(self.product.final_price) * self.quantity

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        # لو مفيش slug، يولده من الاسم
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name


from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from django.db.models import Avg
from django.db import models
from django.conf import settings
from django.db.models import Avg

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2 , default=70)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="products")
    slug = models.SlugField(blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sales_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    discount = models.PositiveIntegerField(default=0)
    is_popular = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=False)

   

    @property
    def final_price(self):
        if self.discount > 0:
            return self.price - (self.price * Decimal(self.discount) / Decimal(100))
        return self.price

    

    @property
    def display_price(self):
        """يرجع HTML جاهز للعرض بدون الحاجة لـ if في القالب"""
        if self.discount > 0:
            return f'<span class="text-muted text-decoration-line-through">${self.price}</span> ' \
                   f'<span class="text-danger fw-bold ms-2">${self.final_price:.2f}</span> ' \
                   f'<span class="badge bg-success ms-1">-{self.discount}%</span>'
        return f'${self.price}'


    def save(self, *args, **kwargs):
        # ✅ slug بيتولّد دايمًا من الاسم
        base_slug = slugify(self.name)
        new_slug = base_slug
        counter = 1

        # لو في منتج تاني بنفس الـ slug نضيف رقم في الآخر
        while Product.objects.filter(slug=new_slug).exclude(pk=self.pk).exists():
            new_slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = new_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(avg or 0, 1)  
    
    


    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(avg or 0, 1)

    @property
    def full_stars(self):
        return int(self.average_rating)

    @property
    def half_star(self):
        return 1 if self.average_rating - self.full_stars >= 0.5 else 0

    @property
    def empty_stars(self):
        return 5 - self.full_stars - self.half_star

    @property
    def review_count(self):
        return self.reviews.count()
    

class Order(models.Model):
    customer_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # بيربط الأوردر باليوزر اللي سجل دخول
        on_delete=models.CASCADE,
        related_name="orders",
        default=1
    )
    
    
    @property
    def total_price(self):
     return sum(item.product.final_price * item.quantity for item in self.items.all())


    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        # أول مرة ينضاف فيها OrderItem نزود مبيعات المنتج
        if not self.pk:
            self.product.sales_count += self.quantity
            self.product.save()
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return Decimal(self.product.final_price) * self.quantity



    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    
class Payment(models.Model):
    PAYMENT_CHOICES = [
        ("credit_card", "Credit / Debit Card"),
        ("paypal", "PayPal"),
        ("apple_pay", "Apple Pay"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)

    amount = models.DecimalField(max_digits=10, decimal_places=2)  # السعر الكلي
    status = models.CharField(max_length=20, default="pending")    # pending / success / failed
    transaction_id = models.CharField(max_length=200, blank=True, null=True)  # رقم العملية من Stripe

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status} - {self.amount}$"



class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipping_address")

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shipping for Order #{self.order.id}"



class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/gallery/")


class ProductVideo(models.Model):
    product = models.OneToOneField(Product, related_name="video", on_delete=models.CASCADE)
    video = models.FileField(upload_to="products/videos/", blank=True, null=True)


class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name="sizes", on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.size}"


class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,  related_name="reviews", on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


from django.conf import settings
from django.db import models

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , related_name="wishlist_items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product}"

    class Meta:
        unique_together = ('user', 'product')

    
    

class OrderTracking(models.Model):
    order = models.OneToOneField(Order, related_name="tracking", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tracking for Order #{self.order.id}"

class TrackingStep(models.Model):
    tracking = models.ForeignKey(OrderTracking, related_name="steps", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, default='bi-check')

    class Meta:
        ordering = ['date']  # ترتيب الخطوات حسب التاريخ

    def __str__(self):
        return f"{self.title} - {self.tracking.order.id}"


from django.conf import settings
from django.db import models

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    is_default = models.BooleanField(default=False)  # لتحديد العنوان الافتراضي
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address}, {self.city}"
