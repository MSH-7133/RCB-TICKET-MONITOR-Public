#!/usr/bin/env python3
"""
Test ChromeDriver with Fixed Debugging Port
Uses port 9222 instead of random port to avoid binding issues
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

print("="*70)
print("  Testing ChromeDriver with Fixed Port 9222")
print("="*70)
print()

print("Step 1: Configuring Chrome with fixed debugging port...")
chrome_options = Options()

# Windows-specific options
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-software-rasterizer')

# CRITICAL: Use fixed port instead of random
chrome_options.add_argument('--remote-debugging-port=9222')

# Force IPv4 localhost
chrome_options.add_argument('--remote-debugging-address=127.0.0.1')

# Disable localhost check
chrome_options.add_argument('--disable-background-networking')

print("✅ Options configured with fixed port 9222")
print()

print("Step 2: Creating ChromeDriver service...")
service = Service(
    ChromeDriverManager().install(),
    service_args=['--verbose', '--allowed-ips=127.0.0.1', '--allowed-origins=*']
)
print("✅ Service created")
print()

print("Step 3: Starting ChromeDriver (timeout: 30 seconds)...")
print("If this hangs, the issue is definitely localhost binding.")
print()

driver = None
try:
    start = time.time()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    elapsed = time.time() - start

    print(f"✅ ChromeDriver started in {elapsed:.2f} seconds!")
    print()

    print("Step 4: Testing navigation...")
    driver.set_page_load_timeout(60)
    driver.get("about:blank")
    print(f"✅ Loaded: {driver.current_url}")
    print()

    print("Step 5: Testing Google...")
    driver.get("https://www.google.com")
    time.sleep(2)
    print(f"✅ Loaded: {driver.title}")
    print()

    print("="*70)
    print("✅ SUCCESS! Fixed port 9222 works!")
    print("="*70)
    print()
    print("This means we can use fixed port in the actual bot.")

except Exception as e:
    print(f"❌ Failed: {e}")
    print()
    print("Next steps:")
    print("1. Run as admin: netsh winsock reset")
    print("2. Run as admin: netsh int ip reset")
    print("3. Restart computer")
    print("4. Disable IPv6 in network adapter")

finally:
    if driver:
        driver.quit()
        print("Browser closed.")

input("\nPress ENTER to exit...")
