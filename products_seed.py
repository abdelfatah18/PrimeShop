import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from products.models import Category, Product

categories = [
    "Shirts & Tops",
    "Boots",
    "Handbags",
    "Plus Size",
    "Coats & Outerwear",
    "Sandals",
    "Eyewear",
    "Petite",
    "Underwear",
    "Heels",
    "Hats",
    "Wide Shoes",
    "Sweatshirts",
    "Loafers",
    "Watches",
    "Narrow Shoes",
    "Dresses",
    "Slippers",
    "Jewelry",
    "Swimwear",
    "Oxfords",
    "Belts",
]

for cat_name in categories:
    category_obj, created = Category.objects.get_or_create(name=cat_name)
    print(f"✅ Category: {cat_name}")

    for i in range(1, 6):
        product_name = f"{cat_name} Product {i}"

        # Avoid duplicate if script runs twice
        if not Product.objects.filter(name=product_name, category=category_obj).exists():
            Product.objects.create(
                name=product_name,
                description=f"Auto generated product for {cat_name}",
                price=Decimal(50 + (i * 10)),
                category=category_obj,
            )
            print(f"   ➕ Added product: {product_name}")
        else:
            print(f"   ⚠️ Already exists: {product_name}")

print("\n✅ Completed Seeding!")
print(f"📦 Total Products: {Product.objects.count()}")
