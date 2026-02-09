#!/bin/bash
# Reset AI Scaler V3 - Clear logs and state
# Use this after fixing metrics to start fresh

echo "=========================================="
echo "AI Scaler V3 Reset Script"
echo "=========================================="
echo ""

# Check if AI Scaler is running
if pgrep -f "ai_scaler_v3.py" > /dev/null; then
    echo "⚠️  AI Scaler V3 is currently running!"
    echo "Please stop it first (Ctrl+C in the terminal where it's running)"
    echo ""
    exit 1
fi

echo "Clearing AI Scaler V3 state..."
echo ""

# Clear log file
if [ -f "ai_scaler_v3.log" ]; then
    echo "✓ Clearing log file (ai_scaler_v3.log)"
    > ai_scaler_v3.log
else
    echo "ℹ️  No log file found (ai_scaler_v3.log)"
fi

echo ""
echo "=========================================="
echo "Reset Complete!"
echo "=========================================="
echo ""
echo "The AI Scaler V3 state has been cleared."
echo "All previous metrics and decisions based on incorrect data (0.0%) have been removed."
echo ""
echo "You can now start AI Scaler V3 with fresh state:"
echo "  cd ai-scaler-v3"
echo "  python3 ai_scaler_v3.py"
echo ""
echo "It will now collect and learn from correct metrics from Prometheus."
echo ""

# Made by Nabanish with Bob's assistance
