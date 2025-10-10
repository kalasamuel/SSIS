from django.shortcuts import render, redirect
from django.db import transaction
from .forms import SaleForm, SaleDetailFormSet
from .models import Product, Sale, SaleDetail
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import ExtractYear

def home(request):
    return render(request, 'inventory/home.html')   

def create_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        formset = SaleDetailFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                sale = form.save(commit=False)
                sale.total_amount = 0
                sale.save()
                total = 0
                for detail_form in formset:
                    if detail_form.cleaned_data and not detail_form.cleaned_data.get('DELETE', False):
                        detail = detail_form.save(commit=False)
                        detail.sale = sale
                        # compute sub_total = qty * unit_price - discount_value (if any)
                        qty = detail.quantity_sold
                        unit = detail.unit_price
                        dval = detail.discount_value or 0
                        detail.sub_total = (qty * unit) - dval
                        detail.save()
                        # reduce product stock
                        prod = Product.objects.get(pk=detail.product.pk)
                        prod.stock_quantity = prod.stock_quantity - detail.quantity_sold
                        prod.save()
                        total += float(detail.sub_total)
                sale.total_amount = total
                sale.save()
            return redirect('sale_detail', pk=sale.pk)
    else:
        form = SaleForm()
        formset = SaleDetailFormSet()
    return render(request, 'inventory/create_sale.html', {'form': form, 'formset': formset})


#Graphical Reports

def sales_by_year_api(request):
    qs = (Sale.objects
          .annotate(year=ExtractYear('sale_datetime'))
          .values('year')
          .annotate(total=Sum('total_amount'))
          .order_by('year'))
    labels = [r['year'] for r in qs]
    data = [float(r['total'] or 0) for r in qs]
    return JsonResponse({'labels': labels, 'data': data})

def sales_by_category_api(request):
    qs = (SaleDetail.objects
          .values('product__category__category_name')
          .annotate(total=Sum('sub_total'))
          .order_by('-total'))
    labels = [r['product__category__category_name'] for r in qs]
    data = [float(r['total'] or 0) for r in qs]
    return JsonResponse({'labels': labels, 'data': data})


def create_sale(request):
    # (your existing sale form logic)
    return render(request, 'inventory/create_sale.html', {})  # simplified if just testing template

def reports_view(request):
    return render(request, 'inventory/reports.html')