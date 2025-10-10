from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Supplier, Product, Customer, Staff, Discount, ProductDiscount, Sale, SaleDetail

admin.site.register([Category, Supplier, Product, Customer, Staff, Discount, ProductDiscount])
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('receipt_no','sale_datetime','total_amount','staff','payment_method')
    search_fields = ('receipt_no',)
@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    list_display = ('sale','product','quantity_sold','sub_total')
