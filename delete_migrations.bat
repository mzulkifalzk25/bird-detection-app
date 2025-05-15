@echo off
setlocal enabledelayedexpansion

:: List of Django apps
set "apps=authentication birds collection discover explore nearby subscription"

echo Starting migration files cleanup...

:: Process each app
for %%a in (%apps%) do (
    echo Processing %%a...
    if exist "%%a\migrations" (
        :: Delete all .py files in migrations except __init__.py
        for %%f in ("%%a\migrations\*.py") do (
            if not "%%~nxf"=="__init__.py" del "%%f"
        )
        :: Delete all .pyc files in migrations
        del /s /q "%%a\migrations\*.pyc" 2>nul
        echo Deleted migrations in %%a
    ) else (
        echo No migrations directory found in %%a
    )
)

echo.
echo Migration files cleanup completed!
echo Note: Don't forget to:
echo 1. Delete your database or remove all tables
echo 2. Run 'python manage.py makemigrations'
echo 3. Run 'python manage.py migrate'

pause