# 🪟 Windows Setup Guide for RCB Ticket Monitor & Bot

## 🐛 Common Windows Issues & Fixes

### Issue 1: ChromeDriver ReadTimeout / HTTP Connection Pool Error

**Error:**
```
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='127.0.0.1', port=XXXXX): Read timed out.
```

**Root Cause:**
- Windows firewall/antivirus blocking ChromeDriver
- Slower driver initialization on Windows
- Connection pool timeout too short

**Solutions Applied in Windows Version:**

1. **Increased Timeouts**
2. **Retry Logic for Driver Init**
3. **Better Error Handling**
4. **Windows-Specific ChromeOptions**

## 📝 Key Modifications for Windows

### 1. ChromeDriver Initialization (CRITICAL FIX)

**Original (macOS):**
```python
service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=chrome_options)
self.driver.set_page_load_timeout(30)
```

**Windows Fix:**
```python
# Increased timeout for ChromeDriver installation
service = Service(
    ChromeDriverManager().install(),
    service_args=['--verbose']  # Better debugging
)

# Add retry logic
max_retries = 3
for attempt in range(max_retries):
    try:
        self.driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

        # Increased timeouts for Windows
        self.driver.set_page_load_timeout(60)  # 30 → 60 seconds
        self.driver.set_script_timeout(60)     # NEW

        # Test connection
        self.driver.get("about:blank")
        break

    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(5)  # Wait before retry
            continue
        raise
```

### 2. ChromeOptions for Windows

```python
chrome_options = Options()

# Windows-specific options
chrome_options.add_argument('--disable-gpu')  # Important for Windows
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--window-size=1920,1080')

# Increased timeouts
chrome_options.add_argument('--timeout=60000')  # 60 seconds

# Disable unnecessary features
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
```

### 3. Connection Pool Settings

```python
import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Configure urllib3 for better Windows compatibility
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Increase connection pool size
import http.client
http.client.HTTPConnection._http_vsn = 11
http.client.HTTPConnection._http_vsn_str = 'HTTP/1.1'
```

### 4. Page Load with Retry

**Original:**
```python
self.driver.get(url)
time.sleep(3)
```

**Windows Fix:**
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        self.driver.get(url)
        time.sleep(5)  # Increased wait for Windows
        break
    except TimeoutException:
        if attempt < max_retries - 1:
            self.log(f"Page load timeout, retry {attempt + 1}/{max_retries}", "WARNING")
            time.sleep(3)
            continue
        raise
```

### 5. Windows Notifications

**macOS (original):**
```python
# Uses afplay for sound
subprocess.run(['afplay', '/System/Library/Sounds/Submarine.aiff'])

# Uses osascript for notifications
os.system("osascript -e 'display notification ...'")
```

**Windows Fix:**
```python
import winsound  # Windows sound

def play_alert_sound():
    """Windows compatible alert sound"""
    try:
        # Play Windows system sound
        winsound.Beep(1000, 500)  # 1000 Hz for 500ms
        time.sleep(0.5)
        winsound.Beep(1500, 500)
        time.sleep(0.5)
        winsound.Beep(1000, 500)
    except:
        # Fallback to bell
        print('\a' * 5)

def show_terminal_alert(url="", new_matches=None):
    """Windows compatible notification"""
    try:
        # Windows toast notification
        from win10toast import ToastNotifier
        toaster = ToastNotifier()

        match_text = "\n".join(new_matches) if new_matches else "RCB Tickets"
        toaster.show_toast(
            "RCB Ticket Alert!",
            f"New tickets available!\n{match_text}",
            duration=20,
            icon_path=None,
            threaded=True
        )
    except:
        # Fallback to console alert
        print("\n" * 5)
        print("=" * 60)
        print("🎟️ NEW RCB TICKETS AVAILABLE! 🎟️")
        if new_matches:
            for match in new_matches:
                print(f"  - {match}")
        print("=" * 60)
        print("\n" * 5)
```

### 6. Bot Launch Command (Windows)

**macOS:**
```python
bot_process = subprocess.Popen(
    ['./venv/bin/python3', 'rcb_booking_bot.py'],
    ...
)
```

**Windows:**
```python
import sys
import platform

# Get Python executable
if platform.system() == 'Windows':
    python_cmd = sys.executable  # Use current Python
else:
    python_cmd = './venv/bin/python3'

