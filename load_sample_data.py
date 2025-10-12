import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supermarket.settings")
django.setup()

from inventory.models import Category, Supplier, Product, Staff, Customer, Sale, SaleDetail

# Clear existing data if you want a clean start
# Category.objects.all().delete()
# Supplier.objects.all().delete()
# Product.objects.all().delete()
# Sale.objects.all().delete()
# SaleDetail.objects.all().delete()

# ---------- Seed base data ----------
print("Creating base data...")

categories = [
    "Beverages", "Snacks", "Dairy", "Bakery", "Frozen Foods",
    "Personal Care", "Cleaning Supplies", "Produce", "Meat", "Condiments"
]
suppliers = ["Acme Distributors", "FreshFarm", "Global Foods Ltd", "City Wholesalers", "Ocean Suppliers"]

for c in categories:
    Category.objects.get_or_create(category_name=c)

for s in suppliers:
    Supplier.objects.get_or_create(supplier_name=s)

staff, _ = Staff.objects.get_or_create(
    username="cashier1",
    defaults={
        "first_name": "Grace",
        "last_name": "Namakula",
        "role": "Cashier",
        "password_hash": "dummyhash"
    }
)

# ---------- Create products ----------
print("Creating products...")
category_list = list(Category.objects.all())
supplier_list = list(Supplier.objects.all())

for i in range(1, 31):  # 30 products
    Product.objects.get_or_create(
        product_name=f"Product {i}",
        defaults={
            "brand": random.choice(["BrandA", "BrandB", "BrandC"]),
            "unit": "pcs",
            "unit_cost": Decimal(random.uniform(500, 10000)).quantize(Decimal("0.01")),
            "retail_price": Decimal(random.uniform(2000, 20000)).quantize(Decimal("0.01")),
            "stock_quantity": random.randint(100, 500),
            "reorder_level": 10,
            "category": random.choice(category_list),
            "supplier": random.choice(supplier_list)
        }
    )

# ---------- Generate random sales ----------
print("Creating sales records...")

products = list(Product.objects.all())
customers = []
for i in range(1, 20):
    customers.append(
        Customer.objects.create(first_name=f"Customer{i}", last_name="Test", phone=f"07{random.randint(1000000,9999999)}")
    )

for _ in range(150):  # ~150 sales
    # Random date in past 2 years
    random_days = random.randint(0, 730)
    sale_date = datetime.now() - timedelta(days=random_days)
    customer = random.choice(customers)
    payment_method = random.choice(["Cash", "Card", "MobileMoney"])
    receipt_no = f"R{random.randint(10000,99999)}"

    sale = Sale.objects.create(
        customer=customer,
        staff=staff,
        sale_datetime=sale_date,
        total_amount=0,
        payment_method=payment_method,
        receipt_no=receipt_no
    )

    total = Decimal("0.00")
    for _ in range(random.randint(1, 5)):  # 1–5 items per sale
        product = random.choice(products)
        qty = random.randint(1, 10)
        sub_total = product.retail_price * qty
        SaleDetail.objects.create(
            sale=sale,
            product=product,
            quantity_sold=qty,
            unit_price=product.retail_price,
            sub_total=sub_total
        )
        total += sub_total

    sale.total_amount = total
    sale.save()

print("✅ Sample data generation complete!")
print(f"Total categories: {Category.objects.count()}")
print(f"Total products: {Product.objects.count()}")
print(f"Total sales: {Sale.objects.count()}")
print(f"Total sale details: {SaleDetail.objects.count()}")
