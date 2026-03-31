# RCB Ticket Monitor

A Python script that monitors the Royal Challengers Bengaluru official website for ticket availability and sends instant alerts.

## Features

- ✅ Monitors https://shop.royalchallengers.com/merchandise continuously
- ✅ Detects when tickets become available
- ✅ Plays loud alert sound (multiple times)
- ✅ Shows prominent terminal notification
- ✅ Sends macOS notification
- ✅ Auto-adjusts check frequency after tickets are found
- ✅ Error handling and retry logic
- ✅ No account or API keys needed

## Setup

### 1. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

Or install manually:
```bash
pip3 install requests beautifulsoup4
```

### 2. Make the Script Executable (Optional)

```bash
chmod +x rcb_ticket_monitor.py
```

## Usage

### Basic Usage (checks every 30 seconds)

```bash
python3 rcb_ticket_monitor.py
```

### Custom Check Interval

Check every 15 seconds:
```bash
python3 rcb_ticket_monitor.py 15
```

Check every 60 seconds (1 minute):
```bash
python3 rcb_ticket_monitor.py 60
```

## What Happens When Tickets Are Found?

When tickets become available, the script will:

1. **Play loud alert sounds** - Glass sound effect plays 4 times
2. **Show large terminal alert** - Red colored box with ticket notification
3. **Send macOS notification** - System notification appears
4. **Continue monitoring** - Switches to checking every 5 minutes

## Output Example

```
============================================================
     RCB (Royal Challengers Bengaluru) Ticket Monitor
============================================================
[2026-03-21 10:30:45] [INFO] 🚀 Starting RCB Ticket Monitor
[2026-03-21 10:30:45] [INFO] Monitoring: https://shop.royalchallengers.com/merchandise
[2026-03-21 10:30:45] [INFO] Check interval: 30 seconds
[2026-03-21 10:30:45] [INFO] Press Ctrl+C to stop

[2026-03-21 10:30:45] [INFO] Check #1: Fetching page...
[2026-03-21 10:30:47] [INFO] ⏳ No tickets detected yet
[2026-03-21 10:30:47] [INFO] Next check in 30 seconds...
```

## How It Works

The script:
1. Fetches the RCB merchandise page every 30 seconds (configurable)
2. Parses the HTML content using BeautifulSoup
3. Looks for ticket-related keywords: "ticket", "tickets", "match", "game", "seat", "booking", "buy tickets", etc.
4. Checks for "Add to Cart" or "Buy" buttons associated with ticket products
5. When tickets are detected, triggers multiple alert mechanisms
6. Continues monitoring with reduced frequency (every 5 minutes)

## Stopping the Monitor

Press `Ctrl+C` to stop the monitoring script.

## Tips

- **Run in background**: Use `nohup python3 rcb_ticket_monitor.py &` to run in background
- **Keep terminal visible**: Keep the terminal window visible to see alerts immediately
- **Volume up**: Make sure your Mac's volume is turned up to hear the sound alerts
- **Stay nearby**: The script alerts you on your computer, so stay near it during monitoring
- **Adjust interval**: If tickets are expected very soon, use a shorter interval (e.g., 15 seconds)

## Troubleshooting

### No sound playing?
- Check your Mac's volume settings
- Make sure the terminal has sound permissions
- The script will still show visual alerts

### Script keeps showing errors?
- Check your internet connection
- The website might be temporarily down
- The script will automatically retry

### False positives?
- The script looks for multiple indicators before alerting
- If you get false alerts, the website structure might have changed

## Requirements

- Python 3.6 or higher
- macOS (for sound and notifications)
- Internet connection
- Required packages: requests, beautifulsoup4

## Important Notes

- The script checks the public website and doesn't require any authentication
- Check intervals too frequent (< 10 seconds) might trigger rate limiting
- Recommended interval: 15-30 seconds
- Once tickets are found, the script continues monitoring every 5 minutes
