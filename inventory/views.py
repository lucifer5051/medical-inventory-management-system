import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, F, Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone

from .models import Category, Supplier, Medicine, Purchase, Sale, StockTransaction
from .forms import CategoryForm, SupplierForm, MedicineForm, PurchaseForm, SaleForm


# ==========================================
# AUTHENTICATION VIEWS
# ==========================================

def user_login_view(request):
    """User login view using Django authentication."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'inventory/login.html', {'form': form})


@login_required
def user_logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')


# ==========================================
# DASHBOARD VIEW
# ==========================================

@login_required
def dashboard_view(request):
    """
    Main Analytics Dashboard.
    Calculates real-time statistics strictly from the MySQL database.
    """
    today = timezone.now().date()
    thirty_days_later = today + datetime.timedelta(days=30)

    # Summary Cards
    total_medicines = Medicine.objects.count()
    total_stock_aggregate = Medicine.objects.aggregate(total=Sum('quantity'))['total'] or 0

    low_stock_medicines = Medicine.objects.filter(quantity__gt=0, quantity__lte=F('minimum_stock'))
    low_stock_count = low_stock_medicines.count()

    out_of_stock_count = Medicine.objects.filter(quantity=0).count()

    expired_medicines = Medicine.objects.filter(expiry_date__lt=today)
    expired_count = expired_medicines.count()

    expiring_soon_medicines = Medicine.objects.filter(expiry_date__gte=today, expiry_date__lte=thirty_days_later)
    expiring_soon_count = expiring_soon_medicines.count()

    safe_count = Medicine.objects.filter(expiry_date__gt=thirty_days_later).count()

    total_stock_value = Medicine.objects.aggregate(
        val=Sum(F('quantity') * F('purchase_price'))
    )['val'] or Decimal('0.00')

    # Category breakdown query
    category_data = Category.objects.annotate(
        stock=Sum('medicines__quantity')
    ).values('name', 'stock')

    category_list = []
    max_cat_stock = 1
    for cat in category_data:
        c_stock = cat['stock'] or 0
        if c_stock > max_cat_stock:
            max_cat_stock = c_stock

    for cat in category_data:
        c_stock = cat['stock'] or 0
        pct = int((c_stock / max_cat_stock) * 100) if max_cat_stock > 0 else 0
        category_list.append({
            'name': cat['name'],
            'stock': c_stock,
            'percentage': pct
        })

    # Search & Recent Table on Dashboard
    search_query = request.GET.get('q', '').strip()
    medicines_qs = Medicine.objects.select_related('category', 'supplier').all()

    if search_query:
        medicines_qs = medicines_qs.filter(
            Q(name__icontains=search_query) |
            Q(generic_name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(batch_number__icontains=search_query)
        )

    recent_medicines = medicines_qs[:10]

    context = {
        'today': today,
        'total_medicines': total_medicines,
        'total_stock': total_stock_aggregate,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'expired_count': expired_count,
        'expiring_soon_count': expiring_soon_count,
        'safe_count': safe_count,
        'total_stock_value': total_stock_value,
        'category_list': category_list,
        'recent_medicines': recent_medicines,
        'search_query': search_query,
    }
    return render(request, 'inventory/dashboard.html', context)


# ==========================================
# MEDICINE CRUD VIEWS
# ==========================================

@login_required
def medicine_list_view(request):
    """View & Filter all medicines in inventory."""
    today = timezone.now().date()
    thirty_days_later = today + datetime.timedelta(days=30)

    medicines = Medicine.objects.select_related('category', 'supplier').all()

    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        medicines = medicines.filter(
            Q(name__icontains=search_query) |
            Q(generic_name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(batch_number__icontains=search_query)
        )

    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        medicines = medicines.filter(category_id=category_id)

    # Supplier filter
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        medicines = medicines.filter(supplier_id=supplier_id)

    # Stock Status filter
    stock_filter = request.GET.get('stock')
    if stock_filter == 'out':
        medicines = medicines.filter(quantity=0)
    elif stock_filter == 'low':
        medicines = medicines.filter(quantity__gt=0, quantity__lte=F('minimum_stock'))
    elif stock_filter == 'in':
        medicines = medicines.filter(quantity__gt=F('minimum_stock'))

    # Expiry Status filter
    expiry_filter = request.GET.get('expiry')
    if expiry_filter == 'expired':
        medicines = medicines.filter(expiry_date__lt=today)
    elif expiry_filter == 'expiring_soon':
        medicines = medicines.filter(expiry_date__gte=today, expiry_date__lte=thirty_days_later)
    elif expiry_filter == 'safe':
        medicines = medicines.filter(expiry_date__gt=thirty_days_later)

    paginator = Paginator(medicines, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'suppliers': suppliers,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_supplier': supplier_id,
        'selected_stock': stock_filter,
        'selected_expiry': expiry_filter,
    }
    return render(request, 'inventory/medicines.html', context)


@login_required
def medicine_detail_view(request, pk):
    """Detailed view of a medicine with its transaction history."""
    medicine = get_object_or_404(Medicine.objects.select_related('category', 'supplier'), pk=pk)
    transactions = medicine.stock_transactions.all()[:20]

    context = {
        'medicine': medicine,
        'transactions': transactions,
    }
    return render(request, 'inventory/medicine_detail.html', context)


@login_required
def medicine_add_view(request):
    """Add a new medicine record."""
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save()
            messages.success(request, f"Medicine '{medicine.name}' added successfully!")
            return redirect('medicine_detail', pk=medicine.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = MedicineForm()

    return render(request, 'inventory/medicine_form.html', {'form': form, 'title': 'Add New Medicine'})


@login_required
def medicine_edit_view(request, pk):
    """Edit an existing medicine record."""
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, f"Medicine '{medicine.name}' updated successfully!")
            return redirect('medicine_detail', pk=medicine.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = MedicineForm(instance=medicine)

    return render(request, 'inventory/medicine_form.html', {'form': form, 'medicine': medicine, 'title': f'Edit {medicine.name}'})


@login_required
def medicine_delete_view(request, pk):
    """
    Delete medicine. Prevents deletion if medicine has transaction history.
    """
    medicine = get_object_or_404(Medicine, pk=pk)

    if not medicine.can_be_deleted():
        messages.warning(request, f"Cannot delete '{medicine.name}' because purchase/sale transaction history exists. Inventory integrity must be preserved.")
        return redirect('medicine_detail', pk=medicine.pk)

    if request.method == 'POST':
        med_name = medicine.name
        medicine.delete()
        messages.success(request, f"Medicine '{med_name}' deleted successfully.")
        return redirect('medicine_list')

    return render(request, 'inventory/medicine_confirm_delete.html', {'medicine': medicine})


# ==========================================
# CATEGORY CRUD VIEWS
# ==========================================

@login_required
def category_list_view(request):
    """List & add categories."""
    categories = Category.objects.annotate(medicine_count=Count('medicines')).all()
    return render(request, 'inventory/categories.html', {'categories': categories})


@login_required
def category_add_view(request):
    """Add a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' created successfully!")
            return redirect('category_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm()

    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_edit_view(request, pk):
    """Edit an existing category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated successfully!")
            return redirect('category_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm(instance=category)

    return render(request, 'inventory/category_form.html', {'form': form, 'category': category, 'title': f'Edit Category: {category.name}'})


@login_required
def category_delete_view(request, pk):
    """Delete category if no medicines belong to it."""
    category = get_object_or_404(Category, pk=pk)
    if category.medicines.exists():
        messages.warning(request, f"Cannot delete category '{category.name}' because medicines belong to it. Please reassign or delete the medicines first.")
        return redirect('category_list')

    if request.method == 'POST':
        cat_name = category.name
        category.delete()
        messages.success(request, f"Category '{cat_name}' deleted successfully.")
        return redirect('category_list')

    return render(request, 'inventory/category_confirm_delete.html', {'category': category})


# ==========================================
# SUPPLIER CRUD VIEWS
# ==========================================

@login_required
def supplier_list_view(request):
    """List all suppliers."""
    suppliers = Supplier.objects.annotate(medicine_count=Count('medicines')).all()
    return render(request, 'inventory/suppliers.html', {'suppliers': suppliers})


@login_required
def supplier_detail_view(request, pk):
    """Detailed view of a supplier with associated medicines and purchases."""
    supplier = get_object_or_404(Supplier, pk=pk)
    medicines = supplier.medicines.all()
    purchases = supplier.purchases.select_related('medicine').all()[:20]

    context = {
        'supplier': supplier,
        'medicines': medicines,
        'purchases': purchases,
    }
    return render(request, 'inventory/supplier_detail.html', context)


@login_required
def supplier_add_view(request):
    """Add a new supplier."""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f"Supplier '{supplier.name}' added successfully!")
            return redirect('supplier_detail', pk=supplier.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SupplierForm()

    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'Add New Supplier'})


@login_required
def supplier_edit_view(request, pk):
    """Edit supplier details."""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Supplier '{supplier.name}' updated successfully!")
            return redirect('supplier_detail', pk=supplier.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'inventory/supplier_form.html', {'form': form, 'supplier': supplier, 'title': f'Edit Supplier: {supplier.name}'})


@login_required
def supplier_delete_view(request, pk):
    """Delete supplier if no medicines or purchases are linked."""
    supplier = get_object_or_404(Supplier, pk=pk)
    if supplier.medicines.exists() or supplier.purchases.exists():
        messages.warning(request, f"Cannot delete supplier '{supplier.name}' because medicines or purchase records are associated with it.")
        return redirect('supplier_detail', pk=supplier.pk)

    if request.method == 'POST':
        sup_name = supplier.name
        supplier.delete()
        messages.success(request, f"Supplier '{sup_name}' deleted successfully.")
        return redirect('supplier_list')

    return render(request, 'inventory/supplier_confirm_delete.html', {'supplier': supplier})


# ==========================================
# PURCHASE MANAGEMENT VIEWS
# ==========================================

@login_required
def purchase_list_view(request):
    """List purchase history."""
    purchases = Purchase.objects.select_related('medicine', 'supplier').all()
    
    paginator = Paginator(purchases, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory/purchases.html', {'page_obj': page_obj})


@login_required
def purchase_add_view(request):
    """
    Record a new purchase.
    Atomic Stock Increase Logic:
    1. Save Purchase.
    2. Increase Medicine stock quantity.
    3. Create StockTransaction record (+ quantity).
    """
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                purchase = form.save()

                # 2. Increase stock
                medicine = purchase.medicine
                medicine.quantity += purchase.quantity
                medicine.save()

                # 3. Record stock transaction
                StockTransaction.objects.create(
                    medicine=medicine,
                    transaction_type='PURCHASE',
                    quantity=purchase.quantity,
                    reference_id=f"PUR-{purchase.id}",
                    notes=f"Purchased {purchase.quantity} units from {purchase.supplier.name}. Batch: {purchase.batch_number}"
                )

            messages.success(request, f"Purchase of {purchase.quantity} units of '{medicine.name}' recorded. Stock increased to {medicine.quantity}.")
            return redirect('purchase_list')
        else:
            messages.error(request, "Please correct the errors in the purchase form.")
    else:
        form = PurchaseForm()

    return render(request, 'inventory/purchase_form.html', {'form': form})


# ==========================================
# SALES MANAGEMENT VIEWS
# ==========================================

@login_required
def sale_list_view(request):
    """List sales history."""
    sales = Sale.objects.select_related('medicine').all()
    
    paginator = Paginator(sales, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory/sales.html', {'page_obj': page_obj})


@login_required
def sale_add_view(request):
    """
    Record a new sale.
    Atomic Stock Decrease Logic:
    1. Verify stock availability (handled in SaleForm.clean()).
    2. Save Sale.
    3. Decrease Medicine stock quantity.
    4. Create StockTransaction record (- quantity).
    """
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                sale = form.save()

                # 3. Decrease stock
                medicine = sale.medicine
                medicine.quantity -= sale.quantity
                medicine.save()

                # 4. Record stock transaction
                StockTransaction.objects.create(
                    medicine=medicine,
                    transaction_type='SALE',
                    quantity=-sale.quantity,
                    reference_id=f"SALE-{sale.id}",
                    notes=f"Sold {sale.quantity} units at ₹{sale.selling_price}/unit."
                )

            messages.success(request, f"Sale of {sale.quantity} units of '{medicine.name}' recorded. New stock: {medicine.quantity}.")
            return redirect('sale_list')
        else:
            messages.error(request, "Sale rejected. Please review stock availability or form errors.")
    else:
        form = SaleForm()

    return render(request, 'inventory/sale_form.html', {'form': form})


# ==========================================
# STOCK TRANSACTIONS HISTORY VIEW
# ==========================================

@login_required
def transaction_list_view(request):
    """View stock movement log."""
    transactions = StockTransaction.objects.select_related('medicine').all()

    tx_type = request.GET.get('type')
    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)

    search_query = request.GET.get('q', '').strip()
    if search_query:
        transactions = transactions.filter(
            Q(medicine__name__icontains=search_query) |
            Q(reference_id__icontains=search_query)
        )

    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory/transactions.html', {
        'page_obj': page_obj,
        'selected_type': tx_type,
        'search_query': search_query,
    })


# ==========================================
# REPORTS VIEWS
# ==========================================

@login_required
def report_inventory_view(request):
    """Full Inventory Valuation and Status Report."""
    medicines = Medicine.objects.select_related('category', 'supplier').all()
    
    total_val = sum([m.total_stock_value for m in medicines])
    total_qty = sum([m.quantity for m in medicines])

    return render(request, 'inventory/reports/inventory.html', {
        'medicines': medicines,
        'total_val': total_val,
        'total_qty': total_qty,
    })


@login_required
def report_expiry_view(request):
    """Expiry Analysis Report (Expired, Expiring Soon, Safe)."""
    today = timezone.now().date()
    thirty_days_later = today + datetime.timedelta(days=30)

    expired = Medicine.objects.select_related('category').filter(expiry_date__lt=today)
    expiring_soon = Medicine.objects.select_related('category').filter(expiry_date__gte=today, expiry_date__lte=thirty_days_later)
    safe = Medicine.objects.select_related('category').filter(expiry_date__gt=thirty_days_later)

    return render(request, 'inventory/reports/expiry.html', {
        'expired': expired,
        'expiring_soon': expiring_soon,
        'safe': safe,
        'today': today,
    })


@login_required
def report_low_stock_view(request):
    """Low Stock & Out of Stock Report."""
    low_stock = Medicine.objects.select_related('category', 'supplier').filter(quantity__gt=0, quantity__lte=F('minimum_stock'))
    out_of_stock = Medicine.objects.select_related('category', 'supplier').filter(quantity=0)

    return render(request, 'inventory/reports/low_stock.html', {
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    })


@login_required
def report_purchases_view(request):
    """Purchase History Report."""
    purchases = Purchase.objects.select_related('medicine', 'supplier').all()
    
    total_spent = purchases.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_units = purchases.aggregate(total=Sum('quantity'))['total'] or 0

    return render(request, 'inventory/reports/purchases.html', {
        'purchases': purchases,
        'total_spent': total_spent,
        'total_units': total_units,
    })


@login_required
def report_sales_view(request):
    """Sales Revenue Report."""
    sales = Sale.objects.select_related('medicine').all()
    
    total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_units = sales.aggregate(total=Sum('quantity'))['total'] or 0

    return render(request, 'inventory/reports/sales.html', {
        'sales': sales,
        'total_revenue': total_revenue,
        'total_units': total_units,
    })


# ==========================================
# API HELPER FOR JS FORMS
# ==========================================

@login_required
def api_medicine_detail(request, pk):
    """Returns medicine JSON details for dynamic frontend form fill."""
    medicine = get_object_or_404(Medicine, pk=pk)
    return JsonResponse({
        'id': medicine.id,
        'name': medicine.name,
        'batch_number': medicine.batch_number,
        'purchase_price': str(medicine.purchase_price),
        'selling_price': str(medicine.selling_price),
        'quantity': medicine.quantity,
        'supplier_id': medicine.supplier_id,
        'expiry_date': medicine.expiry_date.strftime('%Y-%m-%d') if medicine.expiry_date else '',
    })
