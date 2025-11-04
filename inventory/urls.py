from django.urls import path
from . import views

urlpatterns = [
    # Home / Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
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
    path('suppliers/<int:pk>/edit/', views.edit_supplier, name='edit_supplier'),

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
    path('staff/<int:pk>/info/', views.staff_info_api, name='staff_info_api'),

    # Discounts
    path('discounts/new/', views.create_discount, name='create_discount'),
    path('discounts/', views.discount_list, name='discount_list'),
    path('discounts/<int:pk>/edit/', views.edit_discount, name='edit_discount'),
    path('discounts/<int:pk>/delete/', views.delete_discount, name='delete_discount'),
    path('discounts/<int:pk>/toggle/', views.toggle_discount_status, name='toggle_discount_status'),
    path('discounts/<int:pk>/details/', views.discount_details_api, name='discount_details_api'),
    path('discounts/export/', views.export_discounts, name='export_discounts'),

    # Purchase Orders
    path('purchase-orders/new/', views.create_purchase_order, name='create_purchase_order'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),

    # Purchase Order Details
    path('purchase-order-details/new/', views.create_purchase_order_detail, name='create_purchase_order_detail'),
    path('purchase-order-details/', views.purchase_order_detail_list, name='purchase_order_detail_list'),

    # Inventory Management
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/log/new/', views.log_inventory, name='log_inventory'),
    path('inventory/logs/', views.inventory_log_list, name='inventory_log_list'),
    path('inventory/api/products/', views.inventory_products_api, name='inventory_products_api'),
    path('inventory/api/transactions/', views.inventory_transactions_api, name='inventory_transactions_api'),
    path('inventory/adjust-stock/', views.adjust_stock, name='adjust_stock'),
    path('inventory/products/<int:pk>/details/', views.product_details_api, name='product_details_api'),
    path('inventory/export/', views.export_inventory, name='export_inventory'),

    # Payroll
    path('payroll/new/', views.create_payroll, name='create_payroll'),
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/<int:pk>/edit/', views.edit_payroll, name='edit_payroll'),
    path('payroll/<int:pk>/delete/', views.delete_payroll, name='delete_payroll'),
    path('payroll/<int:pk>/details/', views.payroll_details_api, name='payroll_details_api'),
    path('payroll/export/', views.export_payroll, name='export_payroll'),

    # Reports & Analytics
    path('reports/', views.reports_view, name='reports'),
    
    # API Endpoints for Charts and Data
    
    path('api/sales/by-category/', views.sales_by_category_api, name='sales_by_category_api'),
    
    path('api/quarterly-sales/', views.quarterly_sales_api, name='quarterly_sales_api'),
    path('api/yearly-sales/', views.yearly_sales_api, name='yearly_sales_api'),
    path('api/monthly-sales/', views.monthly_sales_api, name='monthly_sales_api'),
    path('api/sales/histogram/', views.sales_histogram_api, name='sales_histogram_api'),
    path('api/sales/table-data/', views.sales_table_data_api, name='sales_table_data_api'),
    path('api/kpi-data/', views.kpi_data_api, name='kpi_data_api'),
    path('api/reports/financial/', views.financial_report_api, name='financial_report_api'),
    path('api/reports/expiry/', views.expiry_reports_api, name='expiry_reports_api'),
    path('api/reports/taxes/', views.taxes_report_api, name='taxes_report_api'),
    
    # Export Endpoints
    path('export/report/', views.export_report, name='export_report'),
    path('export/table/', views.export_table, name='export_table'),
    path('export/report/pdf/', views.export_report_pdf, name='export_report_pdf'),
    path('export/report/csv/', views.export_report_csv, name='export_report_csv'),
    path('export/report/excel/', views.export_report_excel, name='export_report_excel'),
    path('export/table/pdf/', views.export_table_pdf, name='export_table_pdf'),
    path('export/table/csv/', views.export_table_csv, name='export_table_csv'),
    path('export/table/excel/', views.export_table_excel, name='export_table_excel'),

    # Expiry Management
    path('expiry/preview/', views.expiry_preview, name='expiry_preview'),
    path('expiry/writeoff/', views.execute_expiry_writeoff, name='execute_expiry_writeoff'),
]