from django.contrib import admin
from django.db import transaction
from django.utils import timezone
from datetime import date
from django.contrib import messages

# Register your models here.
from django.contrib import admin
from .models import Category, Supplier, Product, Customer, Staff, Discount, ProductDiscount, Sale, SaleDetail, InventoryLog

def writeoff_expired_products(modeladmin, request, queryset):
    """Admin action to write off expired products"""
    today = date.today()
    
    # Filter to only expired products with stock
    expired_products = queryset.filter(
        expiry_date__lt=today,
        stock_quantity__gt=0
    )
    
    if not expired_products.exists():
        messages.info(request, 'No expired products found in the selected items.')
        return
    
    # Get or create system staff member
    try:
        staff = Staff.objects.get(username='system')
    except Staff.DoesNotExist:
        staff = Staff.objects.create(
            first_name='System',
            last_name='User',
            role='Admin',
            username='system',
            password_hash='system_user'
        )
    
    # Process write-offs in a transaction
    with transaction.atomic():
        total_loss = 0
        processed_count = 0
        
        for product in expired_products:
            qty_before = product.stock_quantity
            # Create inventory log entry
            InventoryLog.objects.create(
                staff=staff,
                product=product,
                log_type='Adjustment',
                quantity=-qty_before,
                remarks='expiry_writeoff',
                log_date=timezone.now()
            )
            
            # Calculate loss
            loss_amount = qty_before * product.unit_cost
            total_loss += loss_amount
            
            # Set stock quantity to 0
            product.stock_quantity = 0
            product.save()
            
            processed_count += 1
    
    messages.success(
        request,
        f'Successfully wrote off {processed_count} expired products. '
        f'Total loss: ${total_loss:.2f}'
    )

writeoff_expired_products.short_description = "Write off expired products"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'brand', 'category', 'supplier', 'stock_quantity', 'expiry_date', 'unit_cost', 'retail_price')
    list_filter = ('category', 'supplier', 'expiry_date')
    search_fields = ('product_name', 'brand')
    actions = [writeoff_expired_products]

admin.site.register([Category, Supplier, Customer, Staff, Discount, ProductDiscount])
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('receipt_no','sale_datetime','total_amount','staff','payment_method')
    search_fields = ('receipt_no',)
@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    list_display = ('sale','product','quantity_sold','sub_total')
