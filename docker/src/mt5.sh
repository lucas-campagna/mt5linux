#!/bin/sh
set -e

start_rpyc_server() {
  echo "Starting RPyC server on ${MT5_HOST}:${RPYC_PORT}..."
  wine64 C:\\mt5server.exe --host $MT5_HOST --port $RPYC_PORT &
  RPYC_PID=$!
  echo "RPyC server started (PID: $RPYC_PID)"
}

start_mt5() {
  wine64 /opt/wineprefix/drive_c/Program/terminal64.exe /portable &
  MT5_PID=$!
}

start_watchdog() {
  watchdog_rpyc() {
    while true; do
      sleep 10
      if ! kill -0 $RPYC_PID 2>/dev/null; then
        echo "RPyC server crashed (PID: $RPYC_PID). Restarting..."
        start_rpyc_server
      fi
    done
  }
  watchdog_rpyc &
  WATCHDOG_PID=$!
}

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
