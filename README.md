# MetaTrader 5 for Linux

A package that uses [Wine](https://www.winehq.org), [RPyC](https://github.com/tomerfiliba-org/rpyc), and a Python Windows version to run [MetaTrader5](https://pypi.org/project/MetaTrader5) on Linux.

## Installation

1. Install [Wine](https://wiki.winehq.org/Download).

2. Install [Python for Windows](https://www.python.org/downloads/windows/) on Linux using Wine.

3. Find the path to `python.exe` (e.g., `/home/user/.wine/drive_c/users/user/Local Settings/Application Data/Programs/Python/Python39`).

4. Install the MetaTrader5 library on your **Windows** Python:

   ```bash
   pip install MetaTrader5
   ```

5. Install this package on both **Windows** and **Linux** Python:

   ```bash
   pip install mt5linux
   ```

## Usage

1. Open MetaTrader5.

2. Start the server:

   - **Windows** (native):
     ```bash
     python -m mt5linux
     ```

   - **Linux** (with Wine):
     ```bash
     wine python -m mt5linux
     ```

   The server accepts various options. View them with:
   ```bash
   python -m mt5linux --help
   ```

3. On the **Linux** side, use the library as usual:

   ```python
   from mt5linux import MetaTrader5

   mt5 = MetaTrader5()
   mt5.initialize()
   mt5.terminal_info()
   mt5.shutdown()
   ```

   For full API documentation, see the [official MetaTrader5 Python integration](https://www.mql5.com/en/docs/integration/python_metatrader5/).
