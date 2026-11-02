#!/bin/sh
# Test harness for the mt5linux AutoTrading (retcode 10027) config gap + proposed fix.
#
# Reproduces docker/src/config.sh's common.ini generation in isolation, so the bug
# and the fix are verifiable without running MT5 under Wine.
#
#   BUG   : [Experts] Enabled=0 and no AllowLiveTrading -> order_send fails 10027.
#   FIX   : opt-in MT5_ENABLE_ALGO=1 sets BOTH keys, section-scoped so the other
#           three Enabled=0 lines (News/Signal/MarketWatch) are untouched.
#
# Run:  sh test_algo_config.sh    (exit 0 = all assertions pass)
set -e
fail=0
check() {  # check "name" "expected" "actual"
  if [ "$2" = "$3" ]; then printf '  PASS  %s\n' "$1"
  else printf '  FAIL  %s\n       expected [%s] got [%s]\n' "$1" "$2" "$3"; fail=1; fi
}

# ── verbatim slice of the [Experts] region as config.sh writes it (post-fix heredoc) ──
# The fix adds one line: AllowLiveTrading=0 under [Experts]. Everything else is upstream.
make_ini() {
  cat <<'EOF'
[Common]
Login=
Server=
Password=
[Experts]
Enabled=0
AllowLiveTrading=0
[News]
Enabled=0
AutoUpdate=0
[Signal]
Enabled=0
AutoUpdate=0
[MarketWatch]
Enabled=0
EOF
}

# ── the proposed fix: section-scoped sed, opt-in via MT5_ENABLE_ALGO ──────────
apply_algo_fix() {  # reads stdin, writes stdout; env MT5_ENABLE_ALGO
  if [ "${MT5_ENABLE_ALGO:-0}" = "1" ]; then
    sed -e '/^\[Experts\]$/,/^\[/ s/^Enabled=0$/Enabled=1/' \
        -e '/^\[Experts\]$/,/^\[/ s/^AllowLiveTrading=0$/AllowLiveTrading=1/'
  else
    cat
  fi
}

experts_val() {  # experts_val <ini> <key> -> value in the [Experts] section only
  awk -v k="$2" '
    /^\[/{sec=$0} sec=="[Experts]" && $0 ~ "^"k"="{split($0,a,"="); print a[2]; exit}
  ' "$1"
}
count_enabled0() { grep -c '^Enabled=0$' "$1"; }

TMP=$(mktemp -d)

# ── 1. DEFAULT (no env) = upstream behaviour, unchanged (the bug persists) ─────
make_ini | apply_algo_fix > "$TMP/default.ini"
check "default: [Experts] Enabled stays 0"           "0" "$(experts_val "$TMP/default.ini" Enabled)"
check "default: [Experts] AllowLiveTrading stays 0"  "0" "$(experts_val "$TMP/default.ini" AllowLiveTrading)"
check "default: all 4 Enabled=0 lines intact"        "4" "$(count_enabled0 "$TMP/default.ini")"

# ── 2. OPT-IN (MT5_ENABLE_ALGO=1) = algo trading enabled ──────────────────────
MT5_ENABLE_ALGO=1 make_ini | MT5_ENABLE_ALGO=1 apply_algo_fix > "$TMP/algo.ini"
check "opt-in: [Experts] Enabled -> 1"               "1" "$(experts_val "$TMP/algo.ini" Enabled)"
check "opt-in: [Experts] AllowLiveTrading -> 1"      "1" "$(experts_val "$TMP/algo.ini" AllowLiveTrading)"

# ── 3. SCOPING GUARANTEE: News/Signal/MarketWatch NOT touched ─────────────────
# 4 Enabled=0 originally; opt-in flips exactly ONE ([Experts]) -> 3 remain.
check "opt-in: only [Experts] flipped, other 3 intact" "3" "$(count_enabled0 "$TMP/algo.ini")"

rm -rf "$TMP"
echo
if [ "$fail" = 0 ]; then echo "all assertions passed — bug reproduced, fix correct, scoping safe"; else echo "FAILURES"; exit 1; fi
