from django.urls import path
from . import views

urlpatterns = [
    # Home / Dashboard
    path('', views.home, name='home'),
    path('authentication/', views.authentication, name='authentication'),

    # Sales
    path('sales/new/', views.create_sale, name='create_sale'),
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),

    # Products
    path('products/new/', views.create_product, name='create_product'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/edit/', views.edit_product, name='edit_product'),

    # Suppliers
    path('suppliers/new/', views.create_supplier, name='create_supplier'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/edit/<int:pk>/', views.edit_supplier, name='edit_supplier'),

    # Categories
    path('categories/new/', views.create_category, name='create_category'),
    path('categories/', views.category_list, name='category_list'),

    # Customers
    path('customers/new/', views.create_customer, name='create_customer'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/edit/', views.edit_customer, name='edit_customer'),


    # Staff
    path('staff/new/', views.create_staff, name='create_staff'),
    path('staff/', views.staff_list, name='staff_list'),


    # Discounts
    path('discounts/new/', views.create_discount, name='create_discount'),
    path('discounts/', views.discount_list, name='discount_list'),

    # Purchase Orders
    path('purchase-orders/new/', views.create_purchase_order, name='create_purchase_order'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),

    # Purchase Order Details
    path('purchase-details/new/', views.create_purchase_order_detail, name='create_purchase_order_detail'),
    path('purchase-details/', views.purchase_order_detail_list, name='purchase_order_detail_list'),

    # Inventory Logs (Material Arrivals)
    path('inventory-log/new/', views.log_inventory, name='log_inventory'),
    path('inventory-log/', views.inventory_log_list, name='inventory_log_list'),

    # Payroll
    path('payroll/new/', views.create_payroll, name='create_payroll'),
    path('payroll/', views.payroll_list, name='payroll_list'),

    # Reports
    path('reports/', views.reports_view, name='reports'),

    # Charts
    path('api/sales_by_year/', views.sales_by_year_api, name='sales_by_year_api'),
    path('api/sales_by_category/', views.sales_by_category_api, name='sales_by_category_api'),
    #extended analytics
    path('api/sales_by_quarter/', views.sales_by_quarter_api, name='sales_by_quarter_api'),
    path('api/sales_histogram/', views.sales_histogram_api, name='sales_histogram_api'),

    path('api/sales_table_data/', views.sales_table_data_api, name='sales_table_data_api'),

    path('api/kpi_data/', views.kpi_data_api, name='kpi_data_api'),

    # Export Data - NEW UNIFIED EXPORT ENDPOINTS
    path('export/report/', views.export_report, name='export_report'),
    path('export/table/', views.export_table, name='export_table'),

    # Expiry Management
    path('expiry/confirm/', views.expiry_preview, name='expiry_preview'),
    path('expiry/writeoff/', views.execute_expiry_writeoff, name='execute_expiry_writeoff'),
    path('api/reports/expiry/', views.expiry_reports_api, name='expiry_reports_api'),
]