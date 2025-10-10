from django.urls import path
from . import views

urlpatterns = [
    path('sales/new/', views.create_sale, name='create_sale'),
    path('reports/', views.reports_view, name='reports'),
    path('', views.home, name='home'),
    path('api/sales_by_year/', views.sales_by_year_api, name='sales_by_year_api'),
    path('api/sales_by_category/', views.sales_by_category_api, name='sales_by_category_api'),
]
