import datetime
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Category name (must be unique)")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Category name cannot be empty.'})


class Supplier(models.Model):
    name = models.CharField(max_length=150, help_text="Supplier business name")
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, help_text="Contact phone number")
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Medicine(models.Model):
    name = models.CharField(max_length=150, help_text="Medicine commercial name")
    generic_name = models.CharField(max_length=150, blank=True, null=True, help_text="Generic formula/active ingredient")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='medicines')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='medicines')
    batch_number = models.CharField(max_length=50, help_text="Manufacturer batch number")
    quantity = models.PositiveIntegerField(default=0, help_text="Current available stock quantity")
    minimum_stock = models.PositiveIntegerField(default=10, help_text="Stock alert threshold")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost price per unit")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price per unit")
    manufacturing_date = models.DateField()
    expiry_date = models.DateField()
    storage_location = models.CharField(max_length=100, blank=True, null=True, help_text="Shelf/Rack location")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Batch: {self.batch_number})"

    def clean(self):
        # Validate dates
        if self.manufacturing_date and self.expiry_date:
            if self.manufacturing_date > self.expiry_date:
                raise ValidationError({
                    'manufacturing_date': 'Manufacturing date cannot be after expiry date.'
                })
        
        # Validate prices
        if self.purchase_price is not None and self.selling_price is not None:
            if self.selling_price < self.purchase_price:
                raise ValidationError({
                    'selling_price': 'Selling price should not be lower than purchase price.'
                })

    @property
    def stock_status(self):
        """
        Dynamically calculates stock status:
        - OUT OF STOCK if quantity == 0
        - LOW STOCK if quantity <= minimum_stock
        - IN STOCK otherwise
        """
        if self.quantity == 0:
            return 'OUT OF STOCK'
        elif self.quantity <= self.minimum_stock:
            return 'LOW STOCK'
        return 'IN STOCK'

    @property
    def expiry_status(self):
        """
        Dynamically calculates expiry status based on current date:
        - EXPIRED if expiry_date < today
        - EXPIRING SOON if today <= expiry_date <= today + 30 days
        - SAFE otherwise
        """
        today = timezone.now().date()
        if self.expiry_date < today:
            return 'EXPIRED'
        elif today <= self.expiry_date <= today + datetime.timedelta(days=30):
            return 'EXPIRING SOON'
        return 'SAFE'

    @property
    def total_stock_value(self):
        """Calculates total monetary value of current stock based on purchase price."""
        return Decimal(self.quantity) * self.purchase_price

    def can_be_deleted(self):
        """Checks if medicine has transaction history."""
        has_purchases = self.purchases.exists()
        has_sales = self.sales.exists()
        has_transactions = self.stock_transactions.exists()
        return not (has_purchases or has_sales or has_transactions)


class Purchase(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='purchases')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.PositiveIntegerField(help_text="Quantity purchased")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unit purchase price")
    batch_number = models.CharField(max_length=50)
    purchase_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchase_date', '-created_at']

    def __str__(self):
        return f"Purchase #{self.id} - {self.medicine.name} ({self.quantity} units)"

    def save(self, *args, **kwargs):
        self.total_amount = Decimal(self.quantity) * Decimal(str(self.purchase_price))
        super().save(*args, **kwargs)


class Sale(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField(help_text="Quantity sold")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unit selling price")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    sale_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sale_date', '-created_at']

    def __str__(self):
        return f"Sale #{self.id} - {self.medicine.name} ({self.quantity} units)"

    def save(self, *args, **kwargs):
        self.total_amount = Decimal(self.quantity) * Decimal(str(self.selling_price))
        super().save(*args, **kwargs)


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('ADJUSTMENT', 'Adjustment'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField(help_text="Positive for additions (+), negative for sales/reductions (-)")
    reference_id = models.CharField(max_length=100, blank=True, null=True, help_text="Related Purchase/Sale ID")
    transaction_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        qty_str = f"+{self.quantity}" if self.quantity > 0 else str(self.quantity)
        return f"{self.medicine.name} | {self.transaction_type} | {qty_str}"
