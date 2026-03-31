#!/bin/bash
# Stop RCB Monitor

if [ -f rcb_monitor.pid ]; then
    PID=$(cat rcb_monitor.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "🛑 Stopped RCB Monitor (PID: $PID)"
        rm rcb_monitor.pid
    else
        echo "⚠️  Process not running (cleaning up PID file)"
        rm rcb_monitor.pid
    fi
else
    echo "⚠️  No PID file found - monitor may not be running"
fi
