@echo off
REM Stop RCB Ticket Monitor (Windows)

echo ======================================================================
echo   Stopping RCB Ticket Monitor
echo ======================================================================
echo.

REM Check if Python is running
tasklist /FI "IMAGENAME eq python.exe" | findstr /C:"python.exe" >nul
if %errorlevel%==0 (
    echo Killing all Python processes...
    taskkill /F /IM python.exe /T
    echo [OK] Python processes stopped
) else (
    echo [INFO] No Python processes found
)

REM Also check for pythonw.exe (hidden mode)
tasklist /FI "IMAGENAME eq pythonw.exe" | findstr /C:"pythonw.exe" >nul
if %errorlevel%==0 (
    echo Killing pythonw processes...
    taskkill /F /IM pythonw.exe /T
    echo [OK] Pythonw processes stopped
)

echo.
echo [OK] Monitor stopped
echo.
pause
