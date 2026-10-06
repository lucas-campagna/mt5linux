#!/bin/sh
set -e

server_search_automation() {
  INPUT_ELEMENT="230 230"
  CANCEL_BUTTON="800 635"
  # FILE_TOP_MENU_BUTTON="21 41"
  # OPEN_AN_ACCOUNT_BUTTON_FILE_FLOAT_MENU="82 321"
  open_search_server_window() {
    while true; do
      WINDOW_ID=$(xdotool search --classname terminal64.exe 2>/dev/null | head -n 1)
      [ -n "$WINDOW_ID" ] && break
      sleep 0.1
    done
    xdotool set_window $WINDOW_ID key Alt f a
  }

  wait_teminal64_open() {
    while true; do
      xdotool search --onlyvisible --classname "terminal64.exe" 2>/dev/null && return 0
      sleep 1
    done
  }

  is_open_search_server_window() {
    for WINDOW_ID in $(xdotool search --onlyvisible --classname "terminal64.exe" 2>/dev/null); do
      WINDOW_NAME=$(xdotool getwindowname $WINDOW_ID)
      if [ "$WINDOW_NAME" = "" ]; then
        return 0
      fi
    done
    return 1
  }

  search_server_window() {
    SERVER_NAME=$1
    [ -z "$SERVER_NAME" ] && return 1
    if ! is_open_search_server_window >/dev/null; then
      open_search_server_window
      local timeout=30
      local start_time=$(date +%s)
      while ! is_open_search_server_window >/dev/null; do
        if [ $(($(date +%s) - start_time)) -ge $timeout ]; then
          log_info "Timeout waiting for search server window, retrying..."
          open_search_server_window
          start_time=$(date +%s)
        fi
        sleep 0.1
      done
    fi
    log_info "Server search: typing $SERVER_NAME"
    xdotool mousemove $INPUT_ELEMENT click 1 type "$SERVER_NAME"
    xdotool key Enter
    sleep 3
    xdotool mousemove $CANCEL_BUTTON click 1
  }

  SEARCHED_SERVERS=""
  wait_teminal64_open

  log_info "Starting server search loop"
  while true; do
    if [ -p $WIN_ROOT/server ]; then
      SERVER_NAME=$(cat $WIN_ROOT/server)
      [ -z "$SERVER_NAME" ] && continue
      [[ "$SEARCHED_SERVERS" == *"$SERVER_NAME"* ]] && continue
      log_info calling search_server_window...
      search_server_window $SERVER_NAME
      SEARCHED_SERVERS="${SEARCHED_SERVERS}${SERVER_NAME} "
    fi
  done
  log_error "Should never reach!!!"
}

update_manager_automation() {
  LATER_BUTTON="570 445"
  while true; do
    while true; do
      UPDATE_WINDOW=$(xdotool search --onlyvisible --name "LiveUpdate" 2>/dev/null | head -n1)
      [ -n "$UPDATE_WINDOW" ] && break
      sleep 1
    done
    xdotool mousemove $LATER_BUTTON click 1
    sleep 300
  done
}

login_automation() {
  OK_BUTTON="488 449"
  while true; do
    LOGIN_WINDOW_ID=$(xdotool search --onlyvisible --name "Login" 2>/dev/null | head -n1)
    [ -z "$LOGIN_WINDOW_ID" ] && sleep 1 && continue
    LOGIN_WINDOW_CLASSNAME=$(xdotool getwindowclassname $LOGIN_WINDOW_ID)
    [ "$LOGIN_WINDOW_CLASSNAME" != "terminal64.exe" ] && sleep 1 && continue
    xdotool mousemove $OK_BUTTON click 1
  done
}

init_wine() {
  log_info "Initializing Wine..."
  wineboot -init >&2 2>/dev/null || true
  while [ ! -d "$WIN_ROOT" ]; do sleep 0.5; done

  [-e $WIN_ROOT/server ] || mkfifo -m 666 $WIN_ROOT/server
}
