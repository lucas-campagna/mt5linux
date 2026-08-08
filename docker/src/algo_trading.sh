#!/bin/sh
# Runtime enablement + verification of MT5 algorithmic trading (the "AutoTrading"
# toolbar button). Companion to the common.ini [Experts] AllowLiveTrading gate in
# config.sh: that sets the *global* "Allow Algo Trading" option, but the toolbar
# button is a session toggle that MT5 does NOT reliably restore from config — a
# volume carrying a previously-disabled toolbar state can leave order_send()
# failing with retcode 10027 even when AllowLiveTrading=1.
#
# This clicks the toolbar button and CONFIRMS via the terminal journal, counting
# only events logged after this boot so a stale "enabled" line from an earlier
# session cannot produce a false positive. Gated by MT5_ENABLE_ALGO=1.
set -e

# MT5 portable-mode journal dir (terminal64.exe /portable puts logs beside itself).
ALGO_LOG_DIR="$MT5/logs"

# Toolbar AutoTrading button position. The button has no config representation and
# no reliable hotkey, so a synthetic click is required. Coordinates depend on the
# terminal window geometry; override via MT5_ALGO_BUTTON_XY="x y" for other layouts.
ALGO_BUTTON_XY="${MT5_ALGO_BUTTON_XY:-290 55}"

# Latest journal file, or empty.
_algo_journal() { ls -t "$ALGO_LOG_DIR"/*.log 2>/dev/null | head -n1; }

# Count "automated trading is (enabled|disabled)" lines in the current journal.
# MT5 journals are UTF-16 (a NUL byte between each ASCII char); without stripping
# the NULs the grep never matches and the count is always 0. This is the crux of
# reliable verification.
_algo_events() {
  f=$(_algo_journal); [ -z "$f" ] && { echo 0; return; }
  tr -d '\000' < "$f" | grep -c "automated trading is" 2>/dev/null || echo 0
}

# The most recent enable/disable line (NULs stripped), for the enabled/disabled check.
_algo_last() {
  f=$(_algo_journal); [ -z "$f" ] && return
  tr -d '\000' < "$f" | grep -i "automated trading is" | tail -n1
}

enable_algo_automation() {
  [ "${MT5_ENABLE_ALGO:-0}" = "1" ] || return 0

  # Wait for the terminal window.
  win=""
  i=0
  while [ $i -lt 60 ]; do
    win=$(xdotool search --classname terminal64.exe 2>/dev/null | head -n1)
    [ -n "$win" ] && break
    i=$((i + 1)); sleep 5
  done
  [ -z "$win" ] && { log_error "enable-algo: no MT5 window found"; return 0; }

  # Let login + terminal fully settle; clicks during early boot don't register.
  sleep 40

  base=$(_algo_events)   # journal lines predating our toggling
  i=0
  while [ $i -lt 20 ]; do
    # Click FIRST, then verify, so an enabling click on the final iteration still
    # counts. Re-resolve the window id each pass in case it changed.
    win=$(xdotool search --classname terminal64.exe 2>/dev/null | head -n1)
    xdotool windowactivate --sync "$win" 2>/dev/null || true
    sleep 0.5
    # shellcheck disable=SC2086
    xdotool mousemove $ALGO_BUTTON_XY click 1
    sleep 3
    if [ "$(_algo_events)" -gt "$base" ]; then
      case "$(_algo_last)" in
        *[Ee]nabled*) log_info "enable-algo: algorithmic trading enabled"; return 0 ;;
      esac
    fi
    i=$((i + 1))
  done
  log_error "enable-algo: could not confirm enablement after retries"
  return 0
}
