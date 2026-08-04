#!/bin/sh
set -e

FIRST_RUN=
if ! [ -e /opt/websockify ]; then
  FIRST_RUN=1
  log_info "Setting up container..."
  tar xzvf /app/opt.tar.gz -C / >&2 >/dev/null
  mkdir -p $MT5
  tar xzvf /app/mt5.tar.gz -C $MT5 >&2 >/dev/null
  mv /app/mt5server.exe $WIN_ROOT
  rm -rf /app/opt.tar.gz /app/mt5.tar.gz
  chmod +x /opt/websockify /opt/noVNC/http-server
fi

cleanup() {
  rm -f /tmp/.X0-lock
  rm -f /tmp/.X99-lock
  rm -rf /usr/lib/wine/i386-windows
}

trap cleanup EXIT
