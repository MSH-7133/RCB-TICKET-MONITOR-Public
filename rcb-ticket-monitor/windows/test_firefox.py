#!/usr/bin/env python3
"""
Test Firefox and GeckoDriver Setup (Windows)
Quick test to verify Firefox WebDriver works on your Windows PC
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import geckodriver_autoinstaller
import time
import sys

def test_firefox():
    """Test if Firefox and GeckoDriver are working"""
    print("=" * 70)
    print("  Firefox WebDriver Windows Test")
    print("=" * 70)
    print()

    print("Step 1: Setting up Firefox options...")
    firefox_options = Options()
    # Firefox preferences
    firefox_options.set_preference('dom.webdriver.enabled', False)
    firefox_options.set_preference('useAutomationExtension', False)
    print("✅ Firefox options configured")
    print()

    print("Step 2: Installing/finding GeckoDriver...")
    try:
        geckodriver_autoinstaller.install()
        print("✅ GeckoDriver ready")
        print()
    except Exception as e:
        print(f"❌ GeckoDriver installation failed: {e}")
        return False

    print("Step 3: Starting Firefox browser...")
    driver = None
    try:
        driver = webdriver.Firefox(options=firefox_options)
        driver.set_page_load_timeout(60)
        print("✅ Firefox browser started successfully!")
        print()

        print("Step 4: Testing page load...")
        driver.get("https://www.google.com")
        time.sleep(2)
        print(f"✅ Successfully loaded: {driver.title}")
        print()

        print("Step 5: Testing RCB website...")
        driver.get("https://shop.royalchallengers.com")
        time.sleep(5)
        print(f"✅ Successfully loaded: {driver.title}")
        print()

        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("Your Windows setup is working correctly!")
        print("You can now use the RCB Ticket Monitor and Bot with Firefox.")
        print()

        time.sleep(3)
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure Firefox browser is installed")
        print("   Download from: https://www.mozilla.org/firefox/")
        print("2. Run as Administrator if needed")
        print("3. Check if Firefox is up to date")
        return False

    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    try:
        success = test_firefox()
        input("\nPress ENTER to exit...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
