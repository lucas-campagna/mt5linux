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

# Create minimal common.ini (UTF-16)
cat << 'EOF' | iconv -f UTF-8 -t UTF-16LE > /app/Config/common.ini
[Common]
NewsEnable=0
SoundEnable=0
MailEnable=0
ProxyEnable=0
SavePassword=0

[Charts]
MaxBars=1000000

[Experts]
Enabled=0

[News]
Enabled=0
AutoUpdate=0

[Events]
Enable=0
NewsEnable=0

[MarketWatch]
Enabled=0

[Signal]
Enabled=0
AutoUpdate=0

[Toolbox]
Visible=0

[NewsWindow]
Visible=0

[MarketWatchWindow]
Visible=0

[Navigator]
Visible=0

[TreeBox]
Visible=0
EOF

# Create minimal terminal.ini (UTF-16) - hide all windows
cat << 'EOF' | iconv -f UTF-8 -t UTF-16LE > /app/Config/terminal.ini
[Window]
Fullscreen=0
Type=3
Left=0
Top=0
Right=1920
Bottom=1080
LSave=0
TSave=0
RSave=1920
BSave=1080

[Toolbars]
Arrange=1

[Settings]
ToolboxTab=0
NavigatorTab=0
MarketWatchTab=0
TesterTab=-1
XPos=-2
ProfileLast=Default

[ChartsBarState]
Visible=0

[BarState-Summary]
Version=508
Bars=12
Visible=0

[Navigator]
Visible=0

[Toolbox]
Visible=0

[MarketWatchWindow]
Visible=0

[NewsWindow]
Visible=0

[BarState_Bar13]
Visible=0

[BarState_Bar14]
Visible=0

[BarState_Bar15]
Visible=0
EOF

if [ ! -f "terminal64.exe" ]; then
    echo "MetaTrader 5 not found. Downloading..."
    curl -L -o mt5setup.exe https://download.mql5.com/cdn/web/metaquotes.ltd/mt5/mt5setup.exe
    echo "Installing MetaTrader 5..."
    wine64 mt5setup.exe
    rm -f mt5setup.exe
fi

# Start MT5
wine64 /app/terminal64.exe &
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
