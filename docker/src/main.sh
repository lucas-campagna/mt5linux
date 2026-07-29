#!/bin/sh
set -e

FIRST_RUN=
if ! [ -e /opt/websockify ]; then
  FIRST_RUN=1
  echo "Extracting /opt folder"
  tar xzvf /app/opt.tar.gz -C / >&2 >/dev/null
  rm -rf /app/opt.tar.gz
  chmod +x /opt/websockify /opt/noVNC/http-server
fi

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

export WINEDEBUG=-all,+err
export DISPLAY=:0
export WINEARCH=win64
export VNC_PORT=$(($NOVNC_PORT - 1))
export WINEPREFIX=/opt/wineprefix
export WINEDLLOVERRIDES="mscoree="
export MT5_HOST=0.0.0.0

echo "Starting x11vnc on port $VNC_PORT..."
x11vnc -display :0 -forever -rfbport $VNC_PORT -nopw &
X11VNC_PID=$!

sleep 1

echo "Starting noVNC WebSocket proxy on port $NOVNC_PORT..."
/opt/websockify --daemon --bind-addr 0.0.0.0:$NOVNC_PORT --remote-addr 0.0.0.0:$VNC_PORT &
NOVNC_PID=$!

echo "Starting noVNC http server on port $NOVNC_PAGE_PORT..."
echo "{\"port\": $NOVNC_PORT, \"host\": \"localhost\"}" >/opt/noVNC/defaults.json
ln -sf /opt/noVNC/vnc.html /opt/noVNC/index.html
(cd /opt/noVNC && ./http-server -ip $NOVNC_PAGE_PORT >&2 2>/dev/null) &
NOVNC_PAGE_PID=$!

sleep 1

# Initialize Wine properly
echo "Initializing Wine..."
wineboot -init >&2 2>/dev/null || true
sleep 2

mkfifo -m 666 /opt/wineprefix/drive_c/server 2>/dev/null || true

server_search_automation() {
  while true; do
    if [ -p /opt/wineprefix/drive_c/server ]; then
      SERVER_NAME=$(cat /opt/wineprefix/drive_c/server)
      if [ -n "$SERVER_NAME" ]; then
        echo "Server search: typing $SERVER_NAME"
        WINDOW_IDS=$(xdotool search --onlyvisible --name "" 2>/dev/null)
        SERVER_SEARCH_WINDOW=$(echo "$WINDOW_IDS" | sed -n '3p')
        if [ -n "$SERVER_SEARCH_WINDOW" ]; then
          INPUT_ELEMENT="230 230"
          xdotool mousemove $INPUT_ELEMENT click 1 type "$SERVER_NAME"
          xdotool key Enter
        fi
      fi
    fi
  done
}
server_search_automation &
SERVER_SEARCH_PID=$!

update_manager_automation() {
  while true; do
    UPDATE_WINDOW=$(xdotool search --onlyvisible --name "LiveUpdate" 2>/dev/null | head -n1)
    [ -n "$UPDATE_WINDOW" ] && break
    sleep 1
  done
  # never update
  LATER_BUTTON="570 445"
  xdotool mousemove $LATER_BUTTON click 1
}
update_manager_automation &
UPDATE_MANAGER_PID=$!

login_automation() {
  while true; do
    while true; do
      LOGIN_WINDOW_ID=$(xdotool search --onlyvisible --name "Login" 2>/dev/null | head -n1)
      [ -n "$LOGIN_WINDOW_ID" ] && break
      sleep 1
    done
    LOGIN_WINDOW_CLASSNAME=$(xdotool getwindowclassname $LOGIN_WINDOW_ID)
    [ "$LOGIN_WINDOW_CLASSNAME" != "terminal64.exe" ] && break
    OK_BUTTON="488 449"
    xdotool mousemove $OK_BUTTON click 1
  done
}
login_automation &
LOGIN_PID=$!

# Function to apply envvar overrides to config files
apply_mt5_config() {
  test $FIRST_RUN || return
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
wine64 /opt/wineprefix/drive_c/Program/terminal64.exe /portable &
MT5_PID=$!

wait_for_mt5_and_type_server() {
  test $FIRST_RUN || return
  echo "Waiting for MT5 start to search for server $SERVER"
  if [ "$SERVER" ]; then
    while ! xdotool search --name 'MetaTrader' 2>/dev/null; do
      sleep 1
    done
    sleep 20
    echo "Searching for server $SERVER"
    xdotool mousemove 200 230 click 1 type "$SERVER"
    xdotool key Enter
  fi
}
wait_for_mt5_and_type_server &
MT5_SETUP_PID=$!

# Function to start the RPyC server
start_rpyc_server() {
  echo "Starting RPyC server on ${MT5_HOST}:${RPYC_PORT}..."
  wine64 C:\\mt5server.exe --host $MT5_HOST --port $RPYC_PORT &
  RPYC_PID=$!
  echo "RPyC server started (PID: $RPYC_PID)"
}

# Start the RPyC server
start_rpyc_server

# Watchdog loop for RPyC server
watchdog_rpyc() {
  while true; do
    sleep 10
    if ! kill -0 $RPYC_PID 2>/dev/null; then
      echo "RPyC server crashed (PID: $RPYC_PID). Restarting..."
      start_rpyc_server
    fi
  done
}

# Start watchdog in background
watchdog_rpyc &
WATCHDOG_PID=$!

echo ""
echo "All services started:"
echo "  - Xvfb :0 (PID: $XVFB_PID)"
echo "  - x11vnc :$VNC_PORT (PID: $X11VNC_PID)"
echo "  - noVNC :$NOVNC_PORT (PID: $NOVNC_PID)"
echo "  - noVNC page :$NOVNC_PAGE_PORT (PID: $NOVNC_PAGE_PID)"
echo "  - MT5 (PID: $MT5_PID)"
echo "  - RPyC server on ${MT5_HOST}:${RPYC_PORT} (PID: $RPYC_PID)"
echo "  - Watchdog (PID: $WATCHDOG_PID)"
echo ""
echo "Access MT5 at: http://localhost:$NOVNC_PAGE_PORT"
echo ""
echo "MT5 Configuration:"
echo "  - LOGIN: ${LOGIN:-not set}"
echo "  - SERVER: ${SERVER:-not set}"
echo "  - PASSWORD: ${PASSWORD:+<set>}"
echo ""
echo "Connect from Linux Python:"
echo "  mt5 = MetaTrader5(host='<container-ip>', port=$RPYC_PORT)"

cleanup() {
  echo "Cleaning up..."
  kill $WATCHDOG_PID 2>/dev/null || true
  rm -f /tmp/.X0-lock
  rm -f /tmp/.X99-lock
}

trap cleanup EXIT

wait $MT5_PID