bot_process = subprocess.Popen(
    [python_cmd, 'rcb_booking_bot.py'],
    ...
)
```

## 📦 Additional Windows Dependencies

Add to `requirements.txt`:
```
win10toast  # For Windows notifications
pywin32     # For Windows system integration
```

Install:
```cmd
pip install win10toast pywin32
```

## 🔧 Complete Windows ChromeDriver Fix Function

Add this to both monitor and bot scripts:

```python
def setup_driver_windows(self):
    """Setup Chrome driver with Windows-specific fixes"""
    try:
        chrome_options = Options()

        # Headless mode for Windows
        if BOT_SETTINGS.get("headless", False):
            chrome_options.add_argument('--headless=new')

        # Windows-specific arguments (CRITICAL)
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        # Timeout settings
        chrome_options.add_argument('--timeout=60000')
        chrome_options.add_argument('--dns-prefetch-disable')

        # Stealth settings
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # ChromeDriver service with verbose logging
        service = Service(
            ChromeDriverManager().install(),
            service_args=['--verbose', '--log-path=chromedriver.log']
        )

        # Retry logic for driver initialization
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                self.log(f"Initializing ChromeDriver (attempt {attempt + 1}/{max_retries})...")

                self.driver = webdriver.Chrome(
                    service=service,
                    options=chrome_options
                )

                # Set increased timeouts for Windows
                self.driver.set_page_load_timeout(60)  # 60 seconds
                self.driver.set_script_timeout(60)

                # Hide webdriver property
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                          get: () => undefined
                        })
                    '''
                })

                # Test connection
                self.driver.get("about:blank")

                self.log("✅ Chrome driver initialized successfully (Windows)", "INFO")
                return True

            except Exception as e:
                last_error = e
                self.log(f"ChromeDriver init attempt {attempt + 1} failed: {e}", "WARNING")

                # Close driver if partially initialized
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None

                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                    self.log(f"Waiting {wait_time}s before retry...", "INFO")
                    time.sleep(wait_time)
                else:
                    raise last_error

        return False

    except Exception as e:
        self.log(f"Error setting up ChromeDriver: {e}", "ERROR")
        self.log(f"Try: 1) Restart script, 2) Check Windows Firewall, 3) Disable antivirus temporarily", "ERROR")
        return False
```

## 🚀 How to Use Windows Version

### 1. Navigate to Windows Folder
```cmd
cd windows
```

### 2. Create Virtual Environment
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```cmd
pip install -r requirements.txt
```

### 4. Run Monitor (Windows CMD)
```cmd
python rcb_ticket_monitor.py 15
```

### 5. Run Bot Manually (Windows CMD)
```cmd
python rcb_booking_bot.py
```

## 🔥 Firewall/Antivirus Settings

If still getting timeout errors:

1. **Windows Defender Firewall:**
   - Allow Python through firewall
   - Allow Chrome/ChromeDriver

2. **Antivirus:**
   - Add Python folder to exclusions
   - Add Chrome to exclusions
   - Temporarily disable real-time protection for testing

3. **Check ChromeDriver:**
   ```cmd
   # Find ChromeDriver location
   python -c "from webdriver_manager.chrome import ChromeDriverManager; print(ChromeDriverManager().install())"

   # Test manually
   "C:\Users\...\chromedriver.exe" --version
   ```

## 📝 Quick Checklist

- [ ] Python 3.9+ installed
- [ ] Chrome browser installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Windows Firewall allows Python
- [ ] Antivirus not blocking ChromeDriver
- [ ] Config files updated (bot_config.py, config.py)
- [ ] Test with: `python rcb_booking_bot.py` (should open browser)

## ⚡ Performance Tips for Windows

1. **Close unnecessary apps** before running
2. **Disable antivirus temporarily** during ticket booking
3. **Use wired internet** (more stable than WiFi)
4. **Run as Administrator** if permission issues
5. **Keep laptop plugged in** (prevent sleep mode)

## 🐛 Troubleshooting

### Error: "chromedriver.exe has stopped working"
```cmd
# Reinstall ChromeDriver
pip uninstall webdriver-manager
pip install webdriver-manager --force-reinstall
```

### Error: "Chrome failed to start"
```cmd
# Check Chrome path
where chrome
# Or specify manually in code:
chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
```

### Error: Still getting ReadTimeout
```python
# Increase ALL timeouts in TIMEOUTS dict (bot_config.py):
TIMEOUTS = {
    "page_load": 90,      # 30 → 90
    "element_wait": 10,   # 3 → 10
    "otp_wait": 180,      # 120 → 180
}
```

---

**Next Step:** I'll create the actual modified Python scripts with all these fixes integrated.
