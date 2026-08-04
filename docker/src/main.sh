#!/bin/sh
set -e

. /app/src/log.sh
. /app/src/env.sh
. /app/src/setup.sh
. /app/src/xvfb.sh
. /app/src/vnc.sh
. /app/src/automation.sh
. /app/src/config.sh
. /app/src/mt5.sh

cleanup

start_xvfb

start_vnc
start_websockify
start_novnc_http

init_wine

server_search_automation &
SERVER_SEARCH_PID=$!

update_manager_automation &
UPDATE_MANAGER_PID=$!

login_automation &
LOGIN_PID=$!

apply_mt5_config

start_mt5
wait_for_mt5_and_type_server &
MT5_SETUP_PID=$!

start_rpyc_server
start_watchdog

echo ""
echo "All services started:"
echo "  - Xvfb :0 (PID: $XVFB_PID)"
echo "  - x11vnc :$VNC_PORT (PID: $X11VNC_PID) ${UI_PASSWORD:+[password protected]}"
echo "  - noVNC :$NOVNC_PORT (PID: $NOVNC_PID)"
echo "  - noVNC page :$NOVNC_PAGE_PORT (PID: $NOVNC_PAGE_PID)"
echo "  - MT5 (PID: $MT5_PID)"
echo "  - RPyC server on ${MT5_HOST}:${RPYC_PORT} (PID: $RPYC_PID)"
echo "  - Watchdog (PID: $WATCHDOG_PID)"
echo ""
echo "Access MT5 at: http://localhost:$NOVNC_PAGE_PORT"
echo ""
echo "MT5 Configuration:"
echo "  - LOGIN: ${LOGIN:-not set}"
echo "  - SERVER: ${SERVER:-not set}"
echo "  - PASSWORD: ${PASSWORD:+<set>}"
echo ""
echo "Connect from Linux Python:"
echo "  mt5 = MetaTrader5(host='<container-ip>', port=$RPYC_PORT)"

wait $MT5_PID
