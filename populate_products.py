# scripts/populate_products.py
import sys

import os
import django

# ضبط بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # غير 'project' باسم مشروعك
django.setup()

from products.models import Category, Product
from django.utils.text import slugify

# تعريف التصنيفات والمنتجات لكل تصنيف
data = {
    "Clothing": [
        {"name": "Shirts & Polos", "price": 29.99},
        {"name": "Jackets & Coats", "price": 79.99},
        {"name": "Underwear", "price": 15.99},
        {"name": "Hoodies", "price": 39.99},
        {"name": "Suits", "price": 199.99},
        {"name": "Activewear", "price": 49.99},
    ],
    "Shoes": [
        {"name": "Sneakers", "price": 59.99},
        {"name": "Boots", "price": 89.99},
        {"name": "Loafers", "price": 69.99},
        {"name": "Dress Shoes", "price": 99.99},
        {"name": "Sandals", "price": 29.99},
        {"name": "Slippers", "price": 19.99},
    ],
    "Accessories": [
        {"name": "Watches", "price": 149.99},
        {"name": "Belts", "price": 24.99},
        {"name": "Ties", "price": 19.99},
        {"name": "Wallets", "price": 34.99},
        {"name": "Sunglasses", "price": 59.99},
        {"name": "Hats", "price": 14.99},
        {"name": "Scarves", "price": 22.99},
        {"name": "Gloves", "price": 19.99},
        {"name": "Hair Accessories", "price": 9.99},
        {"name": "Backpacks", "price": 49.99},
    ],
    "Specialty Sizes": [
        {"name": "Big & Tall", "price": 59.99},
        {"name": "Slim Fit", "price": 49.99},
        {"name": "Extended Sizes", "price": 69.99},
    ],
    "By Age": [
        {"name": "Babies (0-24 months)", "price": 19.99},
        {"name": "Toddlers (2-4 years)", "price": 24.99},
        {"name": "Kids (4-7 years)", "price": 29.99},
        {"name": "Older Kids (8-14 years)", "price": 34.99},
    ]
}

# إضافة كل التصنيفات والمنتجات
for category_name, products in data.items():
    category, created = Category.objects.get_or_create(name=category_name)
    if created:
        category.slug = slugify(category_name)
        category.save()
    for prod in products:
        product_name = prod['name']
        price = prod['price']
        # تحقق لو المنتج موجود مسبقًا لنكررهش
        product, p_created = Product.objects.get_or_create(
            name=product_name,
            category=category,
            defaults={
                "price": price,
                "description": f"Description for {product_name}",
            }
        )
        if p_created:
            product.save()
        print(f"Added product: {product_name} under {category_name}")

print("✅ Done populating products.")
