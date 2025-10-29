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
    path('sales/<int:pk>/items/', views.sale_items_api, name='sale_items_api'),
    path('sales/export/', views.export_sales, name='export_sales'),
    path('receipt/<str:receipt_no>/', views.print_receipt, name='print_receipt'),

    # Products
    path('products/new/', views.create_product, name='create_product'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),

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
    path('staff/info/<int:pk>/', views.staff_info_api, name='staff_info_api'),


    # Discounts
    path('discounts/new/', views.create_discount, name='create_discount'),
    path('discounts/', views.discount_list, name='discount_list'),
    path('discounts/edit/<int:pk>/', views.edit_discount, name='edit_discount'),
    path('discounts/delete/<int:pk>/', views.delete_discount, name='delete_discount'),
    path('discounts/toggle/<int:pk>/', views.toggle_discount_status, name='toggle_discount_status'),
    path('discounts/details/<int:pk>/', views.discount_details_api, name='discount_details_api'),
    path('discounts/export/', views.export_discounts, name='export_discounts'),

    # Purchase Orders
    path('purchase-orders/new/', views.create_purchase_order, name='create_purchase_order'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),

    # Purchase Order Details
    path('purchase-details/new/', views.create_purchase_order_detail, name='create_purchase_order_detail'),
    path('purchase-details/', views.purchase_order_detail_list, name='purchase_order_detail_list'),

    # Inventory Logs (Material Arrivals)
    path('inventory-log/new/', views.log_inventory, name='log_inventory'),
    path('inventory-log/', views.inventory_log_list, name='inventory_log_list'),
    
    # Inventory Management
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/api/products/', views.inventory_products_api, name='inventory_products_api'),
    path('inventory/api/transactions/', views.inventory_transactions_api, name='inventory_transactions_api'),
    path('inventory/adjust-stock/', views.adjust_stock, name='adjust_stock'),
    path('inventory/product-details/<int:pk>/', views.product_details_api, name='product_details_api'),
    path('inventory/export/', views.export_inventory, name='export_inventory'),

    # Payroll
    path('payroll/new/', views.create_payroll, name='create_payroll'),
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/edit/<int:pk>/', views.edit_payroll, name='edit_payroll'),
    path('payroll/delete/<int:pk>/', views.delete_payroll, name='delete_payroll'),
    path('payroll/details/<int:pk>/', views.payroll_details_api, name='payroll_details_api'),
    path('payroll/export/', views.export_payroll, name='export_payroll'),

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

    #Finacial reports
    path('api/reports/financial/', views.financial_report_api, name='financial_report_api'),

# Remove or update the old export endpoints to match the new function names:
path('reports/export/pdf/', views.export_report_pdf, name='export_reports_pdf'),
path('reports/export/csv/', views.export_report_csv, name='export_reports_csv'),
path('reports/export/excel/', views.export_report_excel, name='export_reports_excel'),
]