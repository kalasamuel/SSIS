import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supermarket.settings")
django.setup()

from inventory.models import Category, Supplier, Product, Staff, Customer, Sale, SaleDetail

# Clear existing data if you want a clean start (uncomment to enable)
# Category.objects.all().delete()
# Supplier.objects.all().delete()
# Product.objects.all().delete()
# Staff.objects.all().delete() # Added staff to clearing
# Sale.objects.all().delete()
# SaleDetail.objects.all().delete()
# Customer.objects.all().delete() # Added customers to clearing

# --- Seed base data ---
print("Creating base data...")

categories = [
    "Beverages", "Snacks", "Dairy", "Bakery", "Frozen Foods",
    "Personal Care", "Cleaning Supplies", "Produce", "Meat", "Condiments"
]
suppliers = ["Coca-Cola Kenya", "Brookside Dairies", "Unilever East Africa", "Mega Bakery Supplies", "FreshCrop Farms"]

for c in categories:
    Category.objects.get_or_create(category_name=c)

for s in suppliers:
    Supplier.objects.get_or_create(supplier_name=s)

# --- Create staff members (more than 5) ---
print("Creating staff members...")
staff_members = [
    {"username": "jdoe_mgr", "first_name": "John", "last_name": "Doe", "role": "Manager"},
    {"username": "amark_cash", "first_name": "Alice", "last_name": "Mark", "role": "Cashier"},
    {"username": "bkimani_stk", "first_name": "Ben", "last_name": "Kimani", "role": "Stock Clerk"},
    {"username": "cnamala_cash", "first_name": "Carol", "last_name": "Namala", "role": "Cashier"},
    {"username": "dwanga_shift", "first_name": "David", "last_name": "Wanga", "role": "Shift Supervisor"},
    {"username": "emutesi_cash", "first_name": "Esther", "last_name": "Mutesi", "role": "Cashier"},
    {"username": "fadamu_deli", "first_name": "Frank", "last_name": "Adamu", "role": "Deli Assistant"},
]

staff_list = []
for s in staff_members:
    staff, _ = Staff.objects.get_or_create(
        username=s["username"],
        defaults={
            "first_name": s["first_name"],
            "last_name": s["last_name"],
            "role": s["role"],
            "password_hash": "dummyhash" # Using a dummy hash for sample data
        }
    )
    staff_list.append(staff)

# --- Real Product Data (grouped by category for selection) ---
# NOTE: Prices are illustrative and should be adjusted for local currency/scale.
real_products = {
    "Beverages": [
        ("Coca-Cola 500ml", "Coca-Cola", "btl", 1500, 2500),
        ("Keringet Water 1L", "Keringet", "btl", 800, 1500),
        ("Minute Maid Orange Juice", "Minute Maid", "carton", 3500, 5800),
        ("Nescafe Classic Jar", "Nescafe", "jar", 7000, 12000),
    ],
    "Snacks": [
        ("Lays Salted Crisps", "Lays", "bag", 700, 1300),
        ("Goodies Digestive Biscuits", "Goodies", "pack", 1200, 2000),
        ("Cadbury Dairy Milk Chocolate", "Cadbury", "bar", 1800, 3000),
        ("Mixed Nuts Trail Mix", "NutsCo", "pack", 4000, 6500),
    ],
    "Dairy": [
        ("Brookside Whole Milk 1L", "Brookside", "carton", 2500, 4200),
        ("KCC Natural Yoghurt 500ml", "KCC", "tub", 1800, 3100),
        ("Dairyland Butter 250g", "Dairyland", "pack", 3000, 5000),
        ("Cheddar Cheese Block", "Cheese King", "kg", 8000, 15000),
    ],
    "Bakery": [
        ("Brown Sliced Bread", "Bakery Fresh", "loaf", 1000, 1800),
        ("Plain White Rolls", "Bakery Fresh", "pcs", 300, 500),
        ("Muffins Chocolate Chip", "Sweet Treats", "pcs", 800, 1500),
    ],
    "Frozen Foods": [
        ("Mixed Vegetables 1kg", "Frozy", "bag", 4500, 7500),
        ("Chicken Drumsticks Frozen", "Farmers Choice", "kg", 6000, 9500),
    ],
    "Personal Care": [
        ("Colgate Toothpaste", "Colgate", "tube", 1500, 2600),
        ("Dove Soap Bar", "Dove", "pcs", 800, 1400),
        ("Always Sanitary Pads", "Always", "pack", 2000, 3500),
    ],
    "Cleaning Supplies": [
        ("OMO Detergent Powder 1kg", "OMO", "bag", 3500, 6000),
        ("Harpic Toilet Cleaner", "Harpic", "btl", 1800, 3200),
    ],
    "Produce": [
        ("Ripe Bananas", "FreshCrop", "kg", 500, 1000),
        ("Irish Potatoes", "FreshCrop", "kg", 800, 1500),
        ("Roma Tomatoes", "FreshCrop", "kg", 1200, 2200),
    ],
    "Meat": [
        ("Ground Beef", "Butchers Best", "kg", 5000, 8500),
        ("Pork Sausages", "Farmers Choice", "pack", 3000, 5500),
    ],
    "Condiments": [
        ("Ketchup Bottle 500ml", "Heinz", "btl", 2000, 3400),
        ("Salt Iodized 1kg", "Kensalt", "pack", 500, 900),
    ],
}

# --- Create products ---
print("Creating products...")
category_objects = {c.category_name: c for c in Category.objects.all()}
supplier_list = list(Supplier.objects.all())

for category_name, products_data in real_products.items():
    category_obj = category_objects.get(category_name)
    if category_obj:
        for name, brand, unit, cost, price in products_data:
            Product.objects.get_or_create(
                product_name=name,
                defaults={
                    "brand": brand,
                    "unit": unit,
                    "unit_cost": Decimal(cost).quantize(Decimal("0.01")),
                    "retail_price": Decimal(price).quantize(Decimal("0.01")),
                    "stock_quantity": random.randint(100, 500),
                    "reorder_level": 10,
                    "category": category_obj,
                    "supplier": random.choice(supplier_list)
                }
            )

# --- Generate random sales ---
print("Creating sales records...")

products = list(Product.objects.all())
customers = []
for i in range(1, 20):
    # Customer names added for better realism
    first_names = ["Sam", "Leah", "Omar", "Tasha", "Juma", "Pendo"]
    last_names = ["Ochieng", "Kariuki", "Musa", "Njeri", "Ali", "Muthoni"]
    customers.append(
        Customer.objects.create(
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            phone=f"07{random.randint(1000000,9999999)}"
        )
    )

for _ in range(150):  # ~150 sales
    # Random date in past 2 years
    random_days = random.randint(0, 730)
    sale_date = datetime.now() - timedelta(days=random_days)
    customer = random.choice(customers)
    # Assign a random staff member from the new list
    staff = random.choice(staff_list)
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
    # Ensure there are products before trying to make a sale detail
    if products:
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

print("Sample data generation complete!")
print(f"Total categories: {Category.objects.count()}")
print(f"Total suppliers: {Supplier.objects.count()}")
print(f"Total staff: {Staff.objects.count()}")
print(f"Total products: {Product.objects.count()}")
print(f"Total customers: {Customer.objects.count()}")
print(f"Total sales: {Sale.objects.count()}")
print(f"Total sale details: {SaleDetail.objects.count()}")