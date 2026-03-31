@echo off
REM Start RCB Ticket Monitor (Windows)

echo ======================================================================
echo   Starting RCB Ticket Monitor
echo ======================================================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start monitor in background (using pythonw for no console)
start /B python rcb_ticket_monitor.py 15 > rcb_monitor.log 2>&1

echo.
echo ✅ Monitor started!
echo.
echo To view logs: type "view_logs.bat"
echo To stop: type "stop_monitor.bat"
echo.
pause
