#!/bin/sh
set -e

export DISPLAY=:0
export WINEPREFIX=/opt/wineprefix

cleanup() {
    rm -f /tmp/.X0-lock
    rm -f /tmp/.X99-lock
}
cleanup

echo "Starting Xvfb on :0..."
Xvfb :0 -screen 0 1024x768x16 &
XVFB_PID=$!

sleep 1

if ! kill -0 $XVFB_PID 2>/dev/null; then
    echo "ERROR: Xvfb failed to start"
    exit 1
fi
echo "Xvfb started (PID: $XVFB_PID)"

echo "Starting x11vnc on port 5900..."
x11vnc -display :0 -forever -rfbport 5900 -nopw &
X11VNC_PID=$!

sleep 1

echo "Starting noVNC proxy on port 8080..."
websockify --web=/opt/noVNC 8080 localhost:5900 &
NOVNC_PID=$!

sleep 1

echo "Starting MetaTrader 5..."
cd /app

# Disable mono/.NET DLL loading to bypass the wine-mono prompt
export WINEDLLOVERRIDES="mscoree="

if [ ! -f "terminal64.exe" ]; then
    echo "MetaTrader 5 not found. Downloading..."
    curl -L -o mt5setup.exe https://download.mql5.com/cdn/web/metaquotes.ltd/mt5/mt5setup.exe
    echo "Installing MetaTrader 5..."
    wine64 mt5setup.exe
    rm -f mt5setup.exe
fi

# Start MT5 without config parameter
wine64 /app/terminal64.exe &
MT5_PID=$!

# Wait for MT5 to load, then close unwanted windows
sleep 10

close_mt5_windows() {
    echo "Closing unwanted MT5 windows..."
    # Close Navigator window
    xdotool search --name "Navigator" windowclose 2>/dev/null || true
    # Close Toolbox window  
    xdotool search --name "Toolbox" windowclose 2>/dev/null || true
    xdotool search --name "Toolbox" windowclose 2>/dev/null || true
    # Close Market Watch
    xdotool search --name "Market Watch" windowclose 2>/dev/null || true
    # Close chart windows (they have "Chart" in title but also symbol names)
    for win in $(xdotool search --name "Chart"); do
        xdotool windowclose $win 2>/dev/null || true
    done
    # Press Escape to close any dialogs
    xdotool key Escape 2>/dev/null || true
    echo "Done cleaning up windows"
}

close_mt5_windows &

echo ""
echo "All services started:"
echo "  - Xvfb :0 (PID: $XVFB_PID)"
echo "  - x11vnc :5900 (PID: $X11VNC_PID)"
echo "  - noVNC :8080 (PID: $NOVNC_PID)"
echo "  - MT5 (PID: $MT5_PID)"
echo ""
echo "Access MT5 at: http://localhost:8080/vnc.html"

trap cleanup EXIT

wait $MT5_PID
