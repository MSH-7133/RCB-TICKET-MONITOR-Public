@echo off
REM Run RCB Booking Bot Manually (Windows)

echo ======================================================================
echo   RCB Ticket Booking Bot
echo ======================================================================
echo.
echo [WARNING]  Make sure tickets are available on the website!
echo.
echo Bot will:
echo   1. Login (you need to enter OTP)
echo   2. Select stand (PUMA B → BOAT C → SUN PHARMA A)
echo   3. Select seats (smart selection)
echo   4. Fill checkout form
echo   5. Initiate UPI payment (you enter UPI PIN)
echo.
echo Press Ctrl+C to cancel
timeout /t 5

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run bot
python rcb_booking_bot.py

pause
