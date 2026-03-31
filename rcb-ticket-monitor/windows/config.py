# RCB Ticket Monitor Configuration

# Your mobile numbers to call (format: +91XXXXXXXXXX)
YOUR_PHONE_NUMBERS = [
    "+916361238487",  # Primary number
    "+916361334564",  # Secondary number (verify this in Twilio console!)
]

# Twilio Configuration
TWILIO_ACCOUNT_SID = "AC5a10167d0d5d067f724f339e8320db67"
TWILIO_AUTH_TOKEN = "4fd6e99662500037c2c2a242ad09b027"
TWILIO_PHONE_NUMBER = "+12545875015"

# Enable/Disable phone calls and SMS (set to False to disable)
ENABLE_PHONE_CALLS = True

# Alert Settings
SMS_RETRY_COUNT = 3  # How many times to retry sending SMS if it fails
ALERT_REPEAT_INTERVAL = 300  # Send alerts again after 5 minutes if tickets still available

# Auto-Launch Booking Bot
# When monitor detects NEW tickets, automatically launch booking bot to book tickets
# Bot will use preferences from bot_config.py (stand preferences, user info, etc.)
AUTO_LAUNCH_BOT = True  # Set to False to only get alerts without auto-booking
