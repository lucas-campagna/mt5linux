#!/bin/sh
# Test the journal-verification logic in algo_trading.sh WITHOUT MT5/Wine/X.
#
# Only the journal reading is exercised here (the xdotool clicking needs a live
# terminal window and is validated in-container). The point under test is the
# UTF-16 handling: MT5 journals are UTF-16LE, and a naive grep silently returns 0.
set -e
fail=0
check() { if [ "$2" = "$3" ]; then printf '  PASS  %s\n' "$1"
  else printf '  FAIL  %s (expected [%s] got [%s])\n' "$1" "$2" "$3"; fail=1; fi; }

export MT5=$(mktemp -d)
export ALGO_LOG_DIR="$MT5/logs"; mkdir -p "$ALGO_LOG_DIR"

# Source the helpers only (guard against running enable_algo_automation).
. /root/app/oss/mt5linux/docker/src/algo_trading.sh 2>/dev/null || true

# Build a realistic UTF-16LE journal (this is how MT5 actually writes it).
utf16() { iconv -f UTF-8 -t UTF-16LE; }
{
  printf '0\t14:00:00.000\tTerminal\tMetaTrader 5 build 4200 started\n'
  printf '0\t14:00:01.000\tExperts\tautomated trading is disabled\n'
} | utf16 > "$ALGO_LOG_DIR/20260808.log"

# 1. NUL-stripped count sees both matching lines (naive grep would see 0).
check "UTF-16 journal: events counted after NUL strip" "1" "$(_algo_events)"

# 1b. prove the naive path fails: grep straight on the UTF-16 file finds nothing.
naive=$(grep -c "automated trading is" "$ALGO_LOG_DIR/20260808.log" 2>/dev/null || true)
check "control: naive grep on UTF-16 returns 0 (the trap)" "0" "$naive"

# 2. last line reflects current state = disabled.
case "$(_algo_last)" in *disabled*) got=disabled ;; *) got=other ;; esac
check "last event parsed as disabled" "disabled" "$got"

# 3. append an ENABLED line -> count rises, last flips to enabled (post-click state).
printf '0\t14:05:00.000\tExperts\tautomated trading is enabled\n' | utf16 >> "$ALGO_LOG_DIR/20260808.log"
check "after enable: event count is 2" "2" "$(_algo_events)"
case "$(_algo_last)" in *[Ee]nabled*) case "$(_algo_last)" in *disabled*) got=disabled;; *) got=enabled;; esac ;; *) got=other ;; esac
check "last event now enabled" "enabled" "$got"

# 4. no journal at all -> 0, no crash (early-boot case).
rm -f "$ALGO_LOG_DIR"/*.log
check "empty log dir: count is 0" "0" "$(_algo_events)"

rm -rf "$MT5"
echo
if [ "$fail" = 0 ]; then echo "all assertions passed — UTF-16 journal verification correct"; else exit 1; fi
