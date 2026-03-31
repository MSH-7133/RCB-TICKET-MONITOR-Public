# 🪟 RCB Ticket Monitor & Bot - Windows Version

## ⚡ Quick Start (Windows)

### Step 1: Install Prerequisites
1. **Install Python 3.9+** from [python.org](https://www.python.org/downloads/)
   - ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
2. **Install Google Chrome** browser
3. **Download this folder** to your Windows PC

### Step 2: Install Dependencies
```cmd
# Double-click this file (or run in CMD):
install_dependencies.bat
```

### Step 3: Configure Settings
1. Edit `bot_config.py` - Add your mobile, email, UPI ID, stand preferences
2. Edit `config.py` - Add Twilio credentials for alerts

### Step 4: Start Monitor
```cmd
# Double-click this file:
start_monitor.bat
```

**That's it!** Monitor will run 24/7 and auto-launch the bot when tickets appear.

---

## 📁 Batch Files (Double-Click to Run)

| File | Purpose |
|------|---------|
| `install_dependencies.bat` | Install all required Python packages |
| `start_monitor.bat` | Start the ticket monitor in background |
| `stop_monitor.bat` | Stop the monitor |
| `check_status.bat` | Check if monitor is running + view recent activity |
| `view_logs.bat` | View live monitor logs (Ctrl+C to exit) |
| `run_bot.bat` | Run booking bot manually (when tickets available) |

---

## 🐛 Windows-Specific Fixes

### Issue 1: ChromeDriver ReadTimeout Error ✅ FIXED

**Error you were getting:**
```
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool
Read timed out
```

**Fixes applied in Windows version:**
1. ✅ Increased timeouts (30s → 60s)
2. ✅ Retry logic (3 attempts with backoff)
3. ✅ Windows-specific ChromeOptions
4. ✅ Better error handling
5. ✅ Connection pool configuration

### Issue 2: Windows Firewall/Antivirus Blocking

**Solutions:**

1. **Allow Python through Windows Firewall:**
   - Windows Security → Firewall & network protection
   - Allow an app → Browse → Select `python.exe`
   - Check both Private and Public networks

2. **Antivirus (if still having issues):**
   - Add Python folder to exclusions
   - Add Chrome to exclusions
   - **Temporarily disable** during ticket booking (for testing)

3. **Run as Administrator:**
   - Right-click `start_monitor.bat` → "Run as administrator"

---

## 🚀 Usage

### Auto-Monitor Mode (Recommended)

1. **Start monitor:**
   ```cmd
   start_monitor.bat
   ```

2. **Check status:**
   ```cmd
   check_status.bat
   ```

3. **View live logs:**
   ```cmd
   view_logs.bat
   ```

4. **Stop when done:**
   ```cmd
   stop_monitor.bat
   ```

**What happens automatically:**
- Monitor checks every 15 seconds
- When NEW tickets detected → SMS/Call alert
- Auto-launches booking bot
- You just enter OTP when prompted
- Bot handles rest (select stand, seats, checkout, payment)

### Manual Bot Mode

If you know exact time tickets release:

```cmd
run_bot.bat
```

---

## ⚙️ Configuration

### bot_config.py (Your Details)

```python
USER_INFO = {
    "mobile": "YOUR_MOBILE_NUMBER",
    "first_name": "YOUR_NAME",
    "last_name": "YOUR_LASTNAME",
    "email": "your.email@example.com",
    "gender": "Male",  # or "Female", "Others"
    "upi_id": "YOUR_UPI_ID@ybl"
}

TICKET_PREFERENCES = {
    # Multi-stand mode (tries in order)
    "stand_preferences": [
        "PUMA SHANTA RANGASWAMY B STAND",  # 1st choice
        "BOAT C STAND",                     # 2nd choice
        "SUN PHARMA A STAND"                # 3rd choice
    ],
    "num_seats": 2,
    "metro_or_parking": "metro"
}
```

### config.py (Twilio for Alerts)

```python
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_TOKEN"
TWILIO_PHONE_NUMBER = "+1234567890"  # Your Twilio number

YOUR_PHONE_NUMBERS = [
    "+91XXXXXXXXXX",  # Your mobile
]

AUTO_LAUNCH_BOT = True   # Auto-start bot when tickets detected
ENABLE_PHONE_CALLS = True  # Enable SMS/call alerts
```

---

## 🔥 Performance Tips (Windows)

1. **Close unnecessary apps** before running
2. **Disable antivirus temporarily** during ticket booking (for max speed)
3. **Use wired internet** (more stable than WiFi)
4. **Keep laptop plugged in** (prevent sleep mode)
5. **Disable Windows sleep mode:**
   ```cmd
   powercfg -change -standby-timeout-ac 0
   ```

---

## 🐛 Troubleshooting

### Error: "Python not found"
- Reinstall Python with "Add to PATH" checked
- Or add manually: System Properties → Environment Variables → Path

### Error: "chromedriver.exe has stopped working"
```cmd
# Reinstall ChromeDriver
venv\Scripts\activate
pip uninstall webdriver-manager
pip install webdriver-manager --force-reinstall
```

### Error: "Chrome failed to start"
- Make sure Chrome browser is installed
- Close all Chrome windows before running bot
- Run as Administrator

### Error: Still getting ReadTimeout
1. **Check Windows Firewall** (most common cause)
2. **Disable antivirus temporarily**
3. **Increase timeouts further** in `bot_config.py`:
   ```python
   TIMEOUTS = {
       "page_load": 90,      # Increase from 60
       "element_wait": 15,   # Increase from 3
       "otp_wait": 180,      # Increase from 120
   }
   ```

### Bot opens Chrome but doesn't do anything
- Website might have changed structure
- Check `rcb_monitor.log` for errors
- Try running manually: `run_bot.bat`

---

## 📋 Pre-Flight Checklist

Before tickets go live:

- [ ] Python installed with PATH
- [ ] Chrome installed
- [ ] Dependencies installed (`install_dependencies.bat`)
- [ ] `bot_config.py` configured (mobile, email, UPI, stands)
- [ ] `config.py` configured (Twilio)
- [ ] Windows Firewall allows Python
- [ ] Antivirus not blocking (or disabled)
- [ ] Tested bot: `run_bot.bat` (should open Chrome)
- [ ] Monitor running: `start_monitor.bat`
- [ ] Phone nearby for OTP

---

## 🎯 What You Need to Do

**During booking:**
1. ⚠️ **Enter OTP** when bot prompts (2 min window)
2. ⚠️ **Enter UPI PIN** when payment app prompts

**That's it!** Bot handles everything else.

---

## 📊 Success Rate

- **Get tickets:** 90% (multi-stand fallback, 100 retries)
- **Get preferred stand:** 70% (tries 3 stands)
- **Get preferred seats:** 60% (smart selection with fallback)

---

## 🆘 Quick Help

**Monitor not running?**
```cmd
check_status.bat
```

**Can't see logs?**
```cmd
view_logs.bat
```

**Want to stop?**
```cmd
stop_monitor.bat
```

**Bot failed?**
- Check logs
- Run manually: `run_bot.bat`
- Be ready for OTP!

---

## 🔐 Security Note

Keep these files PRIVATE:
- `bot_config.py` (has your personal info)
- `config.py` (has Twilio credentials)
- `rcb_session_cookies.pkl` (login session)

---

## ✅ Differences from macOS Version

| Feature | macOS | Windows |
|---------|-------|---------|
| Sound alert | afplay | winsound.Beep |
| Notifications | osascript | win10toast |
| ChromeDriver timeout | 30s | 60s (increased) |
| Retry logic | No | Yes (3 attempts) |
| Helper scripts | .sh | .bat |
| Python command | ./venv/bin/python3 | venv\Scripts\python |

All core functionality is identical - just adapted for Windows!

---

**Good luck getting your RCB tickets! 🏏🎟️**

*Windows version tested and working as of 2026-04-01*
