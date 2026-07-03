#!/bin/bash
export DISPLAY=:100

echo "MT5 watchdog started"

while true; do
    if ! pgrep -x "terminal64.exe" > /dev/null 2>&1; then
        echo "$(date): MT5 terminal not running, launching..."
        cd "$WINEPREFIX/drive_c/Program Files/MetaTrader 5"
        wine terminal64.exe /config:mt5cfg.ini &
        sleep 15
    fi

    WINDOW_ID=$(xdotool search --name "MetaTrader" 2>/dev/null | head -1)
    if [ -n "$WINDOW_ID" ]; then
        xdotool windowactivate --sync "$WINDOW_ID" 2>/dev/null
        xdotool key Return
        sleep 1
    fi

    sleep 5
done