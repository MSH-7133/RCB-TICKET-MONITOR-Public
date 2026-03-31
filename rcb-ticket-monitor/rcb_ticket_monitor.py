#!/usr/bin/env python3
"""
RCB Ticket Monitor
Monitors multiple RCB shop URLs for ticket availability
Sends sound and terminal alerts when tickets become available
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import sys
from datetime import datetime
import subprocess
import json

# Import Twilio for phone calls
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

# Import configuration
try:
    from config import (
        YOUR_PHONE_NUMBERS,
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_PHONE_NUMBER,
        ENABLE_PHONE_CALLS,
        SMS_RETRY_COUNT
    )
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    ENABLE_PHONE_CALLS = False
    YOUR_PHONE_NUMBERS = []
    SMS_RETRY_COUNT = 3

# Auto-launch booking bot when new tickets detected
try:
    from config import AUTO_LAUNCH_BOT
except ImportError:
    AUTO_LAUNCH_BOT = True  # Default: auto-launch enabled

class RCBTicketMonitor:
    def __init__(self, check_interval=30):
        """
        Initialize the ticket monitor

        Args:
            check_interval: Seconds between checks (default: 30)
        """
        # Monitor the dedicated ticket page (singular - confirmed by user)
        self.urls_to_check = [
            "https://shop.royalchallengers.com/ticket",
        ]

        self.check_interval = check_interval
        self.tickets_found = False
        self.driver = None
        self.last_alert_time = 0  # Track when we last sent alerts
        self.checks_since_browser_restart = 0  # Track browser age
        self.browser_restart_interval = 100  # Restart browser every 100 checks (~70 min)

        # Known matches tracking to avoid duplicate alerts
        self.known_matches_file = "known_matches.json"
        self.known_matches = self.load_known_matches()

        # Keywords that indicate tickets are available
        self.ticket_keywords = [
            'ticket', 'tickets', 'match', 'game', 'seat', 'seats',
            'stadium', 'venue', 'booking', 'book now', 'buy tickets',
            'ipl', 'chinnaswamy'
        ]

    def log(self, message, level="INFO"):
        """Print timestamped log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        sys.stdout.flush()

    def load_known_matches(self):
        """Load known matches from JSON file"""
        try:
            if os.path.exists(self.known_matches_file):
                with open(self.known_matches_file, 'r') as f:
                    data = json.load(f)
                    self.log(f"Loaded {len(data)} known match(es) from {self.known_matches_file}")
                    return data
            else:
                self.log(f"No existing known matches file - creating new tracker")
                return {}
        except Exception as e:
            self.log(f"Error loading known matches: {e}", "WARNING")
            return {}

    def save_known_matches(self):
        """Save known matches to JSON file"""
        try:
            with open(self.known_matches_file, 'w') as f:
                json.dump(self.known_matches, f, indent=2)
            self.log(f"Saved {len(self.known_matches)} known match(es) to {self.known_matches_file}")
            return True
        except Exception as e:
            self.log(f"Error saving known matches: {e}", "ERROR")
            return False

    def add_known_match(self, match_name):
        """Add a match to known matches list"""
        if match_name not in self.known_matches:
            self.known_matches[match_name] = True
            self.save_known_matches()
            self.log(f"Added '{match_name}' to known matches")
            return True
        return False

    def is_known_match(self, match_name):
        """Check if a match is already known"""
        return match_name in self.known_matches

    def launch_booking_bot(self):
        """Launch the booking bot to automatically book tickets"""
        try:
            self.log("Closing monitor browser to free resources for bot...", "INFO")

            # Close monitor's browser to free memory for bot
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

            self.log("Starting booking bot (rcb_booking_bot.py)...", "ALERT")
            self.log("Bot will use preferences from bot_config.py", "INFO")

            # Launch bot in foreground (visible browser for user to see progress)
            bot_process = subprocess.Popen(
                ['./venv/bin/python3', 'rcb_booking_bot.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            self.log(f"Booking bot started (PID: {bot_process.pid})", "ALERT")
            self.log("=" * 60, "ALERT")
            self.log("📺 BOOKING BOT RUNNING - WATCH THE BROWSER WINDOW", "ALERT")
            self.log("=" * 60, "ALERT")

            # Stream bot output to monitor log
            for line in bot_process.stdout:
                print(line, end='')  # Print to monitor log
                sys.stdout.flush()

            # Wait for bot to complete
            bot_process.wait()
            exit_code = bot_process.returncode

            if exit_code == 0:
                self.log("=" * 60, "ALERT")
                self.log("✅ BOOKING BOT COMPLETED SUCCESSFULLY!", "ALERT")
                self.log("=" * 60, "ALERT")
            else:
                self.log("=" * 60, "ERROR")
                self.log(f"❌ Booking bot failed with exit code {exit_code}", "ERROR")
                self.log("=" * 60, "ERROR")

            # Reinitialize browser for continued monitoring
            self.log("Reinitializing monitor browser...", "INFO")
            self.setup_driver()

            return exit_code == 0

        except Exception as e:
            self.log(f"Error launching booking bot: {e}", "ERROR")
            import traceback
            traceback.print_exc()

            # Try to reinitialize browser
            try:
                self.setup_driver()
            except:
                pass

            return False

    def extract_match_names(self, html_content):
        """
        Extract match names from the ticket listing page
        Returns list of match names found
        """
        if not html_content:
            return []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            match_names = []

            # Look for match names - typically in headings or product titles
            # Common patterns: "Royal Challengers Bengaluru vs [Team Name]"
            # or "RCB vs [Team]"

            # Strategy 1: Find headings with "vs" in them
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'div', 'span'])

            for heading in headings:
                text = heading.get_text().strip()

                # Check if this looks like a match name
                if 'vs' in text.lower() or ' v ' in text.lower():
                    # Clean up the text
                    text = ' '.join(text.split())  # Normalize whitespace

                    # Filter out navigation/header elements
                    parent = heading.find_parent()
                    if parent and parent.name in ['nav', 'header', 'footer']:
                        continue

                    # Check if it has team names
                    if any(team in text for team in ['Royal Challengers', 'RCB', 'Bengaluru',
                                                      'Mumbai', 'Delhi', 'Chennai', 'Kolkata',
                                                      'Punjab', 'Rajasthan', 'Hyderabad', 'Gujarat',
                                                      'Lucknow']):
                        match_names.append(text)
                        self.log(f"    Found match: {text}", "DEBUG")

            # Remove duplicates while preserving order
            unique_matches = []
            seen = set()
            for match in match_names:
                if match not in seen:
                    unique_matches.append(match)
                    seen.add(match)

            return unique_matches

        except Exception as e:
            self.log(f"Error extracting match names: {e}", "ERROR")
            return []

    def rotate_logs(self):
        """Rotate log file if it gets too large (prevent disk space issues)"""
        try:
            import os
            log_file = 'rcb_monitor.log'
            max_size = 50 * 1024 * 1024  # 50 MB

            if os.path.exists(log_file):
                size = os.path.getsize(log_file)
                if size > max_size:
                    # Rename old log
                    backup = f'rcb_monitor.log.old'
                    if os.path.exists(backup):
                        os.remove(backup)
                    os.rename(log_file, backup)
                    self.log(f"Log file rotated (was {size / (1024*1024):.2f} MB)", "INFO")
        except Exception as e:
            pass  # Don't crash if log rotation fails

    def setup_driver(self):
        """Setup Chrome driver in headless mode with stealth settings"""
        try:
            chrome_options = Options()
            # Use new headless mode (better for modern sites)
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')

            # Stealth settings to avoid detection
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Hide webdriver property
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                '''
            })

            self.driver.set_page_load_timeout(30)
            self.log("Chrome driver initialized successfully (stealth mode)")
            return True
        except Exception as e:
            self.log(f"Error setting up Chrome driver: {e}", "ERROR")
            return False

    def send_sms_alert(self, retry_count=3):
        """Send SMS alerts with retry logic"""
        if not ENABLE_PHONE_CALLS:
            self.log("SMS alerts disabled in config", "INFO")
            return

        if not TWILIO_AVAILABLE:
            self.log("Twilio not installed - skipping SMS", "WARNING")
            return

        if not CONFIG_AVAILABLE:
            self.log("Config file not found - skipping SMS", "WARNING")
            return

        try:
            # Initialize Twilio client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            # Send SMS to all configured phone numbers with retries
            for phone_number in YOUR_PHONE_NUMBERS:
                success = False
                for attempt in range(retry_count):
                    try:
                        self.log(f"📱 Sending SMS to {phone_number} (attempt {attempt + 1}/{retry_count})...", "ALERT")

                        message = client.messages.create(
                            body=f"🚨 URGENT ALERT #{attempt + 1}: RCB TICKETS ARE OUT! Go to https://shop.royalchallengers.com/ticket NOW to book! Tickets are available! Don't miss this!",
                            to=phone_number,
                            from_=TWILIO_PHONE_NUMBER
                        )

                        self.log(f"✅ SMS sent to {phone_number}! Message SID: {message.sid}", "ALERT")
                        success = True
                        break

                    except Exception as e:
                        self.log(f"❌ SMS attempt {attempt + 1} failed for {phone_number}: {e}", "ERROR")
                        if attempt < retry_count - 1:
                            self.log(f"Retrying in 5 seconds...", "INFO")
                            time.sleep(5)

                if not success:
                    self.log(f"⚠️ All SMS attempts failed for {phone_number}", "ERROR")

        except Exception as e:
            self.log(f"❌ Failed to send SMS: {e}", "ERROR")

    def make_phone_call(self):
        """Make phone calls to alert about tickets"""
        if not ENABLE_PHONE_CALLS:
            self.log("Phone calls disabled in config", "INFO")
            return

        if not TWILIO_AVAILABLE:
            self.log("Twilio not installed - skipping phone call", "WARNING")
            return

        if not CONFIG_AVAILABLE:
            self.log("Config file not found - skipping phone call", "WARNING")
            return

        try:
            # Initialize Twilio client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            # Call all configured phone numbers
            for phone_number in YOUR_PHONE_NUMBERS:
                try:
                    self.log(f"📞 Making phone call to {phone_number}...", "ALERT")

                    # Make the call with a simpler, louder message
                    call = client.calls.create(
                        twiml='<Response><Say voice="woman" language="en-IN">RCB Tickets are out! RCB Tickets are out! Go to shop dot royal challengers dot com now!</Say><Pause length="1"/><Say voice="woman" language="en-IN">Urgent! Tickets available! Book now!</Say></Response>',
                        to=phone_number,
                        from_=TWILIO_PHONE_NUMBER,
                        machine_detection='DetectMessageEnd'  # Better detection
                    )

                    self.log(f"✅ Phone call initiated to {phone_number}! Call SID: {call.sid}", "ALERT")

                except Exception as e:
                    self.log(f"❌ Failed to call {phone_number}: {e}", "ERROR")

        except Exception as e:
            self.log(f"❌ Failed to initialize Twilio client: {e}", "ERROR")

    def play_alert_sound(self):
        """Play alert sound on Mac"""
        try:
            # Mac system sound
            subprocess.run(['afplay', '/System/Library/Sounds/Submarine.aiff'],
                         check=False)
            # Play multiple times for emphasis
            for _ in range(3):
                time.sleep(0.5)
                subprocess.run(['afplay', '/System/Library/Sounds/Submarine.aiff'],
                             check=False)
        except Exception as e:
            self.log(f"Could not play sound: {e}", "WARNING")
            # Fallback: system beep
            print('\a' * 5)

    def show_terminal_alert(self, url="", new_matches=None):
        """Show prominent alert in terminal"""
        if new_matches:
            matches_text = "\n".join([f"           - {m}" for m in new_matches])
            alert_msg = f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🎟️  NEW MATCH TICKETS AVAILABLE! 🎟️             ║
║                                                           ║
{matches_text}
║                                                           ║
║              >>> GO BOOK YOUR TICKETS NOW! <<<           ║
║                                                           ║
║     {url.ljust(53)}║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        else:
            alert_msg = f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🎟️  TICKETS AVAILABLE ON RCB WEBSITE! 🎟️         ║
║                                                           ║
║     {url.ljust(53)}║
║                                                           ║
║              >>> GO BOOK YOUR TICKETS NOW! <<<           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        print("\n" * 3)
        print("\033[91m" + alert_msg + "\033[0m")  # Red color
        print("\n" * 3)
        sys.stdout.flush()

        # Send macOS notification
        try:
            match_info = f" - {', '.join(new_matches)}" if new_matches else ""
            os.system(f'''
                osascript -e 'display notification "New match tickets available{match_info}! Go to {url}" with title "🚨 RCB New Tickets!" sound name "Submarine"'
            ''')
        except:
            pass

        # Also show a popup dialog (more visible than notification)
        try:
            match_list = "\n".join(new_matches) if new_matches else "RCB Match"
            subprocess.Popen([
                'osascript', '-e',
                f'display dialog "🎟️ NEW RCB MATCH TICKETS AVAILABLE!\\n\\nMatches:\\n{match_list}\\n\\nGo to:\\n{url}\\n\\nBook your tickets immediately!" with title "🚨 NEW TICKET ALERT 🚨" buttons {{"GO TO WEBSITE"}} default button "GO TO WEBSITE" with icon caution giving up after 60'
            ])
        except:
            pass

    def try_click_tickets_tab(self):
        """Try to find and click a 'Tickets' tab/button if it exists"""
        try:
            # Look for buttons/links with "ticket" text
            ticket_buttons = self.driver.find_elements(By.XPATH,
                "//*[contains(translate(text(), 'TICKET', 'ticket'), 'ticket') and (self::button or self::a)]")

            for btn in ticket_buttons[:3]:  # Try first 3 matches
                try:
                    btn_text = btn.text.strip().lower()
                    if btn_text in ['tickets', 'ticket', 'ipl tickets']:
                        self.log(f"Found '{btn.text}' button - clicking it")
                        btn.click()
                        time.sleep(3)  # Wait for content to load
                        return True
                except:
                    continue
            return False
        except Exception as e:
            self.log(f"No tickets tab found (expected): {str(e)[:50]}", "DEBUG")
            return False

    def restart_browser(self):
        """Restart browser to prevent memory leaks"""
        try:
            if self.driver:
                self.log("Restarting browser to free memory...", "INFO")
                self.driver.quit()
                self.driver = None
                time.sleep(2)
            return self.setup_driver()
        except Exception as e:
            self.log(f"Error restarting browser: {e}", "ERROR")
            return False

    def fetch_page(self, url):
        """Fetch the webpage content using Selenium"""
        try:
            # Periodically restart browser to prevent memory leaks
            if self.checks_since_browser_restart >= self.browser_restart_interval:
                self.restart_browser()
                self.checks_since_browser_restart = 0

            if not self.driver:
                if not self.setup_driver():
                    return None

            self.checks_since_browser_restart += 1
            self.driver.get(url)

            # Wait for page to load - wait for the main content div
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "rcb-shop"))
                )
                # Wait for React content to render (10 seconds minimum needed for content to appear)
                time.sleep(10)
            except Exception as e:
                self.log(f"Timeout waiting for page elements: {e}", "WARNING")

            # Get the fully rendered HTML
            html_content = self.driver.page_source
            return html_content

        except Exception as e:
            self.log(f"Error fetching page {url}: {e}", "ERROR")
            # Try to reinitialize driver on error
            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass
            self.driver = None
            return None

    def check_for_tickets(self, html_content):
        """
        Check if ACTUAL match tickets (products with buy buttons) are available

        IMPROVED DETECTION:
        - Looks for product containers with ticket keywords
        - Requires buy buttons/price within those products
        - Ignores navigation/header elements
        - Prevents false positives from menu items

        Returns:
            tuple: (tickets_found: bool, found_text: str)
        """
        if not html_content:
            return False, ""

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # STRATEGY: Look for product containers, not just keywords

            # 1. Find all potential product containers
            product_containers = soup.find_all(['div', 'article', 'section', 'li'],
                                              class_=lambda x: x and (
                                                  'product' in x.lower() or
                                                  'card' in x.lower() or
                                                  'item' in x.lower() or
                                                  'listing' in x.lower() or
                                                  'grid' in x.lower()
                                              ))

            ticket_products_found = []

            for container in product_containers:
                container_text = container.get_text().lower()

                # Check if this container mentions tickets/matches
                has_ticket_keywords = any(kw in container_text for kw in
                                         ['ticket', 'match', 'ipl', 'game', 'seat'])

                if not has_ticket_keywords:
                    continue

                # Check if this container has purchase options (buy buttons, prices, etc.)
                has_buy_button = container.find(['button', 'a'],
                                               string=lambda t: t and (
                                                   'add to cart' in t.lower() or
                                                   'buy' in t.lower() or
                                                   'book' in t.lower() or
                                                   'purchase' in t.lower() or
                                                   'add to bag' in t.lower() or
                                                   'get tickets' in t.lower()
                                               ))

                # Check for price indicators (₹, Rs, price, amount)
                has_price = ('₹' in container_text or
                           'rs' in container_text or
                           'price' in container_text or
                           'amount' in container_text)

                # VALID TICKET PRODUCT: Has ticket keywords + (buy button OR price)
                if has_buy_button or has_price:
                    product_info = container_text[:150].replace('\n', ' ').strip()
                    ticket_products_found.append(product_info)
                    self.log(f"    Found ticket product: {product_info[:80]}...", "INFO")

            # If we found actual ticket products with purchase options
            if ticket_products_found:
                return True, f"Found {len(ticket_products_found)} match ticket(s) with buy buttons/prices"

            # 2. PRIMARY SIGNAL: Look for "buy ticket" / "buy tickets" buttons/text
            #    This is the CONFIRMED signal from user - appears when matches are available
            buy_ticket_elements = soup.find_all(['button', 'a', 'div', 'span'],
                                               string=lambda t: t and (
                                                   'buy ticket' in t.lower() or
                                                   'buy tickets' in t.lower()
                                               ))

            if buy_ticket_elements:
                # Found the specific "buy ticket(s)" text - this is the real deal!
                for elem in buy_ticket_elements:
                    elem_text = elem.get_text().strip()
                    # Make sure it's not in navigation (check if it's in a product context)
                    parent = elem.find_parent()
                    # Verify it's not just a nav link
                    if parent and parent.name not in ['nav', 'header', 'footer']:
                        return True, f"MATCH TICKETS FOUND! Button: '{elem_text}'"

            # 3. Alternative check: Look for explicit "tickets available" messages
            #    (in case page structure is different)
            page_text = soup.get_text().lower()

            # Look for strong availability signals outside of navigation
            body = soup.find('body')
            if body:
                # Exclude navigation/header/footer from this check
                for nav in body.find_all(['nav', 'header', 'footer']):
                    nav.decompose()

                body_text = body.get_text().lower()

                # Check for explicit ticket availability messages
                availability_phrases = [
                    'buy ticket',
                    'buy tickets',
                    'tickets available now',
                    'tickets on sale',
                    'book your tickets',
                    'tickets released',
                    'buy tickets now',
                    'get your tickets'
                ]

                for phrase in availability_phrases:
                    if phrase in body_text:
                        return True, f"Ticket availability message: '{phrase}'"

            # 3. If page has buy buttons and ticket keywords (but not in nav)
            #    This catches cases where product structure is different
            buy_buttons_on_page = soup.find_all(['button', 'a'],
                                               string=lambda t: t and (
                                                   'add to cart' in t.lower() or
                                                   'buy now' in t.lower() or
                                                   'book now' in t.lower()
                                               ))

            if buy_buttons_on_page and len(buy_buttons_on_page) >= 1:
                # Make sure these buttons are near ticket content
                for button in buy_buttons_on_page:
                    # Check parent containers for ticket keywords
                    parent = button.find_parent()
                    for _ in range(5):  # Check up to 5 levels up
                        if parent:
                            parent_text = parent.get_text().lower()
                            if any(kw in parent_text for kw in ['ticket', 'match', 'ipl']):
                                return True, f"Buy button found with ticket content: {button.get_text()}"
                            parent = parent.find_parent()

            # No valid ticket products found
            return False, ""

        except Exception as e:
            self.log(f"Error parsing page: {e}", "ERROR")
            return False, ""

    def monitor(self):
        """Main monitoring loop"""
        self.log("🚀 Starting RCB Ticket Monitor (Multi-URL)")
        self.log(f"Monitoring {len(self.urls_to_check)} URLs:")
        for url in self.urls_to_check:
            self.log(f"  - {url}")
        self.log(f"Check interval: {self.check_interval} seconds")
        self.log(f"Browser restart: Every {self.browser_restart_interval} checks (~{self.browser_restart_interval * 15 / 60:.0f} min)")
        self.log("Press Ctrl+C to stop\n")

        check_count = 0

        try:
            while True:
                check_count += 1
                self.log(f"Check #{check_count}: Starting scan...")

                # Rotate logs every 100 checks to prevent huge files
                if check_count % 100 == 0:
                    self.rotate_logs()

                # Check each URL
                for url in self.urls_to_check:
                    self.log(f"  Checking: {url}")

                    html_content = self.fetch_page(url)

                    if html_content:
                        tickets_available, details = self.check_for_tickets(html_content)

                        if tickets_available:
                            # Tickets detected - now check if they're NEW matches
                            match_names = self.extract_match_names(html_content)

                            if match_names:
                                self.log(f"  Found {len(match_names)} match(es) with tickets")

                                # Check which matches are NEW
                                new_matches = [m for m in match_names if not self.is_known_match(m)]

                                if new_matches:
                                    # NEW MATCH DETECTED!
                                    self.log("=" * 60, "ALERT")
                                    self.log("🚨 NEW MATCH TICKETS DETECTED!", "ALERT")
                                    self.log("=" * 60, "ALERT")
                                    for match in new_matches:
                                        self.log(f"  🆕 {match}", "ALERT")

                                    # Send all alerts
                                    self.show_terminal_alert(url, new_matches=new_matches)
                                    self.play_alert_sound()
                                    self.send_sms_alert(retry_count=SMS_RETRY_COUNT)
                                    self.make_phone_call()

                                    # Add to known matches
                                    for match in new_matches:
                                        self.add_known_match(match)

                                    self.tickets_found = True
                                    self.last_alert_time = time.time()

                                    # AUTO-START BOOKING BOT (if enabled)
                                    if AUTO_LAUNCH_BOT:
                                        self.log("=" * 60, "ALERT")
                                        self.log("🤖 AUTO-LAUNCHING BOOKING BOT!", "ALERT")
                                        self.log("=" * 60, "ALERT")
                                        bot_success = self.launch_booking_bot()

                                        if bot_success:
                                            self.log("✅ Bot completed successfully - tickets likely booked!", "ALERT")
                                        else:
                                            self.log("⚠️ Bot encountered issues - check logs above", "WARNING")
                                    else:
                                        self.log("ℹ️  Auto-launch disabled - book tickets manually", "INFO")

                                    # Continue monitoring but with less frequency
                                    self.log("Continuing to monitor for more new matches (check every 5 minutes)")
                                    self.check_interval = 300  # 5 minutes

                                else:
                                    # All matches are already known - no alert
                                    self.log(f"  ✅ Tickets available but all matches already known:")
                                    for match in match_names:
                                        self.log(f"    - {match}")

                            else:
                                # Tickets detected but couldn't extract match names
                                self.log(f"  ⚠️ Tickets available but couldn't extract match names", "WARNING")
                                self.log(f"  Details: {details}", "WARNING")
                        else:
                            self.log(f"  ⏳ No tickets at {url}")
                    else:
                        self.log(f"  ❌ Failed to fetch {url}", "WARNING")

                    # No delay between URLs - check as fast as possible!

                # Minimal delay before next check cycle (continuous monitoring)
                if not self.tickets_found:
                    self.log(f"Starting next check cycle immediately...\n")
                    time.sleep(1)  # Just 1 second to prevent CPU overload
                else:
                    # After tickets found, check every 5 minutes
                    self.log(f"Next check in {self.check_interval} seconds...\n")
                    time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.log("\n🛑 Monitoring stopped by user")
            if self.driver:
                self.driver.quit()
            sys.exit(0)
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            if self.driver:
                self.driver.quit()
            sys.exit(1)

def main():
    """Entry point"""
    print("=" * 60)
    print("     RCB (Royal Challengers Bengaluru) Ticket Monitor")
    print("=" * 60)

    # Configuration
    check_interval = 30  # seconds (default: 30 seconds)

    # Allow user to specify custom interval
    if len(sys.argv) > 1:
        try:
            check_interval = int(sys.argv[1])
        except ValueError:
            print(f"Invalid interval. Using default: {check_interval} seconds")

    monitor = RCBTicketMonitor(check_interval=check_interval)
    monitor.monitor()

if __name__ == "__main__":
    main()
