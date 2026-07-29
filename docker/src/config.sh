#!/bin/sh
set -e

apply_mt5_config() {
  test $FIRST_RUN || return
  local common_ini="$MT5/common.ini"
  local terminal_ini="$MT5/terminal.ini"
  local assets_dir="$(dirname "$0")/assets"

  mkdir -p /app/Config

  cat "$assets_dir/common_ini.txt" >/tmp/common_ini.txt
  cat "$assets_dir/terminal_ini.txt" >/tmp/terminal_ini.txt

  if [ -n "$AUTH_TOKEN" ]; then
    echo "[Login]" >>/tmp/terminal_ini.txt
    DECODED=$(echo "$AUTH_TOKEN" | base64 -d)
    SERVER=$(echo "$DECODED" | cut -d: -f1)
    LOGIN=$(echo "$DECODED" | cut -d: -f2)
    PASSWORD=$(echo "$DECODED" | cut -d: -f3)
    echo "Setting LOGIN=$LOGIN"
    echo "Account=$LOGIN" >>/tmp/terminal_ini.txt
    echo "Setting SERVER=$SERVER"
    echo "Server=$SERVER" >>/tmp/terminal_ini.txt
    echo "Setting PASSWORD (saved)"
    echo "Password=$PASSWORD" >>/tmp/terminal_ini.txt
  fi

  iconv -f UTF-8 -t UTF-16LE /tmp/common_ini.txt >"$common_ini"
  iconv -f UTF-8 -t UTF-16LE /tmp/terminal_ini.txt >"$terminal_ini"

  rm -f /tmp/common_ini.txt /tmp/terminal_ini.txt

  echo "MT5 config applied"
}

