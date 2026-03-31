#!/bin/bash
# Keep Laptop Awake for RCB Ticket Monitoring

echo "="
echo "☕ KEEPING LAPTOP AWAKE FOR RCB MONITORING"
echo "="
echo ""

# Check if caffeinate is already running
if pgrep -f "caffeinate.*rcb" > /dev/null; then
    echo "✅ Laptop is already being kept awake!"
    echo ""
    echo "To stop it later, run:"
    echo "  pkill -f 'caffeinate.*rcb'"
    exit 0
fi

echo "Starting caffeinate to prevent laptop sleep..."
echo ""

# Start caffeinate in background
# -d: Prevent display sleep
# -i: Prevent system idle sleep
# -w $MONITOR_PID: Keep awake while monitor is running
if [ -f rcb_monitor.pid ]; then
    MONITOR_PID=$(cat rcb_monitor.pid)
    echo "✅ Keeping laptop awake while monitor (PID: $MONITOR_PID) is running"
    echo ""

    # This will keep laptop awake as long as the monitor is running
    caffeinate -di -w $MONITOR_PID &

    echo "✅ SUCCESS! Laptop will stay awake for monitoring"
    echo ""
    echo "What this means:"
    echo "  • Laptop won't sleep automatically"
    echo "  • Display can turn off (saves power)"
    echo "  • Monitor keeps running 24/7"
    echo "  • Stops automatically when you stop the monitor"
    echo ""
    echo "You can now:"
    echo "  • Close terminal window (monitor keeps running)"
    echo "  • Dim or turn off display (monitor keeps running)"
    echo "  • Leave laptop alone (monitor keeps running)"
    echo ""
    echo "To stop everything later:"
    echo "  ./stop_monitor.sh"
    echo ""
else
    echo "❌ Monitor not running! Start it first:"
    echo "  nohup ./venv/bin/python3 -u rcb_ticket_monitor.py 1 > rcb_monitor.log 2>&1 &"
    echo "  echo \$! > rcb_monitor.pid"
    exit 1
fi
