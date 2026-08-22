from django.contrib import admin
from .models import Category, Supplier, Medicine, Purchase, Sale, StockTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'category', 'supplier', 'quantity', 'minimum_stock', 'purchase_price', 'selling_price', 'expiry_date')
    list_filter = ('category', 'supplier', 'expiry_date')
    search_fields = ('name', 'generic_name', 'batch_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'medicine', 'supplier', 'quantity', 'purchase_price', 'total_amount', 'purchase_date')
    list_filter = ('supplier', 'purchase_date')
    search_fields = ('medicine__name', 'batch_number')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'medicine', 'quantity', 'selling_price', 'total_amount', 'sale_date')
    list_filter = ('sale_date',)
    search_fields = ('medicine__name',)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'transaction_type', 'quantity', 'reference_id', 'transaction_date')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('medicine__name', 'reference_id')
