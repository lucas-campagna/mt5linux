# MetaTrader 5 for linux system

A simple package that use [wine](https://www.winehq.org), [rpyc](https://github.com/tomerfiliba-org/rpyc) and a Python Windows version to enable the usage of [MetaTrader5](https://pypi.org/project/MetaTrader5) on linux.

## Instal

As usual:

```
pip instal mt5linux
```

## How to use

Follow the steps:

1. open [MetaTrader5](https://www.metatrader5.com)
2. open the server: `python -m mt5linux <path/to/python.exe>`
3. import this module on your script or notebook: `from mt5linux import MetaTrader5`
4. connect to the server: `mt5 = MetaTrader5()`

In steps 2 and 4 you can provide the port, host and so on.
