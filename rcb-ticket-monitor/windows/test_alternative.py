#!/usr/bin/env python3
"""
Alternative ChromeDriver Test - Uses Different Connection Method
Bypasses standard localhost connection
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import subprocess
import os

print("="*70)
print("  Alternative ChromeDriver Test - Bypasses Standard Connection")
print("="*70)
print()

print("Step 1: Starting Chrome manually with remote debugging...")

# Start Chrome manually with debugging enabled on specific port
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if not os.path.exists(chrome_path):
    print(f"❌ Chrome not found at standard locations")
    input("Press ENTER to exit...")
    exit(1)

# Start Chrome with remote debugging
user_data_dir = os.path.join(os.environ['TEMP'], 'chrome_selenium_test')
os.makedirs(user_data_dir, exist_ok=True)

chrome_process = subprocess.Popen([
    chrome_path,
    f'--remote-debugging-port=9223',
    f'--user-data-dir={user_data_dir}',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-gpu'
])

print(f"✅ Chrome started manually (PID: {chrome_process.pid})")
print("Waiting 3 seconds for Chrome to initialize...")
time.sleep(3)
print()

print("Step 2: Connecting Selenium to running Chrome...")
try:
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")

    # Minimal service without verbose logging
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("✅ Connected to Chrome!")
    print()

    print("Step 3: Testing navigation...")
    driver.get("about:blank")
    print(f"✅ Loaded: {driver.current_url}")
    time.sleep(1)

    driver.get("https://www.google.com")
    time.sleep(2)
    print(f"✅ Loaded: {driver.title}")
    time.sleep(1)

    driver.get("https://shop.royalchallengers.com")
    time.sleep(3)
    print(f"✅ Loaded: {driver.title}")
    print()

    print("="*70)
    print("✅✅✅ SUCCESS! Alternative method works! ✅✅✅")
    print("="*70)
    print()
    print("This means we can use this approach in the bot.")
    print("The bot will start Chrome manually and connect to it,")
    print("bypassing the standard ChromeDriver connection that's failing.")

    driver.quit()

except Exception as e:
    print(f"❌ Failed: {e}")
    print()
    print("If this also fails with timeout, the issue is very deep.")
    print("Possible causes:")
    print("- Corporate security software")
    print("- VPN blocking localhost")
    print("- Windows has deeper networking issues")

finally:
    # Kill chrome process
    try:
        chrome_process.terminate()
        chrome_process.wait(timeout=5)
        print("Chrome process terminated")
    except:
        chrome_process.kill()
        print("Chrome process killed")

input("\nPress ENTER to exit...")
