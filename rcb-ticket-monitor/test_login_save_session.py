#!/usr/bin/env python3
"""
Test Script: Login and Save Session
Just logs in, saves cookies, and exits (doesn't book)
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pickle
import os
from datetime import datetime

# Import user config
from bot_config import USER_INFO, URLS

def log(message, level="INFO"):
    """Print timestamped log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def save_cookies(driver, cookies_file="rcb_session_cookies.pkl"):
    """Save session cookies"""
    try:
        cookies = driver.get_cookies()
        with open(cookies_file, 'wb') as f:
            pickle.dump(cookies, f)
        log(f"✅ Session saved to {cookies_file}")
        log(f"📦 Saved {len(cookies)} cookies")
        return True
    except Exception as e:
        log(f"Error saving cookies: {e}", "ERROR")
        return False

def test_login():
    """Login and save session"""
    log("=" * 70)
    log("RCB SESSION SAVE TEST")
    log("=" * 70)
    log(f"Mobile: {USER_INFO['mobile']}")
    log("=" * 70)

    # Setup browser (visible so you can enter OTP)
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

    # Stealth settings
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Go to tickets page
        log("Opening RCB tickets page...")
        driver.get(URLS["tickets"])
        time.sleep(3)

        # Check if already logged in
        current_url = driver.current_url
        log(f"Current URL: {current_url}")

        if "/ticket" in current_url and "/auth" not in current_url:
            log("✅ Already logged in! Saving session...")
            save_cookies(driver)
            log("✅ Session saved successfully!")
            log("You can close this browser now.")
            input("\nPress ENTER to close browser...")
            return True

        # Need to login
        log("🔐 Login required - clicking a match to trigger login...")

        # Find and click any BUY TICKETS button to trigger login
        try:
            buy_buttons = driver.find_elements(By.XPATH,
                "//button[contains(text(), 'BUY TICKETS') or contains(text(), 'Buy Tickets')]")

            if buy_buttons:
                log(f"Found {len(buy_buttons)} BUY TICKETS button(s)")
                buy_buttons[0].click()
                time.sleep(3)
            else:
                log("No BUY TICKETS buttons found - navigating to login manually", "WARNING")
                driver.get(URLS["base"] + "/auth")
                time.sleep(3)
        except Exception as e:
            log(f"Error clicking button: {e}", "WARNING")

        # Enter mobile number if on login page
        if "/auth" in driver.current_url or "LOGIN" in driver.page_source.upper():
            log("📱 On login page - entering mobile number...")

            try:
                mobile_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='tel' or contains(@placeholder, 'Mobile')]"))
                )
                mobile_input.clear()
                mobile_input.send_keys(USER_INFO['mobile'])
                log(f"Entered mobile: {USER_INFO['mobile']}")
                time.sleep(1)

                # Click Continue
                continue_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
                driver.execute_script("arguments[0].click();", continue_btn)
                log("Clicked Continue")
                time.sleep(3)

                # Wait for OTP screen
                log("=" * 70)
                log("📱 OTP REQUIRED!")
                log("Please enter the OTP in the browser window...")
                log("=" * 70)

                # Monitor for successful login
                for i in range(120):  # 2 minutes max
                    time.sleep(1)

                    # Check if we're logged in (on tickets/category page)
                    if "/ticket" in driver.current_url and "/auth" not in driver.current_url:
                        log("=" * 70)
                        log("✅ LOGIN SUCCESSFUL!")
                        log("=" * 70)

                        # Save session
                        save_cookies(driver)

                        log("=" * 70)
                        log("✅ SESSION SAVED SUCCESSFULLY!")
                        log("This session will be used at 4 PM (no OTP needed)")
                        log("You can close this browser now.")
                        log("=" * 70)

                        input("\nPress ENTER to close browser...")
                        return True

                    if i % 10 == 0 and i > 0:
                        log(f"Waiting for OTP... ({i}s)")

                log("⚠️  Login timeout", "WARNING")
                return False

            except Exception as e:
                log(f"Error during login: {e}", "ERROR")
                import traceback
                traceback.print_exc()
                return False

        return False

    finally:
        driver.quit()
        log("Browser closed")

if __name__ == "__main__":
    success = test_login()

    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Session saved for 4 PM booking")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ Login test failed")
        print("=" * 70)
