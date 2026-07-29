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

trap cleanup EXIT
