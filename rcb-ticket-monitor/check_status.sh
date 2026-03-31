#!/bin/bash
# Check RCB Monitor Status

if [ -f rcb_monitor.pid ]; then
    PID=$(cat rcb_monitor.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ RCB Monitor is RUNNING (PID: $PID)"
        echo ""
        echo "Recent activity:"
        tail -15 rcb_monitor.log | grep -E "\[INFO\]|\[ALERT\]"
    else
        echo "❌ RCB Monitor is NOT running (stale PID file)"
    fi
else
    echo "❌ RCB Monitor is NOT running (no PID file found)"
fi
