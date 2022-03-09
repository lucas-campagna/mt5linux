# MetaTrader 5 for linux system

A simple package that use [wine](https://www.winehq.org), [rpyc](https://github.com/tomerfiliba-org/rpyc) and a Python Windows version to allow using [MetaTrader5](https://pypi.org/project/MetaTrader5) on Linux.

## Install


1. Install [Wine](https://wiki.winehq.org/Download).

2. Install [Python for Windows](https://www.python.org/downloads/windows/) on Linux with the help of Wine.

3. Find the path to `python.exe`.

    - I installed on `/home/user/.wine/drive_c/users/user/Local Settings/Application Data/Programs/Python/Python39`.

4. Install [mt5](https://www.mql5.com/en/docs/integration/python_metatrader5) library on your **Windows** Python version.

```bash
pip install MetaTrader5
pip install --upgrade MetaTrader5
```

5. Install this package on your **Linux** Python version:

```
pip install mt5linux
```

## How To Use

Follow the steps:

1. Open MetaTrader5.

2. On a terminal start the server:

```
python -m mt5linux <path/to/python.exe>
```

3. On your script/notebook:

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

4. Be happy!


On step 2 you can provide the port, host, executable, etc... just type `python -m mt5linux --help`.
