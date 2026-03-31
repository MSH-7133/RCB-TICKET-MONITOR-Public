#!/usr/bin/env python3
"""
Test Chrome and ChromeDriver Setup (Windows)
Quick test to verify ChromeDriver works on your Windows PC
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys

def test_chrome():
    """Test if Chrome and ChromeDriver are working"""
    print("=" * 70)
    print("  ChromeDriver Windows Test")
    print("=" * 70)
    print()

    print("Step 1: Setting up Chrome options...")
    chrome_options = Options()
    # Windows-specific options
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    print("✅ Chrome options configured")
    print()

    print("Step 2: Installing/finding ChromeDriver...")
    try:
        service = Service(ChromeDriverManager().install())
        print("✅ ChromeDriver ready")
        print()
    except Exception as e:
        print(f"❌ ChromeDriver installation failed: {e}")
        return False

    print("Step 3: Starting Chrome browser...")
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)
        print("✅ Chrome browser started successfully!")
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
        print("You can now use the RCB Ticket Monitor and Bot.")
        print()

        time.sleep(3)
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure Chrome browser is installed")
        print("2. Check Windows Firewall settings")
        print("3. Temporarily disable antivirus")
        print("4. Run as Administrator")
        return False

    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    try:
        success = test_chrome()
        input("\nPress ENTER to exit...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
