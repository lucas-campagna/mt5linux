#!/bin/sh
set -e

export WINEDEBUG=-all,+err
export DISPLAY=:0
export WINEARCH=win64
export VNC_PORT=$(($NOVNC_PORT - 1))
export WINEPREFIX=/opt/wineprefix
export WINEDLLOVERRIDES="mscoree="
export MT5_HOST=0.0.0.0
