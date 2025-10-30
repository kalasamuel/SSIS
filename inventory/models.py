from django.db import models
from django.utils import timezone

class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta: db_table = 'category'
    
    def __str__(self): return self.category_name

class Supplier(models.Model):
    supplier_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta: db_table = 'supplier'
    def __str__(self): return self.supplier_name

class Product(models.Model):
    product_name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100, null=True, blank=True)
    unit = models.CharField(max_length=20)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)
    reorder_level = models.IntegerField(default=10)
    batch_number = models.CharField(max_length=50, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    
    class Meta: db_table = 'product'
    def __str__(self): return self.product_name

class Customer(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    class Meta: db_table = 'customer'
    def __str__(self): return f"{self.first_name or ''} {self.last_name or ''}".strip()

class Staff(models.Model):
    ROLE_CHOICES = [('Cashier','Cashier'), ('Manager','Manager'), ('Admin','Admin')]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    
    class Meta: db_table = 'staff'
    def __str__(self): return f"{self.first_name} {self.last_name}"

class Discount(models.Model):
    TYPE_CHOICES = [('Percentage','Percentage'), ('Fixed','Fixed'), ('BOGO','BOGO')]
    discount_name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta: db_table = 'discount'
    def __str__(self): return self.discount_name

class ProductDiscount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    
    class Meta: db_table = 'product_discount'

class Sale(models.Model):
    PAYMENT_CHOICES = [('Cash','Cash'), ('Card','Card'), ('MobileMoney','MobileMoney')]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    sale_datetime = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    receipt_no = models.CharField(max_length=50, unique=True)
    
    class Meta: db_table = 'sale'
    def __str__(self): return f"Sale {self.receipt_no} - {self.total_amount}"

class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, related_name='details', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_sold = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2)
    batch_number = models.CharField(max_length=45, null=True, blank=True)
    
    class Meta: db_table = 'sale_detail'
    def __str__(self): return f"{self.product} x {self.quantity_sold}"
    
class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT)
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    invoice_no = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"PO-{self.id} for {self.supplier.supplier_name}"

    @property
    def computed_total_cost(self):
        return sum(item.subtotal for item in self.items.all())

    class Meta:
        db_table = 'purchase_order'

class PurchaseOrderDetail(models.Model):
    order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity_ordered = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity_ordered * self.unit_cost
    
    class Meta:
        db_table = 'purchase_order_detail'

class InventoryLog(models.Model):
    LOG_CHOICES = [('Purchase','Purchase'), ('Sale','Sale'), ('Adjustment','Adjustment')]
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    log_type = models.CharField(max_length=20, choices=LOG_CHOICES)
    quantity = models.IntegerField()
    log_date = models.DateTimeField(default=timezone.now)
    remarks = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'inventory_log'

class Payroll(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT)
    payment_date = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)

    class Meta:
        db_table = 'payroll'
