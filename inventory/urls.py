from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Auth
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),

    # Medicines
    path('medicines/', views.medicine_list_view, name='medicine_list'),
    path('medicines/add/', views.medicine_add_view, name='medicine_add'),
    path('medicines/<int:pk>/', views.medicine_detail_view, name='medicine_detail'),
    path('medicines/<int:pk>/edit/', views.medicine_edit_view, name='medicine_edit'),
    path('medicines/<int:pk>/delete/', views.medicine_delete_view, name='medicine_delete'),

    # Categories
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/add/', views.category_add_view, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),

    # Suppliers
    path('suppliers/', views.supplier_list_view, name='supplier_list'),
    path('suppliers/add/', views.supplier_add_view, name='supplier_add'),
    path('suppliers/<int:pk>/', views.supplier_detail_view, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit_view, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete_view, name='supplier_delete'),

    # Purchases
    path('purchases/', views.purchase_list_view, name='purchase_list'),
    path('purchases/add/', views.purchase_add_view, name='purchase_add'),

    # Sales
    path('sales/', views.sale_list_view, name='sale_list'),
    path('sales/add/', views.sale_add_view, name='sale_add'),

    # Transactions History
    path('transactions/', views.transaction_list_view, name='transaction_list'),

    # Reports
    path('reports/inventory/', views.report_inventory_view, name='report_inventory'),
    path('reports/expiry/', views.report_expiry_view, name='report_expiry'),
    path('reports/low-stock/', views.report_low_stock_view, name='report_low_stock'),
    path('reports/purchases/', views.report_purchases_view, name='report_purchases'),
    path('reports/sales/', views.report_sales_view, name='report_sales'),

    # API JSON Endpoint for JS form fill
    path('api/medicines/<int:pk>/', views.api_medicine_detail, name='api_medicine_detail'),
]
