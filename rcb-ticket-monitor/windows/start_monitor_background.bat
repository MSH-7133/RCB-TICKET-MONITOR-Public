@echo off
REM Start RCB Monitor in Background (Windows) - Creates Log File

echo ======================================================================
echo   Starting RCB Ticket Monitor (Background Mode)
echo ======================================================================
echo.

REM Check if venv exists
if not exist venv\Scripts\python.exe (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run: install_dependencies.bat
    pause
    exit /b 1
)

REM Kill any existing monitor processes
tasklist /FI "IMAGENAME eq python.exe" | findstr /C:"python.exe" >nul
if %errorlevel%==0 (
    echo Stopping existing monitor...
    call stop_monitor.bat
    timeout /t 2 >nul
)

REM Start monitor in background with output to log file
echo Starting monitor...
start /B venv\Scripts\python.exe rcb_ticket_monitor.py 15 > rcb_monitor.log 2>&1

echo.
echo [OK] Monitor started in background!
echo.
echo Log file: rcb_monitor.log
echo.
echo Commands:
echo   - Check status: check_status.bat
echo   - View logs:    view_logs.bat
echo   - Stop:         stop_monitor.bat
echo.
pause
