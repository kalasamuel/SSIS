from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib import messages
from django.db import transaction

from .models import (
    Sale, SaleDetail, Product, Supplier, Category,
    Customer, Staff, Discount, PurchaseOrder,
    PurchaseOrderDetail, InventoryLog, Payroll
)
from .forms import (
    SaleForm, SaleDetailForm, SaleDetailFormSet, ProductForm, SupplierForm,
    CategoryForm, CustomerForm, SaffForm, DiscountForm, PurchaseOrderForm,
    PurchaseOrderDetailForm, InventoryLogForm, PayrollForm
)


from django.http import JsonResponse
from django.db.models import Sum, F, FloatField
from django.db.models.functions import ExtractYear, ExtractQuarter, ExtractMonth


from django.utils import timezone
from datetime import timedelta


from datetime import timedelta, date
from django.utils.timezone import now

# ---------------------------------------------------------
# DASHBOARD / HOME PAGE
# ---------------------------------------------------------
def authentication(request):
    pass

def home(request):
    total_sales = Sale.objects.count()
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_staff = Staff.objects.count()
    return render(request, "inventory/home.html", {
        "total_sales": total_sales,
        "total_products": total_products,
        "total_customers": total_customers,
        "total_staff": total_staff,
    })

def dashboard(request):
    today = now().date()
    last_month = today - timedelta(days=30)
    previous_month = today - timedelta(days=60)

    current_sales = Sale.objects.filter(
        sale_datetime__gte=last_month
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    past_sales = Sale.objects.filter(
        sale_datetime__gte=previous_month,
        sale_datetime__lt=last_month
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    growth = ((current_sales - past_sales) / past_sales * 100) if past_sales > 0 else 0

    context = {
        "current_sales": current_sales,
        "past_sales": past_sales,
        "growth": growth,
    }

    return render(request, "dashboard.html", context)
# ---------------------------------------------------------
# SALE + SALE DETAILS
# ---------------------------------------------------------
@transaction.atomic
def create_sale(request):
    """Create a sale and related sale detail items."""
    if request.method == "POST":
        sale_form = SaleForm(request.POST)
        formset = SaleDetailFormSet(request.POST)
        if sale_form.is_valid() and formset.is_valid():
            sale = sale_form.save(commit=False)
            sale.save()
            formset.instance = sale
            formset.save()
            messages.success(request, "Sale recorded successfully.")
            return redirect("sales_list")
    else:
        sale_form = SaleForm()
        formset = SaleDetailFormSet()

    return render(request, "inventory/billing_form.html", {
        "sale_form": sale_form,
        "formset": formset
    })


def sales_list(request):
    """List all recorded sales."""
    sales = Sale.objects.all().order_by("-sale_datetime")
    return render(request, "inventory/sales_list.html", {"sales": sales})


def sale_detail(request, pk):
    """View detailed sale items."""
    sale = get_object_or_404(Sale, pk=pk)
    details = SaleDetail.objects.filter(sale=sale)
    return render(request, "inventory/sale_detail.html", {"sale": sale, "details": details})


# ---------------------------------------------------------
# PRODUCT
# ---------------------------------------------------------
def create_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully.")
            return redirect("product_list")
    else:
        form = ProductForm()
    return render(request, "inventory/product_form.html", {"form": form})


def product_list(request):
    products = Product.objects.all().order_by("product_name")
    return render(request, "inventory/product_list.html", {"products": products})


def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, "inventory/product_form.html", {"form": form})


# ---------------------------------------------------------
# SUPPLIER
# ---------------------------------------------------------
def create_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier added successfully.")
            return redirect("supplier_list")
    else:
        form = SupplierForm()
    return render(request, "inventory/supplier_form.html", {"form": form})


def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "inventory/supplier_list.html", {"suppliers": suppliers})


# ---------------------------------------------------------
# CATEGORY
# ---------------------------------------------------------
def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(request, "inventory/category_form.html", {"form": form})


def category_list(request):
    categories = Category.objects.all()
    return render(request, "inventory/category_list.html", {"categories": categories})


# ---------------------------------------------------------
# CUSTOMER
# ---------------------------------------------------------
def create_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer registered successfully.")
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return render(request, "inventory/customer_form.html", {"form": form})


def customer_list(request):
    customers = Customer.objects.all().order_by("first_name")
    return render(request, "inventory/customer_list.html", {"customers": customers})


def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated successfully.")
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)
    return render(request, "inventory/customer_form.html", {"form": form})


# ---------------------------------------------------------
# STAFF
# ---------------------------------------------------------
def create_staff(request):
    if request.method == "POST":
        form = SaffForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff added successfully.")
            return redirect("staff_list")
    else:
        form = SaffForm()
    return render(request, "inventory/staff_form.html", {"form": form})


def staff_list(request):
    staff = Staff.objects.all()
    return render(request, "inventory/staff_list.html", {"staff": staff})


# ---------------------------------------------------------
# DISCOUNT
# ---------------------------------------------------------
def create_discount(request):
    if request.method == "POST":
        form = DiscountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Discount created successfully.")
            return redirect("discount_list")
    else:
        form = DiscountForm()
    return render(request, "inventory/discount_form.html", {"form": form})


def discount_list(request):
    discounts = Discount.objects.all()
    return render(request, "inventory/discount_list.html", {"discounts": discounts})


# ---------------------------------------------------------
# PURCHASE ORDER
# ---------------------------------------------------------

def create_purchase_order(request):
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Purchase order created.")
            return redirect("purchase_order_list")
    else:
        form = PurchaseOrderForm()
    return render(request, "inventory/purchase_order_form.html", {"form": form})


def purchase_order_list(request):
    orders = PurchaseOrder.objects.all().order_by("-order_date")
    return render(request, "inventory/purchase_order_list.html", {"orders": orders})


# ---------------------------------------------------------
# PURCHASE ORDER DETAIL
# ---------------------------------------------------------
def create_purchase_order_detail(request):
    if request.method == "POST":
        form = PurchaseOrderDetailForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Purchase order detail added.")
            return redirect("purchase_order_detail_list")
    else:
        form = PurchaseOrderDetailForm()
    return render(request, "inventory/purchase_order_detail_form.html", {"form": form})


def purchase_order_detail_list(request):
    details = PurchaseOrderDetail.objects.all()
    return render(request, "inventory/purchase_order_detail_list.html", {"details": details})


# ---------------------------------------------------------
# INVENTORY LOG (Material Arrival)
# ---------------------------------------------------------
def log_inventory(request):
    if request.method == "POST":
        form = InventoryLogForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Inventory log recorded.")
            return redirect("inventory_log_list")
    else:
        form = InventoryLogForm()
    return render(request, "inventory/material_arrival_form.html", {"form": form})


def inventory_log_list(request):
    logs = InventoryLog.objects.all().order_by("-arrival_date")
    return render(request, "inventory/inventory_log_list.html", {"logs": logs})


# ---------------------------------------------------------
# PAYROLL
# ---------------------------------------------------------
def create_payroll(request):
    if request.method == "POST":
        form = PayrollForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Payroll record saved.")
            return redirect("payroll_list")
    else:
        form = PayrollForm()
    return render(request, "inventory/payroll_form.html", {"form": form})


def payroll_list(request):
    payrolls = Payroll.objects.all().order_by("-payment_date")
    return render(request, "inventory/payroll_list.html", {"payrolls": payrolls})




# ---------------------------------------------------------
# 📊 REPORTING & ANALYTICS API VIEWS
# ---------------------------------------------------------

# Helper function to get date filters from request
def get_date_filters(request):
    """
    Extract 'from' and 'to' date parameters from request.
    Returns a dict with 'start' and 'end' datetime objects or None.
    """
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    
    filters = {}
    
    if from_date:
        try:
            # Parse date and set to start of day
            from datetime import datetime
            start = datetime.strptime(from_date, '%Y-%m-%d')
            filters['start'] = timezone.make_aware(start) if timezone.is_naive(start) else start
        except ValueError:
            pass
    
    if to_date:
        try:
            # Parse date and set to end of day
            from datetime import datetime
            end = datetime.strptime(to_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            filters['end'] = timezone.make_aware(end) if timezone.is_naive(end) else end
        except ValueError:
            pass
    
    return filters


def reports_view(request):
    date_filters = get_date_filters(request)
    
    # Base queryset
    sales_qs = Sale.objects.all()
    if 'start' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__lte=date_filters['end'])
    
    total_revenue = sales_qs.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = sales_qs.count()
    avg_order_value = total_revenue / total_orders if total_orders else 0
    
    # SaleDetail queryset with same filters
    sale_details_qs = SaleDetail.objects.filter(sale__in=sales_qs)
    
    top_category = (
        sale_details_qs
        .values('product__category__category_name')
        .annotate(total=Sum(F('unit_price') * F('quantity_sold')))
        .order_by('-total')
        .first()
    )
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'top_category': top_category['product__category__category_name'] if top_category else '-',
    }
    return render(request, 'inventory/reports.html', context)

def sales_by_year_api(request):
    """Return total sales grouped by year."""
    date_filters = get_date_filters(request)
    
    # Base queryset
    sales_qs = Sale.objects.all()
    if 'start' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__lte=date_filters['end'])
    
    data = (
        sales_qs
        .annotate(year=ExtractYear('sale_datetime'))
        .values('year')
        .annotate(total=Sum('total_amount', output_field=FloatField()))
        .order_by('year')
    )
    labels = [d['year'] for d in data]
    values = [float(d['total'] or 0) for d in data]
    return JsonResponse({'labels': labels, 'data': values})


def sales_by_category_api(request):
    """Return total sales grouped by product category."""
    date_filters = get_date_filters(request)
    
    # Base queryset - filter by sale date
    sale_details_qs = SaleDetail.objects.all()
    if 'start' in date_filters:
        sale_details_qs = sale_details_qs.filter(sale__sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sale_details_qs = sale_details_qs.filter(sale__sale_datetime__lte=date_filters['end'])
    
    data = (
        sale_details_qs
        .values('product__category__category_name')
        .annotate(total=Sum(F('unit_price') * F('quantity_sold'), output_field=FloatField()))
        .order_by('product__category__category_name')
    )
    labels = [d['product__category__category_name'] or 'Uncategorized' for d in data]
    values = [float(d['total'] or 0) for d in data]
    return JsonResponse({'labels': labels, 'data': values})


def sales_by_quarter_api(request):
    """Return quarterly sales totals for each year."""
    date_filters = get_date_filters(request)
    
    # Base queryset
    sales_qs = Sale.objects.all()
    if 'start' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__lte=date_filters['end'])
    
    data = (
        sales_qs
        .annotate(year=ExtractYear('sale_datetime'), quarter=ExtractQuarter('sale_datetime'))
        .values('year', 'quarter')
        .annotate(total=Sum('total_amount', output_field=FloatField()))
        .order_by('year', 'quarter')
    )
    labels = [f"Q{d['quarter']} {d['year']}" for d in data]
    values = [float(d['total'] or 0) for d in data]
    return JsonResponse({'labels': labels, 'data': values})


def sales_histogram_api(request):
    """Return histogram-like data for sales frequency distribution."""
    date_filters = get_date_filters(request)
    
    # Base queryset
    sales_qs = Sale.objects.all()
    if 'start' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__lte=date_filters['end'])
    
    buckets = {
        "0–100": sales_qs.filter(total_amount__lt=100).count(),
        "100–500": sales_qs.filter(total_amount__gte=100, total_amount__lt=500).count(),
        "500–1000": sales_qs.filter(total_amount__gte=500, total_amount__lt=1000).count(),
        "1000+": sales_qs.filter(total_amount__gte=1000).count(),
    }
    labels = list(buckets.keys())
    values = list(buckets.values())
    return JsonResponse({'labels': labels, 'data': values})


