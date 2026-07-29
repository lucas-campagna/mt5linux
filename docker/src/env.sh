#!/bin/sh
set -e

export WINEDEBUG=-all,+err
export DISPLAY=:0
export WINEARCH=win64
export VNC_PORT=$(($NOVNC_PORT - 1))
export WINEPREFIX=/opt/wineprefix
export WIN_ROOT="$WINEPREFIX/drive_c"
export MT5="$WIN_ROOT/MT5"
export WINEDLLOVERRIDES="mscoree="
export MT5_HOST=0.0.0.0
