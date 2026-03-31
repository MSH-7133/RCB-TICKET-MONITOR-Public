"""
RCB Ticket Bot Configuration
Contains all user details and bot settings
"""

# ===== USER DETAILS =====
USER_INFO = {
    "mobile": "6361238487",  
    "first_name": "Mallikarjun",
    "last_name": "H",
    "email": "mallikarjunhanagandi2000@gmail.com",
    "gender": "Male",  # Options: Male, Female, Others
    "upi_id": "6361238487@ybl"
}

# ===== TICKET PREFERENCES =====
TICKET_PREFERENCES = {
    "match_name": "Royal Challengers Bengaluru vs Chennai Super Kings",  # Full match name as shown on website

    # SINGLE STAND MODE: Set target_stand for single stand booking
    "target_stand": "PUMA SHANTA RANGASWAMY B STAND",  # The stand you want to book (used if stand_preferences is None)

    # MULTI-STAND MODE: Set stand_preferences for priority-based booking
    # Bot will try stands in order - if 1st choice sold out, tries 2nd, then 3rd, etc.
    # Set to None to use single stand mode (target_stand)
    "stand_preferences": [
        "PUMA SHANTA RANGASWAMY B STAND",  # 1st preference - ₹3750 (try first)
        "BOAT C STAND",                     # 2nd preference - ₹3750 (fallback)
        "SUN PHARMA A STAND"                # 3rd preference - ₹3750 (fallback)
    ],
    # To use single stand mode, set:
    #"stand_preferences": None,

    "num_seats": 2,  # Number of seats to select (max 2)
    "metro_or_parking": "metro",  # Options: "metro" or "parking"
}

# ===== SEAT SELECTION PREFERENCES =====
# Bot automatically selects best seats based on these preferences:
#
# PUMA B STAND & BOAT C STAND:
#   - Prefer rows K-Z (middle rows for better view)
#   - Within rows, prefer MIDDLE seat numbers (e.g., seats 25-26 if row has 1-50)
#   - Example: K25, K26 > K24, K27 > K20, K30
#
# SUN PHARMA A STAND:
#   - Top priority: Row A (closest to action)
#   - Within row A: Prefer FRONT seats 1-20 (stand is huge, want close seats)
#   - Example: A1, A2 > A5, A6 > A15, A16 > A25, A26
#   - Fallback: Rows B-Z with front seats
#
# SMART FALLBACK STRATEGY:
#   - Attempts 1-19: Prefer specific rows (K-Z for PUMA/BOAT, A for SUN PHARMA)
#   - Attempts 20+: ACCEPT ANY AVAILABLE SEATS
#   - Better to get ANY seat than miss tickets entirely!
#
# Bot will automatically:
#   1. Scan all available seats
#   2. Score them based on row letter and seat position
#   3. Select the 2 best seats (adjacent if possible)
#   4. PUMA/BOAT: middle seats | SUN PHARMA A: front seats (1-20)
#   5. Fall back to ANY seats if preferred positions unavailable after 20 attempts

# ===== BOT SETTINGS =====
BOT_SETTINGS = {
    "headless": False,  # Set to True to run without browser window
    "screenshot_each_step": False,  # Disabled for speed (enable for debugging)
    "max_wait_time": 30,  # Max seconds to wait for elements
    "seat_check_interval": 0.5,  # Seconds between seat availability checks
    "auto_proceed_on_seats": True,  # Automatically click proceed when 2 seats selected
}

# ===== URLS =====
URLS = {
    "base": "https://shop.royalchallengers.com",
    "tickets": "https://shop.royalchallengers.com/ticket",
}

# ===== TIMEOUTS =====
TIMEOUTS = {
    "page_load": 30,
    "element_wait": 3,  # Reduced from 10 to 3 for faster seat booking
    "otp_wait": 120,  # 2 minutes for OTP entry
    "checkout_timer": 600,  # 10 minutes checkout timer
    "payment_timer": 360,  # 6 minutes payment timer
}
