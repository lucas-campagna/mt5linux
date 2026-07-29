# MetaTrader 5 for Linux

<!-- test final release -->

A package that uses [Wine](https://www.winehq.org), [RPyC](https://github.com/tomerfiliba-org/rpyc), and [mt5server.exe](https://github.com/lucas-campagna/mt5linux/releases) (a standalone binary with all dependencies) to run [MetaTrader5](https://pypi.org/project/MetaTrader5) on Linux.

For an explanation of who should use mt5linux and why, see [Motivation and Use Cases](docs/MOTIVATION.md).

## Installation

1. Install [Wine](https://wiki.winehq.org/Download).

2. Install this package on **Linux** Python:

   ```bash
   pip install mt5linux
   ```

3. Download the latest [mt5server.exe](https://github.com/lucas-campagna/mt5linux/releases) release binary.

## Docker

Alternatively, you can run this library using Docker, see the [docs](https://github.com/lucas-campagna/mt5linux/tree/master/docker#docker).

## Usage

1. Open MetaTrader5.

2. Start the server:

   - **Linux** (with Wine):
      ```bash
      wine mt5server.exe [-p/--port <port>]
      ```

    The default port is `18812`. The server accepts various options. View them with:
   ```bash
   wine mt5server.exe --help
   ```

3. On the **Linux** side, use the library as usual:

   ```python
   from mt5linux import MetaTrader5

    mt5 = MetaTrader5()
    mt5.initialize(server=<server_ip>, login=<login_id>, password=<password>)
    # Or simply: mt5.initialize() to auto-search for the server
   mt5.terminal_info()
   mt5.shutdown()
   ```

   For full API documentation, see the [official MetaTrader5 Python integration](https://www.mql5.com/en/docs/integration/python_metatrader5/).

## Thanks

- [hpdeandrade](https://github.com/hpdeandrade) for many improvements and insights about [docker](https://github.com/ananta-dev).
- [ananta-dev](https://github.com/ananta-dev) for project [motivation](https://github.com/lucas-campagna/mt5linux/blob/master/docs/MOTIVATION.md#motivation-and-use-cases).
