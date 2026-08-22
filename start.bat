@echo off
TITLE Medical Inventory Management System - Auto Launcher
COLOR 0A
CLS

echo =======================================================================
echo          MEDICAL INVENTORY MANAGEMENT SYSTEM (Django + MySQL)
echo =======================================================================
echo.

:: Check Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to PATH!
    echo Please install Python 3.10 or higher and try again.
    pause
    exit /b
)

echo -----------------------------------------------------------------------
echo [1/4] Checking & Installing Python Dependencies...
echo -----------------------------------------------------------------------
pip install -r requirements.txt

echo.
echo -----------------------------------------------------------------------
echo [2/4] Checking Environment Configuration (.env)...
echo -----------------------------------------------------------------------
if not exist .env (
    echo Creating default .env file from .env.example...
    copy .env.example .env
)

echo.
echo -----------------------------------------------------------------------
echo [3/4] Applying MySQL Database Migrations...
echo -----------------------------------------------------------------------
python manage.py makemigrations
python manage.py migrate

echo.
echo -----------------------------------------------------------------------
echo [4/4] Seeding Database Records (Categories, Suppliers, Medicines)...
echo -----------------------------------------------------------------------
python manage.py seed_data

echo.
echo =======================================================================
echo SUCCESS: System Ready! Opening browser and starting server...
echo =======================================================================
echo.
start http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000
