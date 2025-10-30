from django import forms
from django.forms import inlineformset_factory
from .models import Sale, SaleDetail, Product, Supplier, Category, Customer, Staff, Discount, PurchaseOrder, PurchaseOrderDetail, InventoryLog, Payroll
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer','staff','discount','sale_datetime','payment_method','receipt_no']

class SaleDetailForm(forms.ModelForm):
    class Meta:
        model = SaleDetail
        fields = ['product','quantity_sold','unit_price','discount_value','batch_number']

SaleDetailFormSet = inlineformset_factory(Sale, SaleDetail, form=SaleDetailForm, extra=1, can_delete=True)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['supplier', 'product_name', 'brand', 'unit', 'unit_cost', 'retail_price',
                  'stock_quantity', 'reorder_level', 'expiry_date', 'category']
        
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'role', 'phone', 'username', 'password_hash']

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = '__all__'
        
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        
class PurchaseOrderDetailForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderDetail
        fields = '__all__'
        
class InventoryLogForm(forms.ModelForm):
    class Meta:
        model = InventoryLog
        fields = '__all__'
        
class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = '__all__'