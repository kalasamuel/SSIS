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

from .utils import generate_purchase_order_pdf


from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, F, FloatField
from django.db.models.functions import ExtractYear, ExtractQuarter, ExtractMonth


from django.utils import timezone
from datetime import timedelta


from datetime import timedelta, date, datetime
from django.utils.timezone import now
from django.core.mail import EmailMessage
from django.conf import settings

# Import for exports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import csv
import io

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

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
    total_suppliers = Supplier.objects.count()
    return render(request, "inventory/home.html", {
        "total_sales": total_sales,
        "total_products": total_products,
        "total_customers": total_customers,
        "total_staff": total_staff,
        "total_suppliers": total_suppliers,
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

def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier updated successfully.")
            return redirect("supplier_list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "inventory/supplier_form.html", {"form": form})

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
    suppliers = Supplier.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        expected_date = request.POST.get("expected_delivery_date")
        invoice_no = request.POST.get("invoice_no")

        # Create the main order
        order = PurchaseOrder.objects.create(
            supplier_id=supplier_id,
            expected_delivery_date=expected_date,
            invoice_no=invoice_no
        )

        # Add product line items
        product_ids = request.POST.getlist("product[]")
        quantities = request.POST.getlist("quantity[]")
        unit_costs = request.POST.getlist("unit_cost[]")

        for i in range(len(product_ids)):
            if product_ids[i] and quantities[i] and unit_costs[i]:
                PurchaseOrderDetail.objects.create(
                    purchase_order=order,
                    product_id=product_ids[i],
                    quantity=quantities[i],
                    unit_cost=unit_costs[i],
                )

        #  Generate PDF
        pdf_data = generate_purchase_order_pdf(order)

        #  Build and send email
        subject = f"Purchase Order #{order.id} from {request.user.username}"
        body = (
            f"Dear {order.supplier.supplier_name},\n\n"
            f"Please find attached our new purchase order.\n\n"
            f"Thank you,\n{request.user.username}\n{request.user.email}"
        )

        email = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [order.supplier.contact_email],
        )
        email.attach(f"PurchaseOrder_{order.id}.pdf", pdf_data, "application/pdf")
        email.send(fail_silently=False)

        messages.success(request, "Purchase order created and sent to supplier.")
        return redirect("purchase_order_list")

    return render(request, "inventory/create_purchase_order.html", {
        "suppliers": suppliers,
        "products": products,
    })


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


# ---------------------------------------------------------
# 📄 EXPORT VIEWS
# ---------------------------------------------------------

# Add these export functions to your views.py

def export_report(request):
    """Export full report (KPIs + Sales details) in selected format"""
    export_format = request.GET.get('format', 'pdf')
    
    if export_format == 'pdf':
        return export_report_pdf(request)
    elif export_format == 'csv':
        return export_report_csv(request)
    elif export_format == 'excel':
        return export_report_excel(request)
    else:
        return HttpResponse("Invalid export format", status=400)

def export_table(request):
    """Export only sales table in selected format"""
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'pdf':
        return export_table_pdf(request)
    elif export_format == 'csv':
        return export_table_csv(request)
    elif export_format == 'excel':
        return export_table_excel(request)
    else:
        return HttpResponse("Invalid export format", status=400)

def export_report_pdf(request):
    """Export KPI + Sales details report as PDF."""
    date_filters = get_date_filters(request)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    elements.append(Paragraph("Sales Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Date range
    if date_filters:
        date_info = f"Period: {date_filters.get('start', 'All')} to {date_filters.get('end', 'Now')}"
        elements.append(Paragraph(date_info, styles['Normal']))
        elements.append(Spacer(1, 12))
    
    # KPIs
    sales_qs = Sale.objects.all()
    if 'start' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__lte=date_filters['end'])
    total_revenue = sales_qs.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = sales_qs.count()
    avg_order_value = total_revenue / total_orders if total_orders else 0
    
    kpi_data = [['Metric', 'Value'],
                ['Total Revenue', f'UGx. {total_revenue:,.0f}'],
                ['Total Orders', f'{total_orders:,}'],
                ['Average Order Value', f'UGx. {avg_order_value:,.0f}']]
    kpi_table = Table(kpi_data, colWidths=[3*inch, 3*inch])
    kpi_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                                   ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                                   ('ALIGN',(0,0),(-1,-1),'CENTER'),
                                   ('GRID',(0,0),(-1,-1),1,colors.black)]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 20))
    
    # Sales details
    elements.append(Paragraph("Sales Details", styles['Heading2']))
    elements.append(Spacer(1, 12))
    sale_details_qs = SaleDetail.objects.select_related('sale','product','product__category')
    if 'start' in date_filters:
        sale_details_qs = sale_details_qs.filter(sale__sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sale_details_qs = sale_details_qs.filter(sale__sale_datetime__lte=date_filters['end'])
    
    table_data = [['Date','Product','Category','Qty','Price','Total']]
    for sd in sale_details_qs.order_by('-sale__sale_datetime')[:50]:
        table_data.append([
            sd.sale.sale_datetime.strftime('%Y-%m-%d'),
            sd.product.product_name if sd.product else '',
            getattr(sd.product.category, 'category_name', '') if getattr(sd.product, 'category', None) else '',
            str(sd.quantity_sold or 0),
            f'UGx. {sd.unit_price or 0:,.0f}',
            f'UGx. {(sd.unit_price * sd.quantity_sold) or 0:,.0f}'
        ])
    sales_table = Table(table_data, colWidths=[1*inch, 1.5*inch, 1.2*inch, 0.6*inch, 1*inch, 1.2*inch])
    sales_table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),
                                     ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                                     ('ALIGN',(0,0),(-1,-1),'CENTER'),
                                     ('GRID',(0,0),(-1,-1),0.5,colors.black)]))
    elements.append(sales_table)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def export_report_csv(request):
    """Export full report as CSV"""
    date_filters = get_date_filters(request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Report header
    writer.writerow(['SALES REPORT'])
    if date_filters:
        date_info = f"Period: {date_filters.get('start', 'All')} to {date_filters.get('end', 'Now')}"
        writer.writerow([date_info])
    writer.writerow([])
    
    # KPIs section
    writer.writerow(['KPI SUMMARY'])
    sales_qs = Sale.objects.all()
    if 'start' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__lte=date_filters['end'])
    
    total_revenue = sales_qs.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = sales_qs.count()
    avg_order_value = total_revenue / total_orders if total_orders else 0
    
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Revenue', f'UGx. {total_revenue:,.0f}'])
    writer.writerow(['Total Orders', total_orders])
    writer.writerow(['Average Order Value', f'UGx. {avg_order_value:,.0f}'])
    writer.writerow([])
    
    # Sales details section
    writer.writerow(['SALES DETAILS'])
    writer.writerow(['Date','Product','Category','Qty','Price','Total','Customer'])
    
    qs = SaleDetail.objects.select_related('sale','product','product__category','sale__customer')
    if 'start' in date_filters:
        qs = qs.filter(sale__sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        qs = qs.filter(sale__sale_datetime__lte=date_filters['end'])
    
    for sd in qs.order_by('-sale__sale_datetime'):
        customer_name = ''
        if sd.sale.customer:
            c = sd.sale.customer
            customer_name = f"{getattr(c,'first_name','')} {getattr(c,'last_name','')}".strip() or getattr(c,'phone','') or getattr(c,'email','')
        writer.writerow([
            sd.sale.sale_datetime.strftime('%Y-%m-%d'),
            sd.product.product_name if sd.product else '',
            getattr(sd.product.category,'category_name','') if getattr(sd.product,'category',None) else '',
            sd.quantity_sold or 0,
            sd.unit_price or 0,
            (sd.unit_price * sd.quantity_sold) or 0,
            customer_name
        ])
    return response

def export_report_excel(request):
    """Export full report as Excel"""
    if not EXCEL_AVAILABLE:
        return HttpResponse("Excel export requires openpyxl. Please install it: pip install openpyxl", status=500)
    
    date_filters = get_date_filters(request)
    
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Report"
    
    # Styling
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=12)
    title_font = Font(bold=True, size=16)
    
    # Title
    ws['A1'] = "SALES REPORT"
    ws['A1'].font = title_font
    ws.merge_cells('A1:G1')
    
    # Date range
    row = 2
    if date_filters:
        date_range = f"Period: {date_filters.get('start', 'All')} to {date_filters.get('end', 'Now')}"
        ws[f'A{row}'] = date_range
        ws.merge_cells(f'A{row}:G{row}')
        row += 1
    
    row += 1
    
    # KPI Summary
    sales_qs = Sale.objects.all()
    if 'start' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        sales_qs = sales_qs.filter(sale_datetime__lte=date_filters['end'])
    
    total_revenue = sales_qs.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = sales_qs.count()
    avg_order_value = total_revenue / total_orders if total_orders else 0
    
    # KPI Header
    ws[f'A{row}'] = "KPI SUMMARY"
    ws[f'A{row}'].font = Font(bold=True, size=14)
    row += 1
    
    # KPI Table Headers
    ws[f'A{row}'] = "Metric"
    ws[f'B{row}'] = "Value"
    ws[f'A{row}'].fill = header_fill
    ws[f'B{row}'].fill = header_fill
    ws[f'A{row}'].font = header_font
    ws[f'B{row}'].font = header_font
    row += 1
    
    # KPI Data
    kpi_data = [
        ['Total Revenue', f'UGx. {total_revenue:,.0f}'],
        ['Total Orders', total_orders],
        ['Average Order Value', f'UGx. {avg_order_value:,.0f}'],
    ]
    
    for kpi_row in kpi_data:
        ws[f'A{row}'] = kpi_row[0]
        ws[f'B{row}'] = kpi_row[1]
        row += 1
    
    row += 2
    
    # Sales Details
    ws[f'A{row}'] = "SALES DETAILS"
    ws[f'A{row}'].font = Font(bold=True, size=14)
    row += 1
    
    # Headers
    headers = ['Date', 'Product', 'Category', 'Quantity', 'Unit Price', 'Total', 'Customer']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    row += 1
    
    # Get sales data
    qs = SaleDetail.objects.select_related('sale','product','product__category','sale__customer')
    if 'start' in date_filters:
        qs = qs.filter(sale__sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        qs = qs.filter(sale__sale_datetime__lte=date_filters['end'])
    
    for sd in qs.order_by('-sale__sale_datetime'):
        customer_name = ''
        if sd.sale.customer:
            c = sd.sale.customer
            customer_name = f"{getattr(c,'first_name','')} {getattr(c,'last_name','')}".strip() or getattr(c,'phone','') or getattr(c,'email','')
        
        ws[f'A{row}'] = sd.sale.sale_datetime.strftime('%Y-%m-%d')
        ws[f'B{row}'] = sd.product.product_name if sd.product else ''
        ws[f'C{row}'] = getattr(sd.product.category,'category_name','') if getattr(sd.product,'category',None) else ''
        ws[f'D{row}'] = sd.quantity_sold or 0
        ws[f'E{row}'] = sd.unit_price or 0
        ws[f'F{row}'] = (sd.unit_price * sd.quantity_sold) or 0
        ws[f'G{row}'] = customer_name
        row += 1
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 20
    
    # Save to response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    wb.save(response)
    
    return response

def export_table_pdf(request):
    """Export only sales table as PDF"""
    date_filters = get_date_filters(request)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_table_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    elements.append(Paragraph("Sales Table", title_style))
    elements.append(Spacer(1, 12))
    
    # Date range
    if date_filters:
        date_info = f"Period: {date_filters.get('start', 'All')} to {date_filters.get('end', 'Now')}"
        elements.append(Paragraph(date_info, styles['Normal']))
        elements.append(Spacer(1, 12))
    
    # Sales table only
    table_data = [['Date','Product','Category','Qty','Price','Total','Customer']]
    
    qs = SaleDetail.objects.select_related('sale','product','product__category','sale__customer')
    if 'start' in date_filters:
        qs = qs.filter(sale__sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        qs = qs.filter(sale__sale_datetime__lte=date_filters['end'])
    
    for sd in qs.order_by('-sale__sale_datetime')[:100]:  # Limit for PDF
        customer_name = ''
        if sd.sale.customer:
            c = sd.sale.customer
            customer_name = f"{getattr(c,'first_name','')} {getattr(c,'last_name','')}".strip() or getattr(c,'phone','') or getattr(c,'email','')
        
        table_data.append([
            sd.sale.sale_datetime.strftime('%Y-%m-%d'),
            sd.product.product_name if sd.product else '',
            getattr(sd.product.category, 'category_name', '') if getattr(sd.product, 'category', None) else '',
            str(sd.quantity_sold or 0),
            f'UGx. {sd.unit_price or 0:,.0f}',
            f'UGx. {(sd.unit_price * sd.quantity_sold) or 0:,.0f}',
            customer_name
        ])
    
    sales_table = Table(table_data, colWidths=[1*inch, 1.5*inch, 1.2*inch, 0.6*inch, 1*inch, 1.2*inch, 1.5*inch])
    sales_table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.grey),
                                     ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                                     ('ALIGN',(0,0),(-1,-1),'CENTER'),
                                     ('GRID',(0,0),(-1,-1),0.5,colors.black)]))
    elements.append(sales_table)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def export_table_csv(request):
    """Export detailed sales table as CSV"""
    date_filters = get_date_filters(request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_table_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date','Product','Category','Qty','Price','Total','Customer'])
    
    qs = SaleDetail.objects.select_related('sale','product','product__category','sale__customer')
    if 'start' in date_filters:
        qs = qs.filter(sale__sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        qs = qs.filter(sale__sale_datetime__lte=date_filters['end'])
    
    for sd in qs.order_by('-sale__sale_datetime'):
        customer_name = ''
        if sd.sale.customer:
            c = sd.sale.customer
            customer_name = f"{getattr(c,'first_name','')} {getattr(c,'last_name','')}".strip() or getattr(c,'phone','') or getattr(c,'email','')
        writer.writerow([
            sd.sale.sale_datetime.strftime('%Y-%m-%d'),
            sd.product.product_name if sd.product else '',
            getattr(sd.product.category,'category_name','') if getattr(sd.product,'category',None) else '',
            sd.quantity_sold or 0,
            sd.unit_price or 0,
            (sd.unit_price * sd.quantity_sold) or 0,
            customer_name
        ])
    return response

def export_table_excel(request):
    """Export sales table as Excel"""
    if not EXCEL_AVAILABLE:
        return HttpResponse("Excel export requires openpyxl. Please install it: pip install openpyxl", status=500)
    
    date_filters = get_date_filters(request)
    
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Table"
    
    # Styling
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=12)
    title_font = Font(bold=True, size=16)
    
    # Title
    ws['A1'] = "SALES TABLE"
    ws['A1'].font = title_font
    ws.merge_cells('A1:G1')
    
    # Date range
    row = 2
    if date_filters:
        date_range = f"Period: {date_filters.get('start', 'All')} to {date_filters.get('end', 'Now')}"
        ws[f'A{row}'] = date_range
        ws.merge_cells(f'A{row}:G{row}')
        row += 1
    
    row += 1
    
    # Headers
    headers = ['Date', 'Product', 'Category', 'Quantity', 'Unit Price', 'Total', 'Customer']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    row += 1
    
    # Get sales data
    qs = SaleDetail.objects.select_related('sale','product','product__category','sale__customer')
    if 'start' in date_filters:
        qs = qs.filter(sale__sale_datetime__gte=date_filters['start'])
    if 'end' in date_filters:
        qs = qs.filter(sale__sale_datetime__lte=date_filters['end'])
    
    for sd in qs.order_by('-sale__sale_datetime'):
        customer_name = ''
        if sd.sale.customer:
            c = sd.sale.customer
            customer_name = f"{getattr(c,'first_name','')} {getattr(c,'last_name','')}".strip() or getattr(c,'phone','') or getattr(c,'email','')
        
        ws[f'A{row}'] = sd.sale.sale_datetime.strftime('%Y-%m-%d')
        ws[f'B{row}'] = sd.product.product_name if sd.product else ''
        ws[f'C{row}'] = getattr(sd.product.category,'category_name','') if getattr(sd.product,'category',None) else ''
        ws[f'D{row}'] = sd.quantity_sold or 0
        ws[f'E{row}'] = sd.unit_price or 0
        ws[f'F{row}'] = (sd.unit_price * sd.quantity_sold) or 0
        ws[f'G{row}'] = customer_name
        row += 1
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 20
    
    # Save to response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="sales_table_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    wb.save(response)
    
    return response