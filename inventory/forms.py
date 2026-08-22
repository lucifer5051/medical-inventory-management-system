from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Category, Supplier, Medicine, Purchase, Sale


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Painkiller, Antibiotic'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description of this category'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company or Business Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primary Contact Person'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@supplier.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Office/Warehouse Address'}),
        }


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'generic_name', 'category', 'supplier',
            'batch_number', 'quantity', 'minimum_stock', 'storage_location',
            'purchase_price', 'selling_price',
            'manufacturing_date', 'expiry_date',
            'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Paracetamol 500mg'}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Acetaminophen'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BATCH-2026-001'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'storage_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Shelf A-3, Rack 2'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'manufacturing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional information or dosage warnings'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        mfg_date = cleaned_data.get('manufacturing_date')
        exp_date = cleaned_data.get('expiry_date')
        cost_price = cleaned_data.get('purchase_price')
        sell_price = cleaned_data.get('selling_price')
        qty = cleaned_data.get('quantity')
        min_stock = cleaned_data.get('minimum_stock')

        if mfg_date and exp_date and mfg_date > exp_date:
            self.add_error('manufacturing_date', 'Manufacturing date cannot be after expiry date.')
            self.add_error('expiry_date', 'Expiry date cannot be before manufacturing date.')

        if cost_price is not None and cost_price < 0:
            self.add_error('purchase_price', 'Purchase price cannot be negative.')

        if sell_price is not None and sell_price < 0:
            self.add_error('selling_price', 'Selling price cannot be negative.')

        if cost_price is not None and sell_price is not None and sell_price < cost_price:
            self.add_error('selling_price', 'Selling price should not be lower than purchase price.')

        if qty is not None and qty < 0:
            self.add_error('quantity', 'Quantity cannot be negative.')

        if min_stock is not None and min_stock < 0:
            self.add_error('minimum_stock', 'Minimum stock cannot be negative.')

        return cleaned_data


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['medicine', 'supplier', 'quantity', 'purchase_price', 'batch_number', 'purchase_date', 'expiry_date']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-select', 'id': 'id_purchase_medicine'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'id_purchase_qty'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_purchase_price'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BATCH-2026-002'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('purchase_date'):
            self.initial['purchase_date'] = timezone.now().date()

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty <= 0:
            raise ValidationError('Purchase quantity must be greater than zero.')
        return qty

    def clean_purchase_price(self):
        price = self.cleaned_data.get('purchase_price')
        if price is None or price < 0:
            raise ValidationError('Purchase price cannot be negative.')
        return price


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['medicine', 'quantity', 'selling_price', 'sale_date']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-select', 'id': 'id_sale_medicine'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'id': 'id_sale_qty'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_sale_price'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('sale_date'):
            self.initial['sale_date'] = timezone.now().date()

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty <= 0:
            raise ValidationError('Sale quantity must be greater than zero.')
        return qty

    def clean(self):
        cleaned_data = super().clean()
        medicine = cleaned_data.get('medicine')
        requested_qty = cleaned_data.get('quantity')

        if medicine and requested_qty:
            if requested_qty > medicine.quantity:
                raise ValidationError({
                    'quantity': f'Insufficient stock available. Current stock: {medicine.quantity}, Requested quantity: {requested_qty}'
                })

        return cleaned_data
