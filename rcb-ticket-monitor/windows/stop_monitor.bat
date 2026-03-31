@echo off
REM Stop RCB Ticket Monitor (Windows)

echo ======================================================================
echo   Stopping RCB Ticket Monitor
echo ======================================================================

REM Kill Python processes running the monitor
taskkill /F /IM python.exe /FI "WINDOWTITLE eq rcb_ticket_monitor*" 2>nul
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq rcb_ticket_monitor*" 2>nul

REM Also try killing by command line (if process name matches)
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /C:"PID:"') do (
    wmic process where "ProcessId=%%a AND CommandLine like '%%rcb_ticket_monitor%%'" delete 2>nul
)

echo.
echo ✅ Monitor stopped
echo.
pause
