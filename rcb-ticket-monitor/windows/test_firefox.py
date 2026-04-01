#!/usr/bin/env python3
"""
Test Firefox WebDriver - Alternative to Chrome
Firefox doesn't have the same localhost connection issues
"""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import geckodriver_autoinstaller
import time

print("="*70)
print("  Firefox WebDriver Test")
print("="*70)
print()

print("Step 1: Installing/locating geckodriver...")
try:
    geckodriver_autoinstaller.install()
    print("✅ Geckodriver ready")
except Exception as e:
    print(f"❌ Geckodriver installation failed: {e}")
    exit(1)
print()

print("Step 2: Configuring Firefox options...")
firefox_options = Options()
# firefox_options.add_argument('--headless')  # Uncomment to run headless
print("✅ Options configured")
print()

print("Step 3: Starting Firefox...")
driver = None
try:
    driver = webdriver.Firefox(options=firefox_options)
    print("✅ Firefox started successfully!")
    print()

    print("Step 4: Testing page load...")
    driver.set_page_load_timeout(60)

    driver.get("https://www.google.com")
    time.sleep(2)
    print(f"✅ Loaded: {driver.title}")
    print()

    print("Step 5: Testing RCB website...")
    driver.get("https://shop.royalchallengers.com")
    time.sleep(5)
    print(f"✅ Loaded: {driver.title}")
    print()

    print("="*70)
    print("✅✅✅ FIREFOX WORKS! ✅✅✅")
    print("="*70)
    print()
    print("We can use Firefox for the bot instead of Chrome!")
    print("Firefox doesn't have the localhost timeout issues.")

except Exception as e:
    print(f"❌ Test failed: {e}")
    print()
    print("If Firefox also fails, the issue is very deep.")

finally:
    if driver:
        driver.quit()
        print("Browser closed.")

input("\nPress ENTER to exit...")
