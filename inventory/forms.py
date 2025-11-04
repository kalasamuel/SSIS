from django import forms
from django.forms import inlineformset_factory
from .models import *

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
        widgets = {
            'discount_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount name'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default discount type choices
        self.fields['discount_type'].choices = [
            ('Percentage', 'Percentage (%)'),
            ('Fixed', 'Fixed Amount (UGx)'),
            ('BOGO', 'Buy One Get One (BOGO)'),
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        value = cleaned_data.get('value')
        discount_type = cleaned_data.get('discount_type')
        
        # Validate date range
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError("End date must be after start date.")
        
        # Validate value based on type
        if value is not None and value <= 0:
            raise forms.ValidationError("Discount value must be greater than 0.")
        
        if discount_type == 'Percentage' and value and value > 100:
            raise forms.ValidationError("Percentage discount cannot exceed 100%.")
        
        return cleaned_data
        
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
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'log_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'log_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional remarks...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default log type choices
        self.fields['log_type'].choices = [
            ('Purchase', 'Purchase (Stock In)'),
            ('Sale', 'Sale (Stock Out)'),
            ('Adjustment', 'Manual Adjustment'),
        ]
        
        # Set default log date to now
        if not self.instance.pk:
            self.fields['log_date'].initial = timezone.now()
    
    def clean(self):
        cleaned_data = super().clean()
        log_type = cleaned_data.get('log_type')
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')
        
        # Validate quantity
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than 0.")
        
        # For sales, check if sufficient stock is available
        if log_type == 'Sale' and product and quantity:
            if product.stock_quantity < quantity:
                raise forms.ValidationError(f"Insufficient stock. Available: {product.stock_quantity}")
        
        return cleaned_data
        
class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = '__all__'
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'allowances': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'net_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'readonly': True}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'staff': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default payment method choices
        self.fields['payment_method'].choices = [
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('check', 'Check'),
            ('mobile_money', 'Mobile Money'),
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        basic_salary = cleaned_data.get('basic_salary', 0)
        allowances = cleaned_data.get('allowances', 0) or 0
        deductions = cleaned_data.get('deductions', 0) or 0
        
        # Calculate net salary
        net_salary = basic_salary + allowances - deductions
        cleaned_data['net_salary'] = max(0, net_salary)  # Ensure non-negative
        
        return cleaned_data