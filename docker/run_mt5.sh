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

wine64 /app/terminal64.exe /config:/app/mt5cfg.ini &
MT5_PID=$!

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
