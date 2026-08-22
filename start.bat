@echo off
TITLE Medical Inventory Management System - Launcher
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

echo Select launch mode:
echo.
echo   [1] Full Automatic Setup & Start Server (Recommended)
echo   [2] Apply Database Migrations Only
echo   [3] Seed / Reset Demonstration Data Only
echo   [4] Start Development Server Only
echo   [5] Exit
echo.
set /p choice="Enter option [1-5]: "

if "%choice%"=="1" goto AUTO_SETUP
if "%choice%"=="2" goto MIGRATE_ONLY
if "%choice%"=="3" goto SEED_ONLY
if "%choice%"=="4" goto START_SERVER
if "%choice%"=="5" goto END

echo Invalid choice. Running Automatic Setup by default...
echo.

:AUTO_SETUP
echo.
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
echo [4/4] Seeding Demo Data (Categories, Suppliers, Medicines)...
echo -----------------------------------------------------------------------
python manage.py seed_data

echo.
echo =======================================================================
echo SUCCESS: System Ready! Opening browser and starting server...
echo Demo Login: Username: admin | Password: admin123
echo =======================================================================
echo.
start http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000
goto END

:MIGRATE_ONLY
echo.
echo Applying database migrations to MySQL...
python manage.py makemigrations
python manage.py migrate
echo.
pause
goto END

:SEED_ONLY
echo.
echo Populating demonstration data into MySQL...
python manage.py seed_data
echo.
pause
goto END

:START_SERVER
echo.
echo Starting Django Development Server...
start http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000
goto END

:END
echo.
