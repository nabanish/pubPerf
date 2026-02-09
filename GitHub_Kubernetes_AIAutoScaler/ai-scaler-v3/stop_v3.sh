#!/bin/bash

# Stop AI Scaler V3

echo "========================================================================"
echo "Stopping AI Scaler V3"
echo "========================================================================"
echo ""

# Find and kill the process
PID=$(ps aux | grep "python3 ai_scaler_v3.py" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "AI Scaler V3 is not running"
else
    echo "Found AI Scaler V3 process: PID $PID"
    kill $PID
    echo "✓ AI Scaler V3 stopped"
fi

echo ""
echo "Done!"

# Made by Nabanish with Bob's assistance
