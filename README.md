# MetaTrader 5 for linux system

A simple package that use [wine](https://www.winehq.org), [rpyc](https://github.com/tomerfiliba-org/rpyc) and a Python Windows version to allow the use of [MetaTrader5](https://pypi.org/project/MetaTrader5) on linux.

## Install

As usual:

```
pip install mt5linux
```

## How to use

Follow the steps:

1. open [MetaTrader5](https://www.metatrader5.com)
2. open the server: `python -m mt5linux <path/to/python.exe>`
3. in your script/notebook:
```python
# import the package
from mt5linux import MetaTrader5
# connecto to the server
mt5 = MetaTrader5(
    # host = 'localhost' (default)
    # port = 18812       (default)
) 
# use as you learned from: https://www.mql5.com/en/docs/integration/python_metatrader5/
mt5.initialize()
mt5.terminal_info()
mt5.copy_rates_from_pos('VALE3',mt5.TIMEFRAME_M1,0,1000)
# ...
# don't forget to shutdown
mt5.shutdown()
```

In step 2 you can provide the port, host, executable, etc... just type `python -m mt5linux --help`.