# --- KPI API: returns totals for dashboard ---
def kpi_data_api(request):
    """
    Returns JSON:
    {
      "total_revenue": float,
      "total_orders": int,
      "avg_order_value": float,
      "top_category": "Category Name" or null,
      "revenue_growth_pct": float (optional, relative to previous period)
    }
    """
    date_filters = get_date_filters(request)
    
    # Base queryset
    sales_qs = Sale.objects.all()
    if 'start' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__lte=date_filters['end'])
    
    # total revenue & orders
    total_revenue = sales_qs.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = sales_qs.count()

    # average order value (safe)
    avg_order_value = float(total_revenue) / total_orders if total_orders else 0.0

    # top category by sales (unit_price * qty) - filter by same date range
    sale_details_qs = SaleDetail.objects.filter(sale__in=sales_qs)
    
    top_cat_q = (
        sale_details_qs
        .values('product__category__category_name')
        .annotate(total=Sum(F('unit_price') * F('quantity_sold'), output_field=FloatField()))
        .order_by('-total')
    ).first()
    top_category = top_cat_q['product__category__category_name'] if top_cat_q else ''

    # optional: simple growth % for last 30 days vs previous 30 days
    # Only calculate if no custom date range is provided
    revenue_growth_pct = None
    if not date_filters:  # Only calculate growth for default view
        try:
            now_time = timezone.now()
            last_30_start = now_time - timedelta(days=30)
            prev_30_start = now_time - timedelta(days=60)
            current_sum = Sale.objects.filter(sale_datetime__gte=last_30_start).aggregate(total=Sum('total_amount'))['total'] or 0
            previous_sum = Sale.objects.filter(sale_datetime__gte=prev_30_start, sale_datetime__lt=last_30_start).aggregate(total=Sum('total_amount'))['total'] or 0
            if previous_sum and previous_sum != 0:
                revenue_growth_pct = float((current_sum - previous_sum) / previous_sum * 100)
        except Exception:
            revenue_growth_pct = None

    payload = {
        'total_revenue': float(total_revenue),
        'total_orders': int(total_orders),
        'avg_order_value': float(avg_order_value),
        'top_category': top_category or '',
        'revenue_growth_pct': revenue_growth_pct,
    }
    return JsonResponse(payload)


# --- Sales table API: returns recent sale lines for the detailed table ---
def sales_table_data_api(request):
    """
    Returns a JSON array of recent sale lines:
    [
      {"date":"YYYY-MM-DD", "product":"Name", "category":"Cat", "quantity":int, 
       "unit_price":float, "total":float, "customer":"Name"},
      ...
    ]
    """
    date_filters = get_date_filters(request)
    
    # Base queryset
    qs = SaleDetail.objects.select_related('sale', 'product', 'product__category', 'sale__customer')
    
    if 'start' in date_filters:
        qs = qs.filter(sale__sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        qs = qs.filter(sale__sale_datetime__lte=date_filters['end'])
    
    qs = qs.order_by('-sale__sale_datetime')[:200]

    rows = []
    for sd in qs:
        sale = sd.sale
        product = sd.product
        # customer display: prefer name, fallback to phone/email
        customer_name = ''
        if getattr(sale, 'customer', None):
            c = sale.customer
            # assemble sensible name
            if hasattr(c, 'first_name') and c.first_name:
                customer_name = f"{(c.first_name or '')} {(c.last_name or '')}".strip()
            else:
                customer_name = getattr(c, 'phone', '') or getattr(c, 'email', '') or ''
        rows.append({
            'date': sale.sale_datetime.strftime('%Y-%m-%d'),
            'product': product.product_name if product else '',
            'category': getattr(product.category, 'category_name', '') if getattr(product, 'category', None) else '',
            'quantity': int(sd.quantity_sold or 0),
            'unit_price': float(sd.unit_price or 0),
            'total': float(sd.sub_total or (sd.unit_price * sd.quantity_sold) or 0),
            'customer': customer_name,
        })

    return JsonResponse(rows, safe=False)