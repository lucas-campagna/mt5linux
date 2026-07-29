#!/bin/sh
set -e

start_vnc() {
  echo "Starting x11vnc on port $VNC_PORT..."
  x11vnc -display :0 -forever -rfbport $VNC_PORT -nopw &
  X11VNC_PID=$!

  sleep 1
}

start_websockify() {
  echo "Starting noVNC WebSocket proxy on port $NOVNC_PORT..."
  /opt/websockify --daemon --bind-addr 0.0.0.0:$NOVNC_PORT --remote-addr 0.0.0.0:$VNC_PORT &
  NOVNC_PID=$!
}

start_novnc_http() {
  echo "Starting noVNC http server on port $NOVNC_PAGE_PORT..."
  echo "{\"port\": $NOVNC_PORT, \"host\": \"localhost\"}" >/opt/noVNC/defaults.json
  ln -sf /opt/noVNC/vnc.html /opt/noVNC/index.html
  (cd /opt/noVNC && ./http-server -ip $NOVNC_PAGE_PORT >&2 2>/dev/null) &
  NOVNC_PAGE_PID=$!

  sleep 1
}
