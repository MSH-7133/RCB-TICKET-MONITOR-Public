@echo off
REM Install Dependencies for RCB Ticket Bot (Windows)

echo ======================================================================
echo   RCB Ticket Bot - Dependency Installation
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.9+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found:
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
    echo.
) else (
    echo ✅ Virtual environment already exists
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
echo.

REM Install Windows-specific packages
echo Installing Windows-specific packages...
pip install win10toast pywin32
echo.

echo ======================================================================
echo   ✅ Installation Complete!
echo ======================================================================
echo.
echo Next steps:
echo 1. Edit bot_config.py (add your details)
echo 2. Edit config.py (add Twilio credentials)
echo 3. Run: start_monitor.bat
echo.
pause
