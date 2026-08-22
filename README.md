# Medical Inventory Management System 🏥💊

A full-stack, database-driven web application built with **Python 3, Django, MySQL, HTML5, CSS3, JavaScript, and Bootstrap 5** for managing pharmacy and medical store inventory.

---

## 🌟 Key Features

- **Authentication System**: Built-in Django authentication with login/logout and session protection.
- **Analytics Dashboard**: Real-time summary metrics calculated dynamically from MySQL:
  - Total Medicines count
  - Total Available Stock
  - Low Stock Alerts
  - Expired Medicines
  - Expiring Soon (Within 30 Days)
  - Total Stock Valuation in Indian Currency (`₹`)
- **Stock Control & Relational Integrity**:
  - **Category & Supplier Management**: Reusable foreign key relationships.
  - **Atomic Purchases**: Automatically increases stock levels and records audit transactions.
  - **Atomic Sales**: Validates stock availability server-side; rejects sales if `requested > available` stock.
  - **Deletion Rules**: Prevents deletion of medicines with transaction history.
- **Reports**:
  - Inventory Valuation Report
  - Expiry Risk Analysis Report
  - Low Stock & Reorder Report
  - Purchase History Summary Report
  - Sales Revenue Summary Report
- **Seed Data Management**: Built-in `seed_data` command to populate realistic sample medicines, categories, suppliers, purchases, and sales.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Django
- **Database**: MySQL (Django ORM)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- MySQL Server (e.g. MySQL 8.0)

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/lucifer5051/medical-inventory-management-system.git
cd medical-inventory-management-system

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration
Copy `.env.example` to `.env` and set your MySQL credentials:
```ini
DB_ENGINE=django.db.backends.mysql
DB_NAME=medical_inventory
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### 4. Run Migrations & Seed Data
```bash
# Apply migrations to MySQL
python manage.py makemigrations
python manage.py migrate

# Populate sample data (creates demo superuser: admin / admin123)
python manage.py seed_data
```

### 5. Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🔑 Demo Account Credentials
- **Username**: `admin`
- **Password**: `admin123`

---

## 📁 Repository Structure

```text
medical_inventory/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── medical_inventory/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── inventory/
    ├── admin.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    ├── management/commands/seed_data.py
    ├── templatetags/currency_tags.py
    ├── templates/inventory/
    └── static/inventory/
```
