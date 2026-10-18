#!/bin/sh
set -e

apply_mt5_config() {
  test $FIRST_RUN || return
  local common_ini="$MT5/common.ini"
  local terminal_ini="$MT5/terminal.ini"

  cat >/tmp/common_ini.txt <<'EOFCOMMON'
[Common]
Login=
Server=
Password=
NewsEnable=0
SoundEnable=0
MailEnable=0
ProxyEnable=0
SavePassword=0

[Charts]
MaxBars=1000000

[Experts]
Enabled=0
AllowLiveTrading=0

[News]
Enabled=0
AutoUpdate=0

[Events]
Enable=0
NewsEnable=0

[MarketWatch]
Enabled=0

[Signal]
Enabled=0
AutoUpdate=0

[Toolbox]
Visible=0

[NewsWindow]
Visible=0

[MarketWatchWindow]
Visible=0

[Navigator]
Visible=0

[TreeBox]
Visible=0
EOFCOMMON

  cat >/tmp/terminal_ini.txt <<'EOFTERMINAL'
[Window]
Fullscreen=0
Type=3
Left=0
Top=0
Right=1920
Bottom=1080
LSave=0
TSave=0
RSave=1920
BSave=1080

[Toolbars]
Arrange=1

[Settings]
ToolboxTab=0
NavigatorTab=0
MarketWatchTab=0
TesterTab=-1
XPos=-2
ProfileLast=Blank

[ChartsBarState]
Visible=0

[BarState-Summary]
Version=508
Bars=12
Visible=0

[Navigator]
Visible=0

[Toolbox]
Visible=0

[MarketWatchWindow]
Visible=0

[NewsWindow]
Visible=0

[BarState_Bar13]
Visible=0

[BarState_Bar14]
Visible=0

[BarState_Bar15]
Visible=0
EOFTERMINAL

  if [ -n "$MT5_LOGIN" ]; then
    sed -i "s/^Login=$/Login=$MT5_LOGIN/" /tmp/common_ini.txt
  fi
  if [ -n "$MT5_SERVER" ]; then
    sed -i "s/^Server=$/Server=$MT5_SERVER/" /tmp/common_ini.txt
  fi
  if [ -n "$MT5_PASSWORD" ]; then
    sed -i "s/^Password=$/Password=$MT5_PASSWORD/" /tmp/common_ini.txt
  fi

  # Opt-in algorithmic trading. MT5 rejects order_send() with retcode 10027
  # ("AutoTrading disabled by client") unless "Allow Algo Trading" is on, which is
  # gated by [Experts] AllowLiveTrading in common.ini. Default stays 0 so data-only
  # users are unaffected; set MT5_ENABLE_ALGO=1 to trade. The sed is scoped to the
  # [Experts] section so it can't flip the other [News]/[Signal]/[MarketWatch]
  # Enabled=0 lines.
  if [ "${MT5_ENABLE_ALGO:-0}" = "1" ]; then
    sed -i -e '/^\[Experts\]$/,/^\[/ s/^Enabled=0$/Enabled=1/' \
           -e '/^\[Experts\]$/,/^\[/ s/^AllowLiveTrading=0$/AllowLiveTrading=1/' \
           /tmp/common_ini.txt
  fi

  iconv -f UTF-8 -t UTF-16LE /tmp/common_ini.txt >"$common_ini"
  iconv -f UTF-8 -t UTF-16LE /tmp/terminal_ini.txt >"$terminal_ini"

  rm -f /tmp/common_ini.txt /tmp/terminal_ini.txt

  echo "MT5 config applied"
}
