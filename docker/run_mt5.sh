#!/bin/sh
set -e

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

echo "Starting x11vnc on port $VNC_PORT..."
x11vnc -display :0 -forever -rfbport $VNC_PORT -nopw &
X11VNC_PID=$!

sleep 1

echo "Starting noVNC proxy on port $NOVNC_PORT..."
websockify --web=/opt/noVNC $NOVNC_PORT localhost:$VNC_PORT &
NOVNC_PID=$!

sleep 1

echo "Extracting MetaTrader 5..."
tar -xzf mt5.tar.gz
rm -f mt5.tar.gz

# Disable mono/.NET DLL loading to bypass the wine-mono prompt
export WINEDLLOVERRIDES="mscoree="

# Delete existing profiles to start fresh
rm -rf /app/Profiles/Default/*

# Function to apply envvar overrides to config files
apply_mt5_config() {
  local common_ini="/app/Config/common.ini"
  local terminal_ini="/app/Config/terminal.ini"

  # Ensure Config directory exists
  mkdir -p /app/Config

  # Create common.ini in UTF-8 first
  cat >/tmp/common_ini.txt <<'EOFCOMMON'
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
EOFCOMMON

  # Create terminal.ini in UTF-8 first
  cat >/tmp/terminal_ini.txt <<'EOFTERMINAL'
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
ProfileLast=Blank

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
EOFTERMINAL

  # Apply LOGIN if set
  if [ -n "$LOGIN" ]; then
    echo "Setting LOGIN=$LOGIN"
    echo "Account=$LOGIN" >>/tmp/terminal_ini.txt
  fi

  # Apply SERVER if set
  if [ -n "$SERVER" ]; then
    echo "Setting SERVER=$SERVER"
    echo "Server=$SERVER" >>/tmp/terminal_ini.txt
  fi

  # Apply PASSWORD if set (saved securely)
  if [ -n "$PASSWORD" ]; then
    echo "Setting PASSWORD (saved)"
    echo "Password=$PASSWORD" >>/tmp/terminal_ini.txt
  fi

  # Convert to UTF-16LE and write to final location
  iconv -f UTF-8 -t UTF-16LE /tmp/common_ini.txt >"$common_ini"
  iconv -f UTF-8 -t UTF-16LE /tmp/terminal_ini.txt >"$terminal_ini"

  # Clean up temp files
  rm -f /tmp/common_ini.txt /tmp/terminal_ini.txt

  echo "MT5 config applied"
}

# Apply envvar config overrides
apply_mt5_config

# Start MT5 (portable mode)
wine64 /app/terminal64.exe /portable &
MT5_PID=$!

echo ""
echo "All services started:"
echo "  - Xvfb :0 (PID: $XVFB_PID)"
echo "  - x11vnc :$VNC_PORT (PID: $X11VNC_PID)"
echo "  - noVNC :$NOVNC_PORT (PID: $NOVNC_PID)"
echo "  - MT5 (PID: $MT5_PID)"
echo ""
echo "Access MT5 at: http://localhost:$NOVNC_PORT/vnc.html"
echo ""
echo "MT5 Configuration:"
echo "  - LOGIN: ${LOGIN:-not set}"
echo "  - SERVER: ${SERVER:-not set}"
echo "  - PASSWORD: ${PASSWORD:+<set>}"

trap cleanup EXIT

wait $MT5_PID
