#!/bin/sh
set -e

start_xvfb() {
  log_info "Starting Xvfb on :0..."
  Xvfb :0 -screen 0 1024x768x16 &
  XVFB_PID=$!

  sleep 1

  if ! kill -0 $XVFB_PID 2>/dev/null; then
    log_info "ERROR: Xvfb failed to start"
    exit 1
  fi
  log_info "Xvfb started (PID: $XVFB_PID)"
}
