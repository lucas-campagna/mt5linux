#!/bin/sh
set -e

apply_mt5_config() {
  test $FIRST_RUN || return
  local common_ini="/app/Config/common.ini"
  local terminal_ini="/app/Config/terminal.ini"

  mkdir -p /app/Config

  cat >/tmp/common_ini.txt <<'EOFCOMMON'
[Common]
NewsEnable=0
SoundEnable=0
MailEnable=0
ProxyEnable=0
SavePassword=0

[Charts]
MaxBars=1000000

[Experts]
Enabled=0

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

  if [ -n "$LOGIN" ]; then
    echo "Setting LOGIN=$LOGIN"
    echo "Account=$LOGIN" >>/tmp/terminal_ini.txt
  fi

  if [ -n "$SERVER" ]; then
    echo "Setting SERVER=$SERVER"
    echo "Server=$SERVER" >>/tmp/terminal_ini.txt
  fi

  if [ -n "$PASSWORD" ]; then
    echo "Setting PASSWORD (saved)"
    echo "Password=$PASSWORD" >>/tmp/terminal_ini.txt
  fi

  iconv -f UTF-8 -t UTF-16LE /tmp/common_ini.txt >"$common_ini"
  iconv -f UTF-8 -t UTF-16LE /tmp/terminal_ini.txt >"$terminal_ini"

  rm -f /tmp/common_ini.txt /tmp/terminal_ini.txt

  echo "MT5 config applied"
}
