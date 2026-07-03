#!/bin/bash
set -e

echo "Installing dependencies..."
apk add --no-cache xvfb xdotool curl x11vnc python3 py3-websockify

echo "Installing noVNC..."
if [ ! -d "/noVNC" ]; then
    curl -L -o /noVNC.zip https://github.com/novnc/noVNC/archive/refs/heads/master.zip
    unzip -q /noVNC.zip -d /
    mv /noVNC-master /noVNC
    rm -f /noVNC.zip
fi

cleanup() {
    rm -f /tmp/.X99-lock
    rm -f /tmp/.X100-lock
}
cleanup

DISPLAY_NUM=99
export DISPLAY=:$DISPLAY_NUM

echo "Starting Xvfb on :$DISPLAY_NUM..."
Xvfb :$DISPLAY_NUM -ac -screen 0 1024x768x24 &
XVFB_PID=$!

sleep 1

if ! kill -0 $XVFB_PID 2>/dev/null; then
    echo "ERROR: Xvfb failed to start"
    exit 1
fi
echo "Xvfb started (PID: $XVFB_PID)"

echo "Starting x11vnc on port 5900..."
x11vnc -display :$DISPLAY_NUM -forever -rfbport 5900 -nopw &
X11VNC_PID=$!

sleep 1

echo "Starting noVNC proxy on port 6081..."
/noVNC/utils/novnc_proxy --vnc localhost:5900 --listen 6081 &
NOVNC_PID=$!

sleep 1

echo "Starting MetaTrader 5..."
cd /app
if [ ! -f "terminal64.exe" ]; then
    echo "MetaTrader 5 not found. Downloading..."
    curl -L -o mt5setup.exe https://download.mql5.com/cdn/web/metaquotes.ltd/mt5/mt5setup.exe
    echo "Installing MetaTrader 5..."
    wine mt5setup.exe
    rm -f mt5setup.exe
fi

wine terminal64.exe /config:/app/mt5cfg.ini &
MT5_PID=$!

echo "All services started:"
echo "  - Xvfb :$DISPLAY_NUM (PID: $XVFB_PID)"
echo "  - x11vnc :5900 (PID: $X11VNC_PID)"
echo "  - noVNC :6081 (PID: $NOVNC_PID)"
echo "  - MT5 (PID: $MT5_PID)"
echo ""
echo "Access noVNC at: http://localhost:6081/vnc.html"

trap cleanup EXIT

wait $MT5_PID
