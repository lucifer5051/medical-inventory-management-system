import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from inventory.models import Category, Supplier, Medicine, Purchase, Sale, StockTransaction


class Command(BaseCommand):
    help = 'Seeds initial sample data (Categories, Suppliers, Medicines, Purchases, Sales) into MySQL'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # 1. Create Superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created with password 'admin123'."))

        # 2. Categories
        categories_data = [
            {'name': 'Painkiller', 'description': 'Analgesics and pain relief medicines'},
            {'name': 'Antibiotic', 'description': 'Bacterial infection treatments'},
            {'name': 'Antihistamine', 'description': 'Allergy and cold relief'},
            {'name': 'Rehydration', 'description': 'Electrolytes and hydration solutions'},
            {'name': 'Cold & Cough', 'description': 'Cough syrups and decongestants'},
            {'name': 'Antacid', 'description': 'Acidity and heartburn relief'},
            {'name': 'Vitamins', 'description': 'Dietary supplements and minerals'},
            {'name': 'Diabetes', 'description': 'Blood sugar control medications'},
            {'name': 'Blood Pressure', 'description': 'Hypertension and cardiac care'},
            {'name': 'First Aid', 'description': 'Antiseptics, bandages, and ointments'},
        ]

        categories = {}
        for item in categories_data:
            cat, created = Category.objects.get_or_create(name=item['name'], defaults={'description': item['description']})
            categories[item['name']] = cat

        self.stdout.write(self.style.SUCCESS(f"{len(categories)} categories created/verified."))

        # 3. Suppliers
        suppliers_data = [
            {
                'name': 'Sun Pharma Distributors',
                'contact_person': 'Rakesh Sharma',
                'phone': '9876543210',
                'email': 'sales@sunpharma-dist.com',
                'address': 'Plot 12, Industrial Area, Mumbai'
            },
            {
                'name': 'Cipla Healthcare India',
                'contact_person': 'Anish Gupta',
                'phone': '9812345678',
                'email': 'orders@cipla-health.com',
                'address': 'Sector 4, Rohini, New Delhi'
            },
            {
                'name': 'Dr. Reddy\'s Laboratories',
                'contact_person': 'Priya Reddy',
                'phone': '9765432109',
                'email': 'supply@drreddys.com',
                'address': 'Banjara Hills, Hyderabad'
            },
            {
                'name': 'Mankind Pharma Logistics',
                'contact_person': 'Vikram Singh',
                'phone': '9988776655',
                'email': 'logistics@mankind.com',
                'address': 'DLF Cyber City, Gurgaon'
            },
        ]

        suppliers = {}
        for item in suppliers_data:
            sup, created = Supplier.objects.get_or_create(
                name=item['name'],
                defaults={
                    'contact_person': item['contact_person'],
                    'phone': item['phone'],
                    'email': item['email'],
                    'address': item['address'],
                }
            )
            suppliers[item['name']] = sup

        self.stdout.write(self.style.SUCCESS(f"{len(suppliers)} suppliers created/verified."))

        # 4. Medicines covering IN STOCK, LOW STOCK, OUT OF STOCK, EXPIRED, EXPIRING SOON
        today = timezone.now().date()

        medicines_data = [
            {
                'name': 'Paracetamol 500mg',
                'generic_name': 'Acetaminophen',
                'category': categories['Painkiller'],
                'supplier': suppliers['Sun Pharma Distributors'],
                'batch_number': 'BATCH-PARA-2026-A',
                'quantity': 150,
                'minimum_stock': 20,
                'purchase_price': Decimal('10.00'),
                'selling_price': Decimal('15.00'),
                'manufacturing_date': today - datetime.timedelta(days=180),
                'expiry_date': today + datetime.timedelta(days=365),
                'storage_location': 'Rack A-1',
                'description': 'Used for fever and mild to moderate pain relief.'
            },
            {
                'name': 'Amoxicillin 250mg',
                'generic_name': 'Amoxicillin Trihydrate',
                'category': categories['Antibiotic'],
                'supplier': suppliers['Cipla Healthcare India'],
                'batch_number': 'BATCH-AMOX-2026-B',
                'quantity': 8,  # LOW STOCK
                'minimum_stock': 15,
                'purchase_price': Decimal('45.00'),
                'selling_price': Decimal('65.00'),
                'manufacturing_date': today - datetime.timedelta(days=120),
                'expiry_date': today + datetime.timedelta(days=300),
                'storage_location': 'Rack B-2',
                'description': 'Broad spectrum antibiotic capsule.'
            },
            {
                'name': 'Cetirizine 10mg',
                'generic_name': 'Cetirizine Hydrochloride',
                'category': categories['Antihistamine'],
                'supplier': suppliers['Dr. Reddy\'s Laboratories'],
                'batch_number': 'BATCH-CET-2026-C',
                'quantity': 0,  # OUT OF STOCK
                'minimum_stock': 10,
                'purchase_price': Decimal('5.00'),
                'selling_price': Decimal('8.50'),
                'manufacturing_date': today - datetime.timedelta(days=200),
                'expiry_date': today + datetime.timedelta(days=250),
                'storage_location': 'Rack C-1',
                'description': 'Antihistamine tablet for allergy, sneezing and cold.'
            },
            {
                'name': 'ORS Sachet 21.8g',
                'generic_name': 'Oral Rehydration Salts',
                'category': categories['Rehydration'],
                'supplier': suppliers['Mankind Pharma Logistics'],
                'batch_number': 'BATCH-ORS-2026-D',
                'quantity': 350,
                'minimum_stock': 50,
                'purchase_price': Decimal('12.00'),
                'selling_price': Decimal('18.00'),
                'manufacturing_date': today - datetime.timedelta(days=90),
                'expiry_date': today + datetime.timedelta(days=20),  # EXPIRING SOON
                'storage_location': 'Shelf D-4',
                'description': 'WHO formula electrolyte powder for dehydration.'
            },
            {
                'name': 'Cough Syrup 100ml',
                'generic_name': 'Dextromethorphan + Chlorpheniramine',
                'category': categories['Cold & Cough'],
                'supplier': suppliers['Sun Pharma Distributors'],
                'batch_number': 'BATCH-COUGH-2024-E',
                'quantity': 15,
                'minimum_stock': 10,
                'purchase_price': Decimal('75.00'),
                'selling_price': Decimal('110.00'),
                'manufacturing_date': today - datetime.timedelta(days=730),
                'expiry_date': today - datetime.timedelta(days=15),  # EXPIRED
                'storage_location': 'Rack E-2 (Quarantine)',
                'description': 'Relieves dry cough and throat irritation.'
            },
            {
                'name': 'Metformin 500mg',
                'generic_name': 'Metformin Hydrochloride',
                'category': categories['Diabetes'],
                'supplier': suppliers['Cipla Healthcare India'],
                'batch_number': 'BATCH-MET-2026-F',
                'quantity': 5,  # LOW STOCK & EXPIRING SOON
                'minimum_stock': 20,
                'purchase_price': Decimal('22.00'),
                'selling_price': Decimal('32.00'),
                'manufacturing_date': today - datetime.timedelta(days=150),
                'expiry_date': today + datetime.timedelta(days=15),  # EXPIRING SOON
                'storage_location': 'Rack F-1',
                'description': 'Antidiabetic medication for Type 2 diabetes.'
            },
            {
                'name': 'Multivitamin Capsules',
                'generic_name': 'Multivitamin & Zinc Formula',
                'category': categories['Vitamins'],
                'supplier': suppliers['Dr. Reddy\'s Laboratories'],
                'batch_number': 'BATCH-MULTI-2026-G',
                'quantity': 200,
                'minimum_stock': 30,
                'purchase_price': Decimal('120.00'),
                'selling_price': Decimal('180.00'),
                'manufacturing_date': today - datetime.timedelta(days=60),
                'expiry_date': today + datetime.timedelta(days=500),
                'storage_location': 'Rack G-3',
                'description': 'Daily health and immunity booster capsule.'
            },
        ]

        medicines = {}
        for m_data in medicines_data:
            med, created = Medicine.objects.get_or_create(
                name=m_data['name'],
                batch_number=m_data['batch_number'],
                defaults=m_data
            )
            medicines[med.name] = med

        self.stdout.write(self.style.SUCCESS(f"{len(medicines)} medicines created/verified."))

        # 5. Create Sample Purchase history and Stock Transactions
        if not Purchase.objects.exists():
            p1 = Purchase.objects.create(
                medicine=medicines['Paracetamol 500mg'],
                supplier=suppliers['Sun Pharma Distributors'],
                quantity=200,
                purchase_price=Decimal('10.00'),
                batch_number='BATCH-PARA-2026-A',
                purchase_date=today - datetime.timedelta(days=30),
                expiry_date=today + datetime.timedelta(days=365),
            )
            StockTransaction.objects.create(
                medicine=medicines['Paracetamol 500mg'],
                transaction_type='PURCHASE',
                quantity=200,
                reference_id=f"PUR-{p1.id}",
                transaction_date=timezone.now() - datetime.timedelta(days=30),
                notes="Initial bulk stock purchase."
            )

            p2 = Purchase.objects.create(
                medicine=medicines['Multivitamin Capsules'],
                supplier=suppliers['Dr. Reddy\'s Laboratories'],
                quantity=250,
                purchase_price=Decimal('120.00'),
                batch_number='BATCH-MULTI-2026-G',
                purchase_date=today - datetime.timedelta(days=15),
                expiry_date=today + datetime.timedelta(days=500),
            )
            StockTransaction.objects.create(
                medicine=medicines['Multivitamin Capsules'],
                transaction_type='PURCHASE',
                quantity=250,
                reference_id=f"PUR-{p2.id}",
                transaction_date=timezone.now() - datetime.timedelta(days=15),
                notes="Quarterly vitamin stock refresh."
            )

            self.stdout.write(self.style.SUCCESS("Sample Purchase history generated."))

        # 6. Create Sample Sales history and Stock Transactions
        if not Sale.objects.exists():
            s1 = Sale.objects.create(
                medicine=medicines['Paracetamol 500mg'],
                quantity=50,
                selling_price=Decimal('15.00'),
                sale_date=today - datetime.timedelta(days=10),
            )
            StockTransaction.objects.create(
                medicine=medicines['Paracetamol 500mg'],
                transaction_type='SALE',
                quantity=-50,
                reference_id=f"SALE-{s1.id}",
                transaction_date=timezone.now() - datetime.timedelta(days=10),
                notes="Counter prescription sale."
            )

            s2 = Sale.objects.create(
                medicine=medicines['Multivitamin Capsules'],
                quantity=50,
                selling_price=Decimal('180.00'),
                sale_date=today - datetime.timedelta(days=5),
            )
            StockTransaction.objects.create(
                medicine=medicines['Multivitamin Capsules'],
                transaction_type='SALE',
                quantity=-50,
                reference_id=f"SALE-{s2.id}",
                transaction_date=timezone.now() - datetime.timedelta(days=5),
                notes="Retail OTC sale."
            )

            self.stdout.write(self.style.SUCCESS("Sample Sales history generated."))

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully! You can log in with username 'admin' and password 'admin123'."))
