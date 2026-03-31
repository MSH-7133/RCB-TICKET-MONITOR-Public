@echo off
REM View RCB Monitor Logs (Windows)

echo ======================================================================
echo   RCB Monitor Logs (Press Ctrl+C to exit)
echo ======================================================================
echo.

if exist rcb_monitor.log (
    REM Use PowerShell to tail the log file (similar to Unix tail -f)
    powershell -Command "Get-Content rcb_monitor.log -Wait -Tail 50"
) else (
    echo No log file found (rcb_monitor.log)
    echo.
    echo Start the monitor first: start_monitor.bat
    pause
)
