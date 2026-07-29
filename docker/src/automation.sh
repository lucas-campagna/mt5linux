#!/bin/sh
set -e

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

update_manager_automation() {
  while true; do
    UPDATE_WINDOW=$(xdotool search --onlyvisible --name "LiveUpdate" 2>/dev/null | head -n1)
    [ -n "$UPDATE_WINDOW" ] && break
    sleep 1
  done
  LATER_BUTTON="570 445"
  xdotool mousemove $LATER_BUTTON click 1
}

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

init_wine() {
  echo "Initializing Wine..."
  wineboot -init >&2 2>/dev/null || true
  sleep 2

  mkfifo -m 666 /opt/wineprefix/drive_c/server 2>/dev/null || true
}
