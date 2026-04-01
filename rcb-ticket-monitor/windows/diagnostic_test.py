#!/usr/bin/env python3
"""
Deep Diagnostic Test for ChromeDriver Issues on Windows
Identifies exact point of failure
"""

import sys
import socket
import subprocess
import os
from pathlib import Path

print("="*70)
print("  DEEP DIAGNOSTIC TEST - ChromeDriver Windows")
print("="*70)
print()

# Test 1: Python and System Info
print("TEST 1: Python & System Info")
print("-" * 70)
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Current Directory: {os.getcwd()}")
print(f"Platform: {sys.platform}")
print()

# Test 2: Check Chrome Installation
print("TEST 2: Chrome Browser Check")
print("-" * 70)
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
chrome_found = False
for path in chrome_paths:
    if os.path.exists(path):
        print(f"✅ Chrome found at: {path}")
        chrome_found = True
        # Get Chrome version
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
            print(f"   Version: {result.stdout.strip()}")
        except Exception as e:
            print(f"   Could not get version: {e}")
        break

if not chrome_found:
    print("❌ Chrome not found in standard locations")
print()

# Test 3: Check Localhost Connectivity
print("TEST 3: Localhost Connectivity")
print("-" * 70)
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 80))
    if result == 0:
        print("✅ Can connect to 127.0.0.1:80 (port in use)")
    else:
        print("⚠️  127.0.0.1:80 not listening (normal)")
    sock.close()

    # Try creating a test socket
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.bind(('127.0.0.1', 0))
    port = test_sock.getsockname()[1]
    test_sock.listen(1)
    print(f"✅ Can bind to localhost, test port: {port}")
    test_sock.close()
except Exception as e:
    print(f"❌ Localhost connectivity issue: {e}")
print()

# Test 4: Check Proxy Settings
print("TEST 4: Proxy/Network Settings")
print("-" * 70)
http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
no_proxy = os.environ.get('NO_PROXY') or os.environ.get('no_proxy')

if http_proxy:
    print(f"⚠️  HTTP_PROXY set: {http_proxy}")
else:
    print("✅ No HTTP_PROXY environment variable")

if https_proxy:
    print(f"⚠️  HTTPS_PROXY set: {https_proxy}")
else:
    print("✅ No HTTPS_PROXY environment variable")

if no_proxy:
    print(f"ℹ️  NO_PROXY: {no_proxy}")
print()

# Test 5: Import Selenium
print("TEST 5: Selenium Import")
print("-" * 70)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    print("✅ All Selenium imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
print()

# Test 6: ChromeDriver Download
print("TEST 6: ChromeDriver Download/Location")
print("-" * 70)
try:
    driver_path = ChromeDriverManager().install()
    print(f"✅ ChromeDriver path: {driver_path}")
    if os.path.exists(driver_path):
        print(f"✅ ChromeDriver file exists")
        print(f"   File size: {os.path.getsize(driver_path)} bytes")
    else:
        print(f"❌ ChromeDriver file not found at path")
except Exception as e:
    print(f"❌ ChromeDriver manager failed: {e}")
    sys.exit(1)
print()

# Test 7: ChromeDriver Service Creation
print("TEST 7: ChromeDriver Service Creation")
print("-" * 70)
try:
    service = Service(
        driver_path,
        service_args=['--verbose', '--log-path=chromedriver_diagnostic.log']
    )
    print("✅ Service object created")
    print(f"   Service args: {service.service_args}")
except Exception as e:
    print(f"❌ Service creation failed: {e}")
    sys.exit(1)
print()

# Test 8: Chrome Options
print("TEST 8: Chrome Options Configuration")
print("-" * 70)
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--remote-debugging-port=9222')  # Explicit port
chrome_options.add_argument('--verbose')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
print("✅ Chrome options configured")
print(f"   Arguments: {chrome_options.arguments}")
print()

# Test 9: Start ChromeDriver (CRITICAL TEST)
print("TEST 9: ChromeDriver Initialization (CRITICAL)")
print("-" * 70)
print("Attempting to start ChromeDriver...")
print("This is where the timeout usually happens.")
print("Please wait up to 120 seconds...")
print()

driver = None
try:
    import time
    start_time = time.time()

    print(f"[{time.time() - start_time:.1f}s] Creating Chrome webdriver...")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print(f"[{time.time() - start_time:.1f}s] ✅ ChromeDriver started successfully!")
    print(f"   Session ID: {driver.session_id}")

    print(f"[{time.time() - start_time:.1f}s] Setting timeouts...")
    driver.set_page_load_timeout(120)
    driver.set_script_timeout(120)
    print(f"[{time.time() - start_time:.1f}s] ✅ Timeouts set")

    print(f"[{time.time() - start_time:.1f}s] Loading about:blank...")
    driver.get("about:blank")
    print(f"[{time.time() - start_time:.1f}s] ✅ about:blank loaded")

    print(f"[{time.time() - start_time:.1f}s] Current URL: {driver.current_url}")

    print()
    print("="*70)
    print("✅✅✅ ALL TESTS PASSED! ✅✅✅")
    print("="*70)
    print()
    print("ChromeDriver is working correctly on your system!")
    print("The original timeout error should be fixed.")

except Exception as e:
    import time
    import traceback

    print()
    print("="*70)
    print("❌❌❌ TEST FAILED ❌❌❌")
    print("="*70)
    print()
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print()
    print("Full Traceback:")
    print("-" * 70)
    traceback.print_exc()
    print("-" * 70)
    print()

    # Check if chromedriver log was created
    if os.path.exists('chromedriver_diagnostic.log'):
        print("ChromeDriver Log Contents:")
        print("-" * 70)
        with open('chromedriver_diagnostic.log', 'r') as f:
            print(f.read())
        print("-" * 70)

    print()
    print("DIAGNOSIS:")
    print("-" * 70)

    if "HTTPConnectionPool" in str(e) or "ReadTimeout" in str(e):
        print("❌ TIMEOUT ERROR - ChromeDriver cannot start")
        print()
        print("Possible causes:")
        print("1. Port blocking - ChromeDriver can't bind to random port")
        print("2. Security software still blocking (even if disabled)")
        print("3. Corporate network/VPN blocking localhost connections")
        print("4. IPv6/IPv4 conflict")
        print("5. Corrupted Chrome or ChromeDriver installation")
        print()
        print("Next steps:")
        print("- Check if you're on corporate network/VPN (disconnect and retry)")
        print("- Try running: netsh winsock reset")
        print("- Restart computer to clear all security software")
        print("- Check chromedriver_diagnostic.log above for details")

    elif "chrome not reachable" in str(e).lower():
        print("❌ Chrome browser cannot be launched")
        print("- Chrome may be corrupted")
        print("- Try reinstalling Chrome browser")

    else:
        print("❌ Unknown error")
        print("- See full traceback above")
        print("- Check chromedriver_diagnostic.log if available")

finally:
    if driver:
        try:
            driver.quit()
            print()
            print("Browser closed successfully")
        except:
            pass

print()
print("="*70)
print("Diagnostic test complete")
print("="*70)
input("\nPress ENTER to exit...")
