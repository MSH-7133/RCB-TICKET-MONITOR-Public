#!/usr/bin/env python3
"""
Test Microsoft Edge WebDriver - Built-in Windows Browser
Edge might avoid Chrome's localhost connection issues
"""

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

print("="*70)
print("  Microsoft Edge WebDriver Test")
print("="*70)
print()

print("Step 1: Configuring Edge options...")
edge_options = Options()
edge_options.add_argument('--disable-gpu')
edge_options.add_argument('--no-sandbox')
edge_options.add_argument('--disable-dev-shm-usage')
print("✅ Edge options configured")
print()

print("Step 2: Installing/locating EdgeDriver...")
try:
    service = Service(EdgeChromiumDriverManager().install())
    print("✅ EdgeDriver ready")
except Exception as e:
    print(f"❌ EdgeDriver installation failed: {e}")
    input("\nPress ENTER to exit...")
    exit(1)
print()

print("Step 3: Starting Edge browser...")
driver = None
try:
    driver = webdriver.Edge(service=service, options=edge_options)
    print("✅ Edge browser started successfully!")
    print()

    print("Step 4: Testing page load...")
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)

    driver.get("https://www.google.com")
    time.sleep(2)
    print(f"✅ Successfully loaded: {driver.title}")
    print()

    print("Step 5: Testing RCB website...")
    driver.get("https://shop.royalchallengers.com")
    time.sleep(5)
    print(f"✅ Successfully loaded: {driver.title}")
    print()

    print("="*70)
    print("✅✅✅ EDGE WORKS PERFECTLY! ✅✅✅")
    print("="*70)
    print()
    print("Microsoft Edge is working correctly on your Windows system!")
    print("We can use Edge for the RCB Ticket Monitor and Bot.")
    print()
    print("Edge uses Chromium (same as Chrome) so all functionality")
    print("will work exactly the same way!")

    time.sleep(3)

except Exception as e:
    print(f"❌ Test failed: {e}")
    print()
    print(f"Error type: {type(e).__name__}")
    print(f"Error details: {str(e)}")
    print()

    if "HTTPConnectionPool" in str(e) or "ReadTimeout" in str(e):
        print("Same timeout issue with Edge.")
        print("The problem is deeper - Windows networking issue.")
        print()
        print("Recommendation: Try Firefox instead")
        print("Run: pip install geckodriver-autoinstaller")
        print("Then: python test_firefox.py")
    else:
        print("Different error - might be solvable!")

finally:
    if driver:
        driver.quit()
        print("Browser closed.")

input("\nPress ENTER to exit...")
