#!/bin/sh
set -e

server_search_automation() {
  INPUT_ELEMENT="230 230"

  is_open_search_server_window() {
    for WINDOW_ID in $(xdotool search --onlyvisible --classname "terminal64.exe" 2>/dev/null); do
      WINDOW_NAME=$(xdotool getwindowname $WINDOW_ID)
      if [ "$WINDOW_NAME" = "" ]; then
        return 0
      fi
    done
    return 1
  }

  while true; do
    if [ -p /opt/wineprefix/drive_c/server ]; then
      SERVER_NAME=$(cat /opt/wineprefix/drive_c/server)
      [ -z "$SERVER_NAME" ] && continue
      echo "Server search: typing $SERVER_NAME"
      if is_open_search_server_window >/dev/null; then
        xdotool mousemove $INPUT_ELEMENT click 1 type "$SERVER_NAME"
        xdotool key Enter
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
