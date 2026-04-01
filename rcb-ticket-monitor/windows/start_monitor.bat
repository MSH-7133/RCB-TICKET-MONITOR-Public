@echo off
REM Start RCB Ticket Monitor (Windows)

echo ======================================================================
echo   Starting RCB Ticket Monitor
echo ======================================================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start monitor (opens new window - you can see output in real-time)
REM For true background with log file, use: start_monitor_hidden.vbs
start python rcb_ticket_monitor.py 15

echo.
echo [OK] Monitor started!
echo.
echo To view logs: type "view_logs.bat"
echo To stop: type "stop_monitor.bat"
echo.
pause
