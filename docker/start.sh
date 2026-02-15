#!/bin/bash
cd /mt5linux

# remove display lock if any
rm -rf /tmp/.X100-lock

# set up display
export DISPLAY=:100
Xvfb :100 -ac -screen 0 1024x768x24 &
x11vnc -storepasswd $VNC_PASSWORD /mt5linux/passwd
x11vnc -display :100 -forever -rfbport 5901 -rfbauth /mt5linux/passwd &
chmod 600 /mt5linux/passwd
/mt5linux/noVNC-master/utils/novnc_proxy --vnc localhost:5901 --listen 6081 &

# install mt5 if not installed yet
if [ ! -f "$WINEPREFIX/drive_c/Program Files/MetaTrader 5/terminal64.exe" ]; then
  curl -L -o mt5setup.exe https://download.mql5.com/cdn/web/metaquotes.ltd/mt5/mt5setup.exe
  wine mt5setup.exe
  wine taskkill /IM "terminal64.exe" /F
fi

# open mt5
mv "/mt5linux/mt5cfg.ini" "$WINEPREFIX/drive_c/Program Files/MetaTrader 5"
cd "$WINEPREFIX/drive_c/Program Files/MetaTrader 5"
wine terminal64.exe /config:mt5cfg.ini &
echo "Waiting 15s for MT5 Windows to instantiate..."
sleep 15

cd /mt5linux
# Check for last version
if ! wine python -m pip show mt5linux &> /dev/null; then
    wine python -m pip install mt5linux
fi
# open mt5 linux
wine python -m mt5linux --host $MT5_HOST

# prevent container termination
while true
do
  sleep 1
done
