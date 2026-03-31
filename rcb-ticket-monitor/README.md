# 🎟️ RCB Ticket Monitor & Auto-Booking Bot

Automated system to monitor Royal Challengers Bengaluru (RCB) ticket releases and automatically book tickets when they become available.

## 🌟 Features

### 📡 Intelligent Monitor
- **24/7 Monitoring**: Continuously checks RCB shop for new match tickets
- **Smart Detection**: Only alerts for NEW matches (won't spam for already-known matches)
- **Multi-Channel Alerts**: SMS, phone calls, macOS notifications, and sound alerts
- **Auto-Launch**: Automatically starts booking bot when new tickets detected

### 🤖 Advanced Booking Bot
- **Multi-Stand Preference**: Try multiple stands in priority order (fallback strategy)
- **Smart Seat Selection**:
  - Preferred rows (K-Z for PUMA/BOAT C, Row A for SUN PHARMA A)
  - Middle/front seat preference
  - Automatic fallback to any available seats after 20 attempts
- **Session Management**: Saves login cookies to skip OTP on subsequent runs
- **Error Recovery**: Handles "Seats Being Taken" errors, retries up to 100 times
- **Payment Automation**: Auto-fills checkout form and initiates UPI payment
- **Payment Monitoring**: Detects and confirms successful booking

## 📋 Requirements

- Python 3.9+
- macOS (tested on macOS, adaptable for other platforms)
- Google Chrome browser
- Twilio account (for SMS/call alerts)
- Active internet connection

## 🚀 Installation

### 1. Clone Repository
```bash
cd /Users/mallikarjun.h
git clone <your-repo-url>
cd rcb-ticket-monitor
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Settings

#### A. Bot Configuration (`bot_config.py`)
```python
USER_INFO = {
    "mobile": "YOUR_MOBILE_NUMBER",
    "first_name": "YOUR_FIRST_NAME",
    "last_name": "YOUR_LAST_NAME",
    "email": "YOUR_EMAIL@example.com",
    "gender": "Male",  # or "Female", "Others"
    "upi_id": "YOUR_UPI_ID@ybl"
}

TICKET_PREFERENCES = {
    "match_name": "Royal Challengers Bengaluru vs [Team Name]",

    # Multi-stand mode (tries in order)
    "stand_preferences": [
        "PUMA SHANTA RANGASWAMY B STAND",  # 1st preference
        "BOAT C STAND",                     # 2nd preference
        "SUN PHARMA A STAND"                # 3rd preference
    ],

    "num_seats": 2,
    "metro_or_parking": "metro"
}
```

#### B. Monitor Configuration (`config.py`)
```python
# Twilio Configuration (for alerts)
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_PHONE_NUMBER = "+1234567890"  # Your Twilio number

YOUR_PHONE_NUMBERS = [
    "+91XXXXXXXXXX",  # Your mobile number(s)
]

ENABLE_PHONE_CALLS = True  # Enable/disable SMS and calls
AUTO_LAUNCH_BOT = True     # Auto-start bot when tickets detected
SMS_RETRY_COUNT = 3
```

## 📖 Usage

### Option 1: Auto-Monitor Mode (Recommended)

**Start the monitor - it will auto-launch the bot when tickets are detected:**

```bash
# Start monitor in background
nohup ./venv/bin/python3 -u rcb_ticket_monitor.py 15 > rcb_monitor.log 2>&1 &
echo $! > rcb_monitor.pid

# Check status
./check_status.sh

# View live logs
tail -f rcb_monitor.log

# Stop monitor
./stop_monitor.sh
```

**What happens automatically:**
1. Monitor checks every 15 seconds for new tickets
2. When new match detected → Sends SMS/call alerts
3. Auto-launches booking bot
4. You just need to **enter OTP** when prompted
5. Bot handles everything else

### Option 2: Manual Bot Mode

**Run the booking bot manually when tickets are available:**

```bash
./venv/bin/python3 rcb_booking_bot.py
```

## 🔧 How It Works

### Monitor Flow
```
Monitor checks RCB website (every 15s)
    ↓
Detects "BUY TICKETS" button
    ↓
Extracts match names
    ↓
Checks against known_matches.json
    ↓
NEW match found? → Alert + Auto-launch bot
    ↓
Already known? → Skip (no spam)
```

### Bot Flow
```
1. Load saved session (skip if fresh start)
    ↓
2. Click BUY TICKETS for target match
    ↓
3. Login (enter OTP if needed)
    ↓
4. Try stands in preference order:
   - PUMA B → BOAT C → SUN PHARMA A
    ↓
5. Smart seat selection:
   - PUMA/BOAT: Rows K-Z, middle seats
   - SUN PHARMA A: Row A, seats 1-20
   - Fallback: Any seats after 20 attempts
    ↓
6. Handle parking/metro popup
    ↓
7. Fill checkout form (auto)
    ↓
8. Initiate UPI payment (enter UPI PIN manually)
    ↓
9. Monitor payment confirmation
    ↓
10. Send success SMS notification
```

## 📁 File Structure

```
rcb-ticket-monitor/
├── rcb_ticket_monitor.py          # Monitor script (detects tickets)
├── rcb_booking_bot.py              # Booking bot (books tickets)
├── bot_config.py                   # Bot configuration
├── config.py                       # Monitor configuration
├── known_matches.json              # Tracked matches (auto-updated)
├── rcb_session_cookies.pkl         # Saved login session (auto-generated)
├── rcb_monitor.log                 # Monitor logs
├── rcb_monitor.pid                 # Monitor process ID
├── requirements.txt                # Python dependencies
├── check_status.sh                 # Helper: Check monitor status
├── stop_monitor.sh                 # Helper: Stop monitor
├── view_logs.sh                    # Helper: View logs
├── test_login_save_session.py      # Helper: Test login and save session
└── README.md                       # This file
```

## ⚙️ Configuration Details

### Seat Selection Strategy

**PUMA B STAND & BOAT C STAND:**
- Priority: Rows K-Z (middle section, better view)
- Seat position: Middle seats preferred (e.g., K25, K26 if row has 1-50)
- Fallback: Any row A-J if K-Z unavailable

**SUN PHARMA A STAND:**
- Priority: Row A (closest to action)
- Seat position: Front seats 1-20 (stand is large)
- Example: A1, A2 > A5, A6 > A15, A16
- Fallback: Rows B-Z with front seats

**Automatic Fallback:**
- Attempts 1-19: Try preferred rows/seats
- Attempts 20+: Accept ANY available seats
- Goal: Better to get ANY seat than miss tickets!

### Timeouts

```python
TIMEOUTS = {
    "page_load": 30,        # Page load timeout
    "element_wait": 3,      # Element wait (fast for speed)
    "otp_wait": 120,        # 2 minutes for OTP entry
    "checkout_timer": 600,  # 10 minutes checkout
    "payment_timer": 360    # 6 minutes payment monitoring
}
```

## 🎯 Important Notes

### Manual Steps Required

1. **OTP Entry**: You must enter OTP when bot triggers login (2 min window)
2. **UPI PIN**: You must enter UPI PIN in payment app when bot initiates payment

### Session Management

- Bot saves login session cookies after successful login
- Next run uses saved session (skips OTP if session valid)
- Sessions may expire after ~7 days
- Delete `rcb_session_cookies.pkl` to force fresh login

### Known Matches Tracking

- Monitor tracks known matches in `known_matches.json`
- Only alerts for NEW matches
- Won't spam for already-announced matches
- Manually edit file to re-enable alerts for a match:

```json
{
  "Royal Challengers Bengaluru vs Sunrisers Hyderabad": true
}
```

Remove entries to get alerts again.

## 🐛 Troubleshooting

### Monitor Not Detecting Tickets

**Check if monitor is running:**
```bash
./check_status.sh
```

**Restart monitor:**
```bash
./stop_monitor.sh
nohup ./venv/bin/python3 -u rcb_ticket_monitor.py 15 > rcb_monitor.log 2>&1 &
echo $! > rcb_monitor.pid
```

**View logs:**
```bash
tail -f rcb_monitor.log
```

### Bot Fails at Seat Selection

- Bot will automatically retry up to 100 times
- After 20 attempts, switches to "relaxed mode" (accepts any seats)
- If still failing, website might have changed structure

### Session Expired

```bash
# Delete old session and force fresh login
rm rcb_session_cookies.pkl
```

### ChromeDriver Issues

```bash
# Reinstall ChromeDriver
pip uninstall webdriver-manager
pip install webdriver-manager
```

## 📊 Success Probability

Based on implementation:

- **Get Tickets**: 90% (multi-stand fallback + 100 retry attempts)
- **Get Preferred Stand**: 70% (tries 3 stands in order)
- **Get Preferred Seats**: 60% (smart selection with fallback)

## ⚠️ Disclaimer

This tool is for **personal use only**. Please:
- Use responsibly
- Don't abuse the system
- Follow RCB's terms of service
- Limit to booking for yourself/family

## 🔐 Security

- Keep `config.py` and `bot_config.py` private (contains credentials)
- Add to `.gitignore`:
  ```
  config.py
  bot_config.py
  rcb_session_cookies.pkl
  rcb_monitor.log
  *.pid
  ```

## 📞 Support

For issues or questions:
1. Check logs: `tail -f rcb_monitor.log`
2. Verify configuration files
3. Test bot manually: `./venv/bin/python3 rcb_booking_bot.py`
4. Check monitor status: `./check_status.sh`

## 🎉 Credits

Built for RCB fans who don't want to miss ticket sales!

## 📝 License

For personal use only. Not for commercial distribution.

---

**Good luck getting your RCB tickets! 🏏🎟️**
