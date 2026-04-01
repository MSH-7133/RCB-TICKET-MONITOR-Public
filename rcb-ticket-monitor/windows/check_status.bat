@echo off
REM Check RCB Monitor Status (Windows)

echo ======================================================================
echo   RCB Ticket Monitor - Status Check
echo ======================================================================
echo.

REM Check if Python is running monitor
tasklist /FI "IMAGENAME eq python.exe" | findstr /C:"python.exe" >nul
if %errorlevel%==0 (
    echo Status: [RUNNING] Monitor is RUNNING
    echo.
    echo Python processes:
    tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
) else (
    echo Status: [STOPPED] Monitor is NOT running
    echo.
    echo To start: type "start_monitor.bat"
)

echo.
echo ======================================================================
echo   Recent Activity (last 20 lines of log)
echo ======================================================================
echo.

if exist rcb_monitor.log (
    REM Show last 20 lines using PowerShell (simpler, no encoding issues with ASCII)
    powershell -Command "Get-Content rcb_monitor.log -Tail 20"
) else (
    echo No log file found (rcb_monitor.log)
)

echo.
pause
