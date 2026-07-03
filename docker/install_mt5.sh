#!/bin/bash
export DISPLAY=:100

echo "Waiting for MT5 installer window..."
while ! xdotool search --name "MetaTrader" 2>/dev/null | grep -q .; do sleep 1; done
sleep 2

echo "Clicking Next (step 1)..."
xdotool key Alt+N
sleep 2

echo "Clicking Next (step 2)..."
xdotool key Alt+N
sleep 2

echo "Clicking Next (step 3)..."
xdotool key Alt+N
sleep 60

echo "Clicking Finish..."
xdotool key Return
sleep 5

echo "Installation automation complete"