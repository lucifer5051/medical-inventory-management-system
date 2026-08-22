# Medical Inventory Management System 🏥💊

A full-stack, database-driven web application built with **Python 3, Django, MySQL, HTML5, CSS3, JavaScript, and Bootstrap 5** for managing pharmacy and medical store inventory.

---

## ⚡ Quick One-Click Automatic Launch (Windows)

Double-click `start.bat` or run in command prompt:
```cmd
start.bat
```
`start.bat` automatically:
1. Installs required Python packages (`pip install -r requirements.txt`).
2. Configures environment `.env`.
3. Applies database schema migrations to MySQL.
4. Seeds categories, suppliers, medicines, purchases, and sales into MySQL.
5. Launches your web browser to `http://127.0.0.1:8000/` and starts the Django server.

---

## 🏛️ Database Architecture & Authenticity

This application uses **MySQL as its true persistent relational database**.

```text
Django Models
      ↓
Django Migrations
      ↓
MySQL Database Tables
      ↓
Django ORM (Object-Relational Mapper)
      ↓
Dashboard & Dynamic HTML Tables
```

### Why is there no static `.sql` dump file in the repository?
- The database schema is defined and managed centrally using **Django Models** (`inventory/models.py`).
- Database tables in MySQL are generated dynamically using **Django Migrations** (`python manage.py migrate`).
- Demonstration data is populated into MySQL using the custom Django management command `python manage.py seed_data`.
- All analytics metrics, alerts, tables, stock updates, purchases, and sales operate on **live MySQL queries** using the Django ORM.

---

## 🌟 Key Features

- **Authentication System**: Built-in Django authentication with login/logout and session protection.
- **Analytics Dashboard**: Real-time summary metrics calculated dynamically from MySQL:
  - Total Medicines count
  - Total Available Stock
  - Low Stock Alerts
  - Out of Stock Items
  - Expired Medicines
  - Expiring Soon (Within 30 Days)
  - Total Stock Valuation in Indian Currency (`₹`)
- **Operational Alerts Panel**: Instant visual alerts for critical out-of-stock, expired, and expiring items.
- **Recent Activity Log**: Real-time audit trail of the latest 10 inventory transactions.
- **Stock Control & Relational Integrity**:
  - **Category & Supplier Management**: Reusable foreign key relationships across 14 categories and 10 suppliers.
  - **Atomic Purchases**: Automatically increases stock levels and records `PURCHASE` audit transactions.
  - **Atomic Sales**: Validates stock availability server-side; rejects sales if `requested > available` stock.
  - **Deletion Protection**: Prevents deletion of medicines with transaction history.
- **Reports**:
  - Inventory Valuation Report
  - Expiry Risk Analysis Report
  - Low Stock & Reorder Report
  - Purchase History Summary Report
  - Sales Revenue Summary Report
  - Stock Movement Audit Log
- **Seed Data System**: Built-in `seed_data` command creating 14 categories, 10 suppliers, 25 medicines, 25+ purchases, 45+ sales, and 70+ stock transactions with 100% mathematical consistency.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Django 6
- **Database**: MySQL Server (`medical_inventory`) via `django.db.backends.mysql`
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons

---

## 🚀 Manual Command Line Execution

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/lucifer5051/medical-inventory-management-system.git
cd medical-inventory-management-system

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration
Copy `.env.example` to `.env` and set your MySQL credentials:
```ini
DB_ENGINE=django.db.backends.mysql
DB_NAME=medical_inventory
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### 3. Run Migrations & Seed Data
```bash
# Apply migrations to MySQL
python manage.py makemigrations
python manage.py migrate

# Populate sample data into MySQL
python manage.py seed_data
```

### 4. Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 📁 Repository Structure

```text
medical_inventory/
├── start.bat
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
