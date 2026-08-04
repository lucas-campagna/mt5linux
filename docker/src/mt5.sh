#!/bin/sh
set -e

. /app/src/automation.sh

start_rpyc_server() {
  log_info "Starting RPyC server on ${MT5_HOST}:${RPYC_PORT}..."
  wine64 C:/mt5server.exe --host $MT5_HOST --port $RPYC_PORT &
  RPYC_PID=$!
  log_info "RPyC server started (PID: $RPYC_PID)"
}

start_mt5() {
  wine64 C:/MT5/terminal64.exe /portable &
  MT5_PID=$!
  wait_for_terminal64
}

start_watchdog() {
  watchdog_rpyc() {
    while true; do
      sleep 10
      if ! kill -0 $RPYC_PID 2>/dev/null; then
        log_info "RPyC server crashed (PID: $RPYC_PID). Restarting..."
        start_rpyc_server
      fi
    done
  }
  watchdog_rpyc &
  WATCHDOG_PID=$!
}

wait_for_terminal64() {
  while ! xdotool search --classname 'terminal64.exe' 2>/dev/null; do
    sleep 1
  done
}

wait_for_mt5_and_type_server() {
  test $FIRST_RUN || return
  if [ "$SERVER" ]; then
    log_info "Waiting for MT5 start to search for server $SERVER"
    wait_for_terminal64
    search_server_window
  fi
}
