#!/usr/bin/env python3
"""
RCB TICKET BOOKING BOT
Complete end-to-end automation for booking RCB match tickets
"""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import geckodriver_autoinstaller
import time
import os
import sys
from datetime import datetime
import traceback
import pickle
from twilio.rest import Client

# Import configuration
from bot_config import USER_INFO, TICKET_PREFERENCES, BOT_SETTINGS, URLS, TIMEOUTS
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, YOUR_PHONE_NUMBERS


class RCBBookingBot:
    def __init__(self):
        """Initialize the booking bot"""
        self.driver = None
        self.screenshots_dir = "bot_screenshots"
        self.step_counter = 0
        self.booked_stand = None  # Track which stand was successfully booked
        self.seat_selection_attempts = 0  # Track attempts for fallback strategy

        # Create screenshots directory
        os.makedirs(self.screenshots_dir, exist_ok=True)

        # Session management (cookies for login persistence)
        self.cookies_file = "rcb_session_cookies.pkl"

        print("="*70)
        print("  RCB TICKET BOOKING BOT")
        print("="*70)
        print(f"Match: {TICKET_PREFERENCES['match_name']}")

        # Show booking mode
        stand_preferences = TICKET_PREFERENCES.get('stand_preferences')
        if stand_preferences and isinstance(stand_preferences, list) and len(stand_preferences) > 0:
            print(f"Mode: Multi-Stand (Preferences: {len(stand_preferences)})")
            for i, stand in enumerate(stand_preferences, 1):
                print(f"  {i}. {stand}")
        else:
            print(f"Mode: Single-Stand")
            print(f"Target Stand: {TICKET_PREFERENCES['target_stand']}")

        print(f"Number of Seats: {TICKET_PREFERENCES['num_seats']}")
        print(f"User: {USER_INFO['first_name']} {USER_INFO['last_name']}")
        print("="*70)
        print()

    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        sys.stdout.flush()

    def send_sms_notification(self, message):
        """Send SMS notification via Twilio"""
        try:
            self.log("Sending SMS notifications...")
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            for phone_number in YOUR_PHONE_NUMBERS:
                try:
                    sms = client.messages.create(
                        body=message,
                        from_=TWILIO_PHONE_NUMBER,
                        to=phone_number
                    )
                    self.log(f"SMS sent to {phone_number}: {sms.sid}")
                except Exception as e:
                    self.log(f"Failed to send SMS to {phone_number}: {e}", "ERROR")

            return True
        except Exception as e:
            self.log(f"Error sending SMS: {e}", "ERROR")
            return False

    def save_cookies(self):
        """Save session cookies to file"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            self.log(f"Session cookies saved to {self.cookies_file}")
            return True
        except Exception as e:
            self.log(f"Error saving cookies: {e}", "WARNING")
            return False

    def load_cookies(self):
        """Load session cookies from file"""
        try:
            if not os.path.exists(self.cookies_file):
                self.log("No saved session found")
                return False

            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)

            # Navigate to base URL first (required before adding cookies)
            self.driver.get(URLS["base"])
            time.sleep(2)

            # Add each cookie
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.log(f"Could not add cookie: {e}", "WARNING")

            self.log(f"Loaded {len(cookies)} cookies from saved session")
            return True
        except Exception as e:
            self.log(f"Error loading cookies: {e}", "WARNING")
            return False

    def check_login_status(self):
        """Check if currently logged in"""
        try:
            # Navigate to tickets page to check login
            self.driver.get(URLS["tickets"])
            time.sleep(3)

            # If redirected to /auth, not logged in
            if "/auth" in self.driver.current_url:
                self.log("Not logged in (redirected to /auth)")
                return False

            # If on /ticket page, logged in
            if "/ticket" in self.driver.current_url:
                self.log("Already logged in!")
                return True

            return False
        except Exception as e:
            self.log(f"Error checking login status: {e}", "WARNING")
            return False

    def take_screenshot(self, name):
        """Take screenshot at current step"""
        if not BOT_SETTINGS["screenshot_each_step"]:
            return

        try:
            self.step_counter += 1
            filename = f"{self.screenshots_dir}/step{self.step_counter:02d}_{name}.png"
            self.driver.save_screenshot(filename)
            self.log(f"Screenshot saved: {filename}")
        except Exception as e:
            self.log(f"Could not save screenshot: {e}", "WARNING")

    def setup_driver(self):
        """Setup Firefox driver for Windows"""
        try:
            # Install geckodriver automatically
            geckodriver_autoinstaller.install()

            firefox_options = Options()

            if BOT_SETTINGS["headless"]:
                firefox_options.add_argument('--headless')

            # Firefox preferences for better performance
            firefox_options.set_preference('dom.webdriver.enabled', False)
            firefox_options.set_preference('useAutomationExtension', False)
            firefox_options.set_preference('general.useragent.override',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0')

            # WINDOWS FIX: Retry logic for WebDriver initialization
            max_retries = 3
            last_error = None

            for attempt in range(max_retries):
                try:
                    self.log(f"Initializing Firefox WebDriver (attempt {attempt + 1}/{max_retries})...")

                    self.driver = webdriver.Firefox(options=firefox_options)

                    # Set increased timeouts for Windows (multiply by 2)
                    page_timeout = TIMEOUTS.get("page_load", 30) * 2  # Double the timeout
                    self.driver.set_page_load_timeout(page_timeout)
                    self.driver.set_script_timeout(60)

                    # Test connection
                    self.driver.get("about:blank")

                    self.log("Firefox driver initialized successfully (Windows)")
                    return True

                except Exception as e:
                    last_error = e
                    self.log(f"Firefox init attempt {attempt + 1} failed: {e}", "WARNING")

                    # Close driver if partially initialized
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None

                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5  # 5, 10 seconds
                        self.log(f"Waiting {wait_time}s before retry...", "INFO")
                        time.sleep(wait_time)
                    else:
                        raise last_error

            return False

        except Exception as e:
            self.log(f"Error setting up Firefox WebDriver: {e}", "ERROR")
            self.log("Try: 1) Restart script, 2) Check Windows Firewall, 3) Disable antivirus temporarily", "ERROR")
            return False

    def wait_for_element(self, by, value, timeout=None):
        """Wait for element to be present"""
        if timeout is None:
            timeout = TIMEOUTS["element_wait"]

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.log(f"Timeout waiting for element: {value}", "WARNING")
            return None

    def wait_for_clickable(self, by, value, timeout=None):
        """Wait for element to be clickable"""
        if timeout is None:
            timeout = TIMEOUTS["element_wait"]

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            self.log(f"Timeout waiting for clickable element: {value}", "WARNING")
            return None

    def safe_click(self, element, description=""):
        """Safely click element with fallback to JS click"""
        try:
            element.click()
            self.log(f"Clicked: {description}")
            return True
        except Exception as e:
            self.log(f"Regular click failed, trying JS click: {e}", "WARNING")
            try:
                self.driver.execute_script("arguments[0].click();", element)
                self.log(f"JS Click succeeded: {description}")
                return True
            except Exception as e2:
                self.log(f"JS click also failed: {e2}", "ERROR")
                return False

    # ===== STEP 1: LOAD SAVED SESSION =====
    def login(self, mobile_number=None):
        """Load saved session cookies if available (no verification)"""
        if mobile_number is None:
            mobile_number = USER_INFO["mobile"]

        self.log("STEP 1: CHECK FOR SAVED SESSION")
        self.log("-" * 50)

        try:
            # Try to load saved session cookies
            if self.load_cookies():
                self.log("✅ Loaded saved session cookies")
                self.log("Will verify session validity when clicking BUY TICKETS")
            else:
                self.log("ℹ️  No saved session (clean start)")
                self.log("Will login fresh when clicking BUY TICKETS")

            # Always return True - Step 2 will handle login if needed
            return True

        except Exception as e:
            self.log(f"Error loading session: {e}", "WARNING")
            # Not critical - Step 2 will handle login
            return True

    # ===== STEP 2: BUY TICKETS =====
    def click_buy_tickets(self):
        """Click BUY TICKETS button for specific match"""
        self.log("\nSTEP 2: CLICK BUY TICKETS")
        self.log("-" * 50)

        try:
            # Navigate to tickets listing page if not already there
            if self.driver.current_url != URLS["tickets"]:
                self.log("Navigating to tickets page...")
                self.driver.get(URLS["tickets"])
                time.sleep(3)

            self.take_screenshot("05_tickets_page")

            # Find BUY TICKETS button matching the team name
            match_name = TICKET_PREFERENCES['match_name']
            self.log(f"Looking for match: {match_name}")

            # First, try to find the match by name
            match_found = False
            match_element = None

            # Try to find elements containing the match name
            try:
                match_elements = self.driver.find_elements(By.XPATH,
                    f"//*[contains(text(), 'Royal Challengers') and contains(text(), 'Sunrisers')]")
                if match_elements:
                    match_element = match_elements[0]
                    match_found = True
                    self.log(f"✅ Found match element on page")
            except:
                pass

            # Find all BUY TICKETS buttons
            buy_buttons = self.driver.find_elements(By.XPATH,
                "//button[contains(text(), 'BUY TICKETS') or contains(text(), 'Buy Tickets')]")

            self.log(f"Found {len(buy_buttons)} BUY TICKETS button(s)")

            if len(buy_buttons) == 0:
                self.log("No BUY TICKETS buttons found", "ERROR")
                return False

            # Select which button to click
            buy_btn = None
            if len(buy_buttons) == 1:
                # Only one match - click it
                buy_btn = buy_buttons[0]
                self.log("Only 1 match available - clicking BUY TICKETS")
            elif match_found and match_element:
                # Multiple matches - find button closest to our match
                self.log("Multiple matches - finding button for our match...")
                # For now, click first button (can enhance to check proximity)
                buy_btn = buy_buttons[0]
                self.log("Using first BUY TICKETS button")
            else:
                # Fallback - click first
                buy_btn = buy_buttons[0]
                self.log("Using first BUY TICKETS button")

            # Click the button
            self.driver.execute_script("arguments[0].click();", buy_btn)
            self.log(f"Clicked BUY TICKETS")
            time.sleep(3)
            self.take_screenshot("06_after_buy_click")

            # Check if we got redirected to login
            current_url = self.driver.current_url
            self.log(f"After clicking BUY TICKETS, current URL: {current_url}")

            # If redirected to login, handle it
            if "/auth" in current_url or "LOGIN" in self.driver.page_source:
                self.log("⚠️  Redirected to login after clicking BUY TICKETS - logging in...")

                # Enter mobile number
                mobile_input = self.wait_for_element(By.XPATH, "//input[@type='tel' or contains(@placeholder, 'Mobile')]", timeout=5)
                if mobile_input:
                    mobile_input.clear()
                    mobile_input.send_keys(USER_INFO['mobile'])
                    self.take_screenshot("06b_mobile_entered")

                    # Click Continue button using JS
                    continue_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
                    self.driver.execute_script("arguments[0].click();", continue_btn)
                    self.log("Clicked Continue for OTP")
                    time.sleep(2)
                    self.take_screenshot("06c_otp_screen")

                    # Wait for OTP entry
                    self.log("=" * 70)
                    self.log("📱 OTP REQUIRED!")
                    self.log("Please enter OTP in the browser window...")
                    self.log("=" * 70)

                    # Monitor for successful login (check for stand selection page)
                    for i in range(120):  # 2 minutes max
                        time.sleep(1)
                        page_source = self.driver.page_source

                        if "SELECT CATEGORY" in page_source or "CATEGORY" in page_source:
                            self.log("✅ Login successful - on stand selection page!")
                            self.save_cookies()
                            return True

                        if i % 30 == 0 and i > 0:
                            self.log(f"Waiting for OTP entry... ({i}s)")

                    self.log("Timeout waiting for OTP", "ERROR")
                    return False

            return True

        except Exception as e:
            self.log(f"Error clicking buy tickets: {e}", "ERROR")
            traceback.print_exc()
            return False

    # ===== STEP 3: HANDLE POPUP =====
    def handle_important_info_popup(self):
        """Handle 'Important Information' popup with Continue button"""
        self.log("\nSTEP 3: HANDLE IMPORTANT INFO POPUP")
        self.log("-" * 50)

        try:
            # Look for popup with "Important Information" or "Continue" button
            time.sleep(2)
            self.take_screenshot("07_popup_check")

            # Try to find Continue button in popup
            continue_btn = self.wait_for_clickable(By.XPATH,
                "//button[contains(text(), 'Continue') or contains(text(), 'CONTINUE')]",
                timeout=5)

            if continue_btn:
                self.log("Found Important Information popup")
                self.safe_click(continue_btn, "Continue button in popup")
                time.sleep(2)
                self.take_screenshot("08_popup_closed")
                return True
            else:
                self.log("No popup found or already closed")
                return True

        except Exception as e:
            self.log(f"Error handling popup: {e}", "WARNING")
            # Not critical - might not always appear
            return True

    # ===== STEP 4: SELECT STAND =====
    def select_stand(self, stand_name=None):
        """Click on stand from category list"""
        if stand_name is None:
            stand_name = TICKET_PREFERENCES["target_stand"]

        self.log(f"\nSTEP 4: SELECT STAND - {stand_name}")
        self.log("-" * 50)

        try:
            time.sleep(0.5)
            self.take_screenshot("09_stand_selection_page")

            # Find stand in category list (left panel)
            # Try multiple selectors - category list elements can be tricky
            selectors = [
                # Try exact match
                f"//p[text()='{stand_name}']",
                f"//div[text()='{stand_name}']",
                # Try contains
                f"//p[contains(text(), '{stand_name}')]",
                f"//*[contains(text(), '{stand_name}')]",
                # Try normalized text
                f"//*[normalize-space(text())='{stand_name}']",
            ]

            stand_element = None
            for i, selector in enumerate(selectors):
                try:
                    self.log(f"Trying selector {i+1}: {selector[:70]}...")
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.log(f"Found {len(elements)} elements")

                    for elem in elements:
                        if elem.is_displayed():
                            stand_element = elem
                            self.log(f"✅ Found visible stand element!")
                            break

                    if stand_element:
                        break

                except Exception as e:
                    self.log(f"Selector {i+1} error: {e}", "DEBUG")
                    continue

            if not stand_element:
                self.log(f"Could not find {stand_name} in category list", "ERROR")
                self.take_screenshot("ERROR_stand_not_found")
                return False

            # Scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", stand_element)
            time.sleep(0.3)

            # Click stand and retry if "Seats Are Being Taken" error appears
            max_retries = 50  # Try up to 50 times
            retry_count = 0

            while retry_count < max_retries:
                retry_count += 1
                self.log(f"Attempting to select stand (attempt {retry_count}/{max_retries})...")

                # Click the stand element
                self.safe_click(stand_element, f"{stand_name} category")
                time.sleep(0.5)

                # Check for "Seats Are Being Taken" error popup
                try:
                    error_popup = self.driver.find_elements(By.XPATH,
                        "//*[contains(text(), 'Seats Are Being Taken') or contains(text(), 'seats are being booked')]")

                    if error_popup and len(error_popup) > 0:
                        self.log(f"⚠️  'Seats Being Taken' error appeared - retrying...", "WARNING")
                        self.take_screenshot(f"10_error_attempt_{retry_count}")

                        # Close the error popup (find X button or close button)
                        close_selectors = [
                            "//button[contains(@aria-label, 'close') or contains(@class, 'close')]",
                            "//*[@aria-label='Close']",
                            "//button[text()='×' or text()='X']",
                            "//*[name()='svg' and contains(@class, 'close')]",
                        ]

                        closed = False
                        for close_sel in close_selectors:
                            try:
                                close_btn = self.driver.find_element(By.XPATH, close_sel)
                                if close_btn.is_displayed():
                                    self.safe_click(close_btn, "Close error popup")
                                    closed = True
                                    break
                            except:
                                continue

                        if not closed:
                            self.log("Could not find close button, pressing ESC", "WARNING")
                            from selenium.webdriver.common.keys import Keys
                            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)

                        time.sleep(0.2)  # Brief pause before retry
                        continue
                    else:
                        # No error popup - success!
                        self.log(f"✅ Successfully selected stand on attempt {retry_count}!")
                        self.take_screenshot("10_stand_clicked_success")
                        return True

                except Exception as e:
                    # If we can't check for error, assume success and continue
                    self.log(f"No error detected on attempt {retry_count} - proceeding")
                    self.take_screenshot("10_stand_clicked")
                    return True

            # If we exhausted all retries
            self.log(f"Failed to select stand after {max_retries} attempts", "ERROR")
            return False

        except Exception as e:
            self.log(f"Error selecting stand: {e}", "ERROR")
            traceback.print_exc()
            return False

    # ===== STEP 5: SELECT SEATS =====
    def parse_seat_label(self, seat_element):
        """
        Extract row series (letter) and seat number from seat element
        Returns: (row_letter, seat_number, seat_element)
        Example: "K25" -> ('K', 25, element)
        """
        try:
            # Try to get seat label from various attributes
            seat_label = None

            # Try aria-label
            aria_label = seat_element.get_attribute('aria-label')
            if aria_label:
                seat_label = aria_label

            # Try data attributes
            if not seat_label:
                seat_label = seat_element.get_attribute('data-seat-id') or \
                            seat_element.get_attribute('data-seat-label') or \
                            seat_element.get_attribute('id') or \
                            seat_element.text

            if not seat_label:
                return (None, None, seat_element)

            # Parse label - common formats: "K25", "Row K Seat 25", "K-25"
            import re
            # Look for letter followed by number
            match = re.search(r'([A-Z])[\s\-]*(\d+)', seat_label.upper())
            if match:
                row_letter = match.group(1)
                seat_number = int(match.group(2))
                return (row_letter, seat_number, seat_element)

            return (None, None, seat_element)

        except Exception as e:
            return (None, None, seat_element)

    def get_seat_preference_score(self, row_letter, seat_number, current_stand, relaxed_mode=False):
        """
        Calculate preference score for a seat (higher = better)
        Based on stand-specific preferences

        relaxed_mode: If True, accept any seat (fallback after multiple retries)
        """
        if not row_letter:
            return 0  # Unknown seat, lowest priority

        score = 0

        # Determine stand type for preference rules
        stand_upper = current_stand.upper()

        # RELAXED MODE: After multiple failed attempts, accept ANY seat
        if relaxed_mode:
            self.log("🔄 Relaxed mode: Accepting any available seats", "WARNING")
            # Still prefer better rows, but don't exclude any
            score += (ord(row_letter) - ord('A')) * 10

        # STRICT MODE: Prefer specific rows
        elif "PUMA" in stand_upper or "BOAT C" in stand_upper:
            # Row preference: K-Z (higher priority)
            if row_letter >= 'K':
                score += 1000  # High priority for K-Z rows
                # Within K-Z, prefer middle letters (around M-P)
                distance_from_middle = abs(ord(row_letter) - ord('M'))
                score += (26 - distance_from_middle) * 10
            else:
                # A-J rows are lower priority but still acceptable
                score += ord(row_letter) - ord('A')

        # SUN PHARMA A STAND - prefer row A first, then B-Z
        elif "SUN PHARMA A" in stand_upper:
            if row_letter == 'A':
                score += 2000  # Highest priority for row A
            else:
                # B-Z rows, ordered by letter
                score += 1000 + (ord(row_letter) - ord('B'))

        else:
            # Default: prefer later rows (better view typically)
            score += (ord(row_letter) - ord('A')) * 10

        # Seat number preference: middle seats are best
        # We'll add bonus for seats that are more "middle"
        # (Actual middle calculation will be done after we know min/max seat numbers)
        # For now, just store the seat number for later sorting
        score += seat_number * 0.01  # Small weight for seat number

        return score

    def select_best_seats(self, available_seats, current_stand, num_seats, relaxed_mode=False):
        """
        Select best seats based on row and position preferences

        relaxed_mode: If True, accept any seats (fallback strategy)
        """
        # Parse all seats
        parsed_seats = []
        for seat in available_seats:
            row, number, element = self.parse_seat_label(seat)
            if row or number:  # Keep seats with at least some info
                parsed_seats.append({
                    'row': row,
                    'number': number,
                    'element': element,
                    'score': self.get_seat_preference_score(row, number, current_stand, relaxed_mode)
                })
            else:
                # Unknown seat format - add with low score
                parsed_seats.append({
                    'row': None,
                    'number': None,
                    'element': element,
                    'score': 0
                })

        if not parsed_seats:
            return []

        # Determine stand type for seat number preferences
        stand_upper = current_stand.upper()
        is_sun_pharma_a = "SUN PHARMA A" in stand_upper

        # Find min/max seat numbers
        seat_numbers = [s['number'] for s in parsed_seats if s['number']]
        if seat_numbers:
            min_seat = min(seat_numbers)
            max_seat = max(seat_numbers)
            middle_seat = (min_seat + max_seat) / 2

            # Adjust scores based on stand-specific seat number preferences
            for seat in parsed_seats:
                if seat['number']:
                    if is_sun_pharma_a:
                        # SUN PHARMA A: Prefer FRONT seats (1-20)
                        # Lower seat number = higher score
                        if seat['number'] <= 20:
                            # Seats 1-20: Very high bonus
                            seat['score'] += (200 - seat['number'] * 5)
                        else:
                            # Seats 21+: Lower priority
                            seat['score'] += (100 - seat['number'])
                    else:
                        # PUMA B / BOAT C: Prefer MIDDLE seats
                        distance_from_middle = abs(seat['number'] - middle_seat)
                        # Closer to middle = higher score
                        seat['score'] += (100 - distance_from_middle)

        # Sort by score (descending - highest score first)
        parsed_seats.sort(key=lambda x: x['score'], reverse=True)

        # Log top preferences
        if is_sun_pharma_a:
            self.log(f"🎯 Smart seat selection for {current_stand} (prefer Row A, seats 1-20):")
        else:
            self.log(f"🎯 Smart seat selection for {current_stand} (prefer rows K-Z, middle seats):")

        for i, seat in enumerate(parsed_seats[:5]):
            if seat['row'] and seat['number']:
                self.log(f"  #{i+1}: Row {seat['row']}, Seat {seat['number']} (score: {seat['score']:.0f})")

        # Return best N seats
        return [s['element'] for s in parsed_seats[:num_seats]]

    def select_seats(self, num_seats=None, current_stand=None):
        """Select best available seats based on preferences"""
        if num_seats is None:
            num_seats = TICKET_PREFERENCES["num_seats"]

        if current_stand is None:
            current_stand = self.booked_stand or TICKET_PREFERENCES.get('target_stand', '')

        self.log(f"\nSTEP 5: SELECT {num_seats} SEATS")
        self.log("-" * 50)

        # Track seat selection attempts for fallback strategy
        self.seat_selection_attempts += 1

        # Accept ANY seats immediately (was 20, set to 1 for immediate fallback)
        RELAXED_MODE_THRESHOLD = 1
        relaxed_mode = self.seat_selection_attempts >= RELAXED_MODE_THRESHOLD

        if relaxed_mode:
            self.log("=" * 60, "WARNING")
            self.log(f"⚠️  FALLBACK MODE ACTIVATED (attempt {self.seat_selection_attempts})", "WARNING")
            self.log("Accepting ANY available seats to secure tickets!", "WARNING")
            self.log("=" * 60, "WARNING")
        elif self.seat_selection_attempts > 10:
            self.log(f"ℹ️  Attempt {self.seat_selection_attempts} - will fallback to any seats after {RELAXED_MODE_THRESHOLD} attempts", "INFO")

        try:
            time.sleep(0.5)
            self.take_screenshot("11_seat_selection_page")

            # Look for available seats - try multiple selectors
            seat_selectors = [
                "//div[contains(@class, 'available')]",
                "//*[@aria-label='Available seat' or @aria-label='Available']",
                "//div[contains(@class, 'seat') and not(contains(@class, 'unavailable')) and not(contains(@class, 'booked'))]",
                "//button[contains(@class, 'seat') and not(contains(@class, 'unavailable'))]",
                "//div[contains(@class, 'seat-available')]",
                "//*[contains(@class, 'available-seat')]",
            ]

            available_seats = []
            for selector in seat_selectors:
                try:
                    seats = self.driver.find_elements(By.XPATH, selector)
                    if seats and len(seats) > 0:
                        self.log(f"Found {len(seats)} available seats using selector: {selector[:50]}...")
                        available_seats = seats
                        break
                except:
                    continue

            if len(available_seats) < num_seats:
                self.log(f"Only {len(available_seats)} seats available, need {num_seats}", "WARNING")
                if len(available_seats) == 0:
                    # Try one more desperate attempt - find ANY clickable elements that might be seats
                    self.log("Trying to find any clickable seat elements...", "WARNING")
                    try:
                        all_clickable = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'seat')]")
                        available_seats = [s for s in all_clickable if s.is_displayed() and s.is_enabled()]
                        self.log(f"Found {len(available_seats)} potentially clickable seats")
                    except:
                        pass

                    if len(available_seats) == 0:
                        return False

            # Select best seats using smart selection (with fallback if needed)
            best_seats = self.select_best_seats(available_seats, current_stand, num_seats, relaxed_mode)

            # If smart selection returned nothing, just take the first available seats
            if not best_seats or len(best_seats) == 0:
                self.log("Smart selection failed, using first available seats", "WARNING")
                best_seats = available_seats[:num_seats]

            # Click selected seats
            seats_selected = 0
            for i, seat in enumerate(best_seats):
                try:
                    self.log(f"Clicking seat {i+1}/{num_seats}")
                    self.safe_click(seat, f"Seat {i+1}")
                    seats_selected += 1
                    time.sleep(0.1)
                except Exception as e:
                    self.log(f"Could not click seat {i+1}: {e}", "WARNING")

            if seats_selected < num_seats:
                self.log(f"Only selected {seats_selected}/{num_seats} seats", "WARNING")

            time.sleep(0.3)
            self.take_screenshot("12_seats_selected")

            # Click Proceed button
            self.log("Looking for Proceed button...")
            proceed_btn = self.wait_for_clickable(By.XPATH,
                "//button[contains(translate(text(), 'PROCEED', 'proceed'), 'proceed')]")

            if not proceed_btn:
                self.log("Could not find Proceed button", "ERROR")
                return False

            self.safe_click(proceed_btn, "Proceed button")
            time.sleep(0.5)
            self.take_screenshot("13_after_proceed")

            # Check if proceed failed and we got kicked back to stand selection
            # Look for "Seats Are Being Taken" error or if we're back on stand selection page
            try:
                error_elements = self.driver.find_elements(By.XPATH,
                    "//*[contains(text(), 'Seats Are Being Taken') or contains(text(), 'seats are being booked')]")

                if error_elements and len(error_elements) > 0:
                    self.log("⚠️  Proceed failed - 'Seats Being Taken' error detected!", "WARNING")
                    return False

                # Check if URL indicates we're back on stand selection
                current_url = self.driver.current_url
                if "ticket/1" in current_url and "checkout" not in current_url:
                    # We might be back on stand selection - check page content
                    page_source = self.driver.page_source
                    if "SELECT CATEGORY" in page_source or "CATEGORY" in page_source:
                        self.log("⚠️  Proceed failed - redirected back to stand selection", "WARNING")
                        return False

            except Exception as e:
                self.log(f"Error checking proceed status: {e}", "DEBUG")

            # If no error detected, assume success
            self.log("✅ Proceed button successful!")
            return True

        except Exception as e:
            self.log(f"Error selecting seats: {e}", "ERROR")
            traceback.print_exc()
            return False

    # ===== STEP 6: HANDLE PARKING/METRO POPUP =====
    def handle_parking_metro_popup(self):
        """Select Free Metro Ticket or Paid Parking"""
        choice = TICKET_PREFERENCES["metro_or_parking"]

        self.log(f"\nSTEP 6: HANDLE PARKING/METRO POPUP - {choice.upper()}")
        self.log("-" * 50)

        try:
            time.sleep(2)
            self.take_screenshot("14_parking_metro_popup")

            # Look for metro or parking radio button
            if choice == "metro":
                radio_selectors = [
                    "//input[@value='Free Metro Ticket' or contains(@id, 'metro')]",
                    "//*[contains(text(), 'Free Metro Ticket')]",
                ]
            else:
                radio_selectors = [
                    "//input[@value='Paid Parking' or contains(@id, 'parking')]",
                    "//*[contains(text(), 'Paid Parking')]",
                ]

            # Try to find and click radio button
            radio_clicked = False
            for selector in radio_selectors:
                try:
                    radio = self.wait_for_element(By.XPATH, selector, timeout=5)
                    if radio:
                        self.safe_click(radio, f"{choice.capitalize()} option")
                        radio_clicked = True
                        break
                except:
                    continue

            if not radio_clicked:
                self.log(f"Could not find {choice} option, trying to continue anyway", "WARNING")

            time.sleep(1)

            # Click Continue button in popup
            continue_btn = self.wait_for_clickable(By.XPATH,
                "//button[contains(text(), 'Continue') or contains(text(), 'CONTINUE')]")

            if not continue_btn:
                self.log("Could not find Continue button in popup", "ERROR")
                return False

            self.safe_click(continue_btn, "Continue button")
            time.sleep(3)
            self.take_screenshot("15_popup_closed")

            return True

        except Exception as e:
            self.log(f"Error handling parking/metro popup: {e}", "ERROR")
            traceback.print_exc()
            return False

    # ===== STEP 7: FILL CHECKOUT FORM =====
    def fill_checkout_form(self):
        """Fill personal details in checkout form"""
        self.log("\nSTEP 7: FILL CHECKOUT FORM")
        self.log("-" * 50)

        try:
            time.sleep(3)
            self.take_screenshot("16_checkout_page")

            # Verify we're on checkout page
            if "/checkout" not in self.driver.current_url:
                self.log(f"Not on checkout page! Current: {self.driver.current_url}", "WARNING")

            # Fill First Name
            self.log(f"Entering first name: {USER_INFO['first_name']}")
            first_name_input = self.wait_for_element(By.XPATH,
                "//input[@name='firstName' or contains(@placeholder, 'First name') or contains(@id, 'first')]")
            if first_name_input:
                first_name_input.clear()
                first_name_input.send_keys(USER_INFO['first_name'])

            time.sleep(0.5)

            # Fill Last Name
            self.log(f"Entering last name: {USER_INFO['last_name']}")
            last_name_input = self.wait_for_element(By.XPATH,
                "//input[@name='lastName' or contains(@placeholder, 'Last') or contains(@id, 'last')]")
            if last_name_input:
                last_name_input.clear()
                last_name_input.send_keys(USER_INFO['last_name'])

            time.sleep(0.5)

            # Fill Mobile (might be pre-filled)
            self.log(f"Entering mobile: {USER_INFO['mobile']}")
            mobile_input = self.wait_for_element(By.XPATH,
                "//input[@name='mobile' or @type='tel' or contains(@placeholder, 'Mobile') or contains(@placeholder, 'mobi')]")
            if mobile_input:
                mobile_input.clear()
                mobile_input.send_keys(USER_INFO['mobile'])

            time.sleep(0.5)

            # Fill Email
            self.log(f"Entering email: {USER_INFO['email']}")
            email_input = self.wait_for_element(By.XPATH,
                "//input[@name='email' or @type='email' or contains(@placeholder, 'Email') or contains(@placeholder, 'email')]")
            if email_input:
                email_input.clear()
                email_input.send_keys(USER_INFO['email'])

            time.sleep(0.5)

            # Select Gender
            self.log(f"Selecting gender: {USER_INFO['gender']}")
            try:
                gender_radio = self.wait_for_element(By.XPATH,
                    f"//input[@value='{USER_INFO['gender']}' or @id='{USER_INFO['gender'].lower()}']")
                if gender_radio:
                    self.safe_click(gender_radio, f"Gender: {USER_INFO['gender']}")
            except:
                self.log("Could not select gender", "WARNING")

            time.sleep(1)
            self.take_screenshot("17_form_filled")

            # Check T&C checkboxes
            self.log("Checking T&C checkboxes...")
            checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            self.log(f"Found {len(checkboxes)} checkboxes")

            for i, checkbox in enumerate(checkboxes):
                try:
                    if not checkbox.is_selected():
                        self.safe_click(checkbox, f"Checkbox {i+1}")
                        time.sleep(0.3)
                except Exception as e:
                    self.log(f"Could not check checkbox {i+1}: {e}", "WARNING")

            time.sleep(1)
            self.take_screenshot("18_checkboxes_checked")

            # Click PAY NOW button
            self.log("Looking for PAY NOW button...")
            pay_now_btn = self.wait_for_clickable(By.XPATH,
                "//button[contains(text(), 'PAY NOW') or contains(text(), 'Pay Now')]")

            if not pay_now_btn:
                self.log("Could not find PAY NOW button", "ERROR")
                return False

            self.safe_click(pay_now_btn, "PAY NOW button")
            time.sleep(5)  # Wait for payment page to load
            self.take_screenshot("19_payment_loading")

            return True

        except Exception as e:
            self.log(f"Error filling checkout form: {e}", "ERROR")
            traceback.print_exc()
            return False

    # ===== STEP 8: PAYMENT =====
    def handle_payment(self):
        """Select UPI and enter UPI ID"""
        self.log("\nSTEP 8: PAYMENT - UPI")
        self.log("-" * 50)

        try:
            # Wait for payment page to load (Juspay)
            time.sleep(5)
            self.take_screenshot("20_payment_page")

            self.log(f"Current URL: {self.driver.current_url}")

            # Click UPI option
            self.log("Selecting UPI payment method...")
            upi_option = self.wait_for_clickable(By.XPATH,
                "//div[contains(text(), 'UPI') or contains(@id, 'upi')]", timeout=15)

            if not upi_option:
                self.log("Could not find UPI option", "ERROR")
                return False

            self.safe_click(upi_option, "UPI payment option")
            time.sleep(2)
            self.take_screenshot("21_upi_selected")

            # Enter UPI ID
            self.log(f"Entering UPI ID: {USER_INFO['upi_id']}")
            upi_input = self.wait_for_element(By.XPATH,
                "//input[@placeholder='Username@bankname' or contains(@name, 'vpa') or contains(@placeholder, 'UPI')]")

            if not upi_input:
                self.log("Could not find UPI input field", "ERROR")
                return False

            upi_input.clear()
            upi_input.send_keys(USER_INFO['upi_id'])
            time.sleep(1)
            self.take_screenshot("22_upi_entered")

            # Click VERIFY AND PAY button
            self.log("Looking for VERIFY AND PAY button...")
            verify_btn = self.wait_for_clickable(By.XPATH,
                "//button[contains(text(), 'VERIFY AND PAY') or contains(text(), 'Verify and Pay')]")

            if not verify_btn:
                self.log("Could not find VERIFY AND PAY button", "ERROR")
                return False

            self.safe_click(verify_btn, "VERIFY AND PAY button")
            time.sleep(3)
            self.take_screenshot("23_payment_initiated")

            # STOP HERE - User completes payment manually
            self.log("=" * 70)
            self.log("✅ PAYMENT INITIATED SUCCESSFULLY!")
            self.log("=" * 70)
            self.log("📱 Please complete the UPI payment on your phone")
            self.log("💳 You will receive a payment request notification")
            self.log("⏰ Complete payment within the timer shown on screen")
            self.log("=" * 70)
            self.log("\n🎉 BOT HAS COMPLETED ALL AUTOMATED STEPS!")
            self.log("=" * 70)

            # Monitor for payment confirmation
            self.log("\nMonitoring for payment confirmation...")
            self.log("Waiting for payment to complete (checking every 5 seconds)...")

            confirmation_detected = False
            max_wait_time = TIMEOUTS["payment_timer"]  # 6 minutes
            check_interval = 5
            elapsed_time = 0

            try:
                while elapsed_time < max_wait_time:
                    time.sleep(check_interval)
                    elapsed_time += check_interval

                    # Take periodic screenshots
                    if elapsed_time % 30 == 0:
                        self.take_screenshot(f"24_payment_monitoring_{elapsed_time}s")

                    # Check for success indicators on page
                    page_source = self.driver.page_source.lower()

                    # Success indicators based on actual confirmation page
                    success_patterns = [
                        "thank you for shopping" in page_source,
                        "order has been completed successfully" in page_source,
                        "order no." in page_source or "order no:" in page_source,
                        "success" in page_source and ("payment" in page_source or "order" in page_source),
                        "confirmed" in page_source,
                        "booking confirmed" in page_source,
                    ]

                    # Check for success messages on page
                    try:
                        success_elements = self.driver.find_elements(By.XPATH,
                            "//*[contains(translate(text(), 'SUCCESS', 'success'), 'success') or "
                            "contains(translate(text(), 'CONFIRMED', 'confirmed'), 'confirmed') or "
                            "contains(translate(text(), 'BOOKING', 'booking'), 'booking')]")

                        if success_elements and len(success_elements) > 0:
                            success_patterns.append(True)
                    except:
                        pass

                    if any(success_patterns):
                        confirmation_detected = True
                        self.log("=" * 70)
                        self.log("🎉 PAYMENT CONFIRMED!")
                        self.log("=" * 70)
                        self.take_screenshot("25_payment_confirmed")

                        # Send SMS notification
                        stand_info = self.booked_stand if self.booked_stand else "tickets"
                        sms_message = f"🎉 RCB TICKET BOOKING SUCCESSFUL!\n\nYour {stand_info} tickets have been confirmed!\nCheck your email: {USER_INFO['email']}\n\nBooking completed at {datetime.now().strftime('%I:%M %p')}"
                        self.send_sms_notification(sms_message)

                        self.log("✅ Confirmation SMS sent!")
                        self.log("✅ Check your email for ticket details")
                        self.log("=" * 70)
                        break

                    # Log progress
                    if elapsed_time % 30 == 0:
                        remaining = max_wait_time - elapsed_time
                        self.log(f"Still monitoring... ({remaining}s remaining)")

            except KeyboardInterrupt:
                self.log("\n⚠️  Monitoring interrupted by user")
                confirmation_detected = False

            if not confirmation_detected:
                self.log("=" * 70)
                self.log("⚠️  Could not detect payment confirmation automatically")
                self.log("Please check your email and 'My Tickets' section manually")
                self.log("=" * 70)

            # Keep browser open for review
            self.log("\nKeeping browser open for 30 seconds for review...")
            self.log("Press Ctrl+C to close immediately")

            try:
                time.sleep(30)
            except KeyboardInterrupt:
                pass

            return True

        except Exception as e:
            self.log(f"Error handling payment: {e}", "ERROR")
            traceback.print_exc()
            return False

    # ===== MAIN BOOKING FLOW =====
    def book_tickets(self):
        """Complete end-to-end booking flow"""
        try:
            # Setup driver
            if not self.setup_driver():
                return False

            # Step 1: Login
            if not self.login():
                self.log("Login failed", "ERROR")
                return False

            # Step 2: Click Buy Tickets
            if not self.click_buy_tickets():
                self.log("Failed to click buy tickets", "ERROR")
                return False

            # Step 3: Handle popup
            if not self.handle_important_info_popup():
                self.log("Failed to handle popup", "ERROR")
                return False

            # Determine booking mode: Single stand or Multi-stand
            stand_preferences = TICKET_PREFERENCES.get('stand_preferences')

            if stand_preferences and isinstance(stand_preferences, list) and len(stand_preferences) > 0:
                # MULTI-STAND MODE
                stands_to_try = stand_preferences
                mode = "MULTI-STAND"
                self.log("=" * 70)
                self.log("🎯 MULTI-STAND MODE ACTIVATED")
                self.log(f"Will try stands in preference order:")
                for i, stand in enumerate(stands_to_try, 1):
                    self.log(f"  {i}. {stand}")
                self.log("=" * 70)
            else:
                # SINGLE STAND MODE (backward compatible)
                stands_to_try = [TICKET_PREFERENCES['target_stand']]
                mode = "SINGLE-STAND"
                self.log("=" * 70)
                self.log(f"🎯 SINGLE-STAND MODE: {stands_to_try[0]}")
                self.log("=" * 70)

            # Steps 4-6: Seat booking loop (retry if proceed fails)
            max_seat_booking_attempts = 100  # Try booking up to 100 times
            seat_booking_attempt = 0
            seat_booking_success = False
            booked_stand = None

            # Reset seat selection attempts counter for this booking session
            self.seat_selection_attempts = 0

            while seat_booking_attempt < max_seat_booking_attempts and not seat_booking_success:
                seat_booking_attempt += 1
                self.log("=" * 70)
                self.log(f"🎯 SEAT BOOKING ATTEMPT {seat_booking_attempt}/{max_seat_booking_attempts}")
                self.log("=" * 70)

                # Try each stand in preference order
                for stand_index, current_stand in enumerate(stands_to_try, 1):
                    if mode == "MULTI-STAND":
                        self.log(f"Trying Stand {stand_index}/{len(stands_to_try)}: {current_stand}")

                    # Step 4: Select stand (with built-in retry for "Seats Being Taken")
                    if not self.select_stand(stand_name=current_stand):
                        self.log(f"Failed to select {current_stand}", "WARNING")
                        continue  # Try next stand in preference list

                    # Step 5: Select seats (with stand-specific preferences)
                    seat_selection_result = self.select_seats(current_stand=current_stand)
                    if not seat_selection_result:
                        self.log(f"No seats available in {current_stand}, trying next stand...", "WARNING")
                        time.sleep(0.2)
                        continue  # Try next stand in preference list

                    # Step 6: Handle parking/metro popup
                    if not self.handle_parking_metro_popup():
                        self.log("Failed to handle parking/metro popup, retrying...", "WARNING")
                        time.sleep(0.2)
                        break  # Break inner loop, retry from first stand

                    # If we got here, all steps succeeded!
                    seat_booking_success = True
                    booked_stand = current_stand
                    self.booked_stand = current_stand  # Store for later use in payment confirmation
                    self.log("=" * 70)
                    self.log(f"✅ SEAT BOOKING SUCCESSFUL ON ATTEMPT {seat_booking_attempt}!")
                    self.log(f"✅ STAND BOOKED: {booked_stand}")
                    if mode == "MULTI-STAND" and stand_index > 1:
                        self.log(f"📊 Used fallback stand (preference #{stand_index})")
                    self.log("=" * 70)
                    break  # Exit stand loop

                if seat_booking_success:
                    break  # Exit attempt loop

                # If we tried all stands and none worked, wait before retry
                if not seat_booking_success:
                    self.log("All preferred stands unavailable, retrying...", "WARNING")
                    time.sleep(0.5)

            if not seat_booking_success:
                self.log(f"Failed to book seats after {max_seat_booking_attempts} attempts", "ERROR")
                self.log(f"Tried stands: {', '.join(stands_to_try)}", "ERROR")
                return False

            # Step 7: Fill checkout form
            if not self.fill_checkout_form():
                self.log("Failed to fill checkout form", "ERROR")
                return False

            # Step 8: Payment
            if not self.handle_payment():
                self.log("Failed to handle payment", "ERROR")
                return False

            return True

        except Exception as e:
            self.log(f"Booking error: {e}", "ERROR")
            traceback.print_exc()
            return False
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass


def main():
    """Entry point"""
    bot = RCBBookingBot()
    success = bot.book_tickets()

    if success:
        print("\n" + "="*70)
        print("✅ BOOKING COMPLETED SUCCESSFULLY!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ BOOKING FAILED - Check logs above")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()
