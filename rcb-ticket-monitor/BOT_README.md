# RCB Ticket Booking Bot

Automated ticket booking system for Royal Challengers Bangalore matches. This bot handles the complete booking flow from login to payment initiation, with intelligent retry logic to beat the competition.

## Features

- **Automatic Login**: Saves session cookies - login once, no OTP needed next time
- **Aggressive Retry Logic**:
  - Up to 100 attempts to book seats
  - 50 retries per stand selection for "Seats Being Taken" errors
  - Auto-retry if Proceed button fails
- **Speed Optimized**: 0.5 second retry intervals - much faster than humans
- **Multi-Match Support**: Configure different match IDs for different games
- **Auto-Fill Forms**: All personal details filled automatically
- **Payment Confirmation**: Monitors and sends SMS when booking succeeds
- **Session Persistence**: Reuses login sessions to save time

## What the Bot Does

1. Login (uses saved session if available)
2. Navigate to specific match
3. Click "BUY TICKETS"
4. Handle "Important Information" popup
5. **Retry Loop** (up to 100 attempts):
   - Select stand (with 50 sub-retries for "Seats Being Taken")
   - Select 2 seats automatically
   - Click Proceed
   - If failed → retry entire process
6. Select Free Metro Ticket
7. Auto-fill checkout form (name, email, mobile, gender)
8. Check Terms & Conditions
9. Click "PAY NOW"
10. Select UPI payment
11. Enter UPI ID automatically
12. Click "VERIFY AND PAY"
13. **Wait for manual payment approval on phone**
14. Detect payment confirmation
15. Send SMS notifications to both phones

## Installation

```bash
# Install dependencies
./venv/bin/pip install selenium webdriver-manager twilio
```

## Configuration

Edit `bot_config.py`:

```python
# User details
USER_INFO = {
    "mobile": "6361238487",
    "first_name": "Mallikarjun",
    "last_name": "H",
    "email": "mallikarjunhanagandi2000@gmail.com",
    "gender": "Male",
    "upi_id": "6361238487@ybl"
}

# Ticket preferences
TICKET_PREFERENCES = {
    "match_id": 1,  # 1 = RCB vs SRH, 2 = next match, etc.
    "target_stand": "E STAND",
    "num_seats": 2,
    "metro_or_parking": "metro",  # "metro" or "parking"
}

# Bot settings
BOT_SETTINGS = {
    "headless": False,  # Set True to run without browser window
    "screenshot_each_step": False,  # Enable for debugging
}
```

## Usage

### Running the Bot

```bash
./venv/bin/python3 rcb_booking_bot.py
```

### For Different Matches

Change `match_id` in `bot_config.py`:
- Match 1 (RCB vs SRH): `"match_id": 1`
- Match 2: `"match_id": 2`
- Match 3: `"match_id": 3`

You can run multiple bot instances simultaneously for different matches!

### First Time Setup

1. Run the bot
2. Enter OTP when prompted (in browser window)
3. Bot saves session cookies to `rcb_session_cookies.pkl`
4. Next time: no OTP needed!

## How It Handles Competition

### Scenario 1: "Seats Are Being Taken" Error
- Bot detects error popup
- Closes popup automatically
- Retries stand selection immediately
- Up to 50 attempts with 0.5s intervals
- Keeps trying until successful

### Scenario 2: Proceed Button Fails
- Bot detects redirect back to stand selection
- Starts over: select stand → select seats → proceed
- Continues retry loop up to 100 total attempts
- Never gives up until seats are booked

### Scenario 3: No Seats Available
- Bot keeps retrying stand selection
- Waits for seats to become available
- Automatically selects first 2 available seats
- Speed advantage: faster than manual selection

## Files Created

- `rcb_session_cookies.pkl` - Saved login session (reused automatically)
- `bot_screenshots/` - Screenshots at each step (if enabled)

## Debugging

Enable screenshots for troubleshooting:

```python
BOT_SETTINGS = {
    "screenshot_each_step": True,  # Enable debugging
}
```

Screenshots will be saved to `bot_screenshots/` folder showing exactly what the bot sees at each step.

## SMS Notifications

When booking succeeds, SMS sent to:
- +916361238487 (Primary)
- +916361334564 (Secondary)

Message includes:
- Booking confirmation
- Stand type
- Email address
- Timestamp

## Important Notes

1. **Manual Payment**: Bot stops at UPI payment screen - you must approve payment on your phone within 6 minutes
2. **Session Cookies**: Delete `rcb_session_cookies.pkl` to force fresh login
3. **Speed vs Screenshots**: Disable screenshots for maximum speed
4. **Browser Window**: Keep browser visible to see what's happening (set `headless: False`)
5. **Multiple Matches**: Run separate bot instances with different `match_id` values

## Troubleshooting

**Bot can't find stand:**
- Check stand name matches exactly (e.g., "E STAND", "NOTHING (R) PLATINUM LOUNGE")
- Enable screenshots to see what bot is seeing

**Login session expired:**
- Delete `rcb_session_cookies.pkl`
- Run bot again to create fresh session

**Bot keeps retrying:**
- This is normal! Bot will retry up to 100 times
- Means tickets are not available yet or competition is high
- Bot will keep trying automatically

**Payment not detected:**
- Normal if you don't approve UPI payment
- Bot will timeout after 6 minutes
- Check email manually for ticket confirmation

## Competition Advantage

**Why this bot wins:**
- **Retry Speed**: 0.5 seconds between attempts vs 3-5 seconds for humans
- **No Hesitation**: Instantly clicks as soon as elements appear
- **Parallel Actions**: Can run multiple instances for different matches
- **Session Reuse**: Skips login after first time
- **Auto-fill**: No typing delays for checkout form
- **Tireless**: Will retry 100 times without fatigue

Your competitive edge: **Speed + Persistence + Automation**
