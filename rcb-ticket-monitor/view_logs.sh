#!/bin/bash
# View RCB Monitor Logs

if [ -f rcb_monitor.log ]; then
    echo "=== Recent RCB Monitor Activity ==="
    echo ""
    tail -30 rcb_monitor.log | grep -v "DeprecationWarning\|NotOpenSSLWarning\|warnings.warn\|cart_buttons"
else
    echo "❌ No log file found"
fi
