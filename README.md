# MetaTrader 5 for Linux

<!-- final pipeline test -->

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

Alternatively, you can run this library using Docker, see the [Docker docs](https://github.com/lucas-campagna/mt5linux/tree/master/docker#docker).

## Usage

### Option 1: Library-Managed Containers (Recommended for Docker)

The library can automatically start and stop Docker containers for you:

```python
from mt5linux import MetaTrader5

mt5 = MetaTrader5(
    host="localhost",
    mt5_login=12345678,
    mt5_password="your_password",
    mt5_server="Broker-Server",
    engine="auto",        # 'auto', 'docker', or 'udocker'
    image_tag="latest",   # Docker image tag
    ui_port=8080,         # noVNC port (auto-selected if None)
    ui_password=None,     # noVNC password
    vnc_port=5901,        # VNC port
)
mt5.initialize()
mt5.terminal_info()
mt5.shutdown()

# Container is automatically stopped when mt5 is deleted
```

### Option 2: Manual Docker

Run Docker manually with `docker compose up -d`, then connect:

```python
from mt5linux import MetaTrader5

mt5 = MetaTrader5(host="localhost", port=18812)
mt5.initialize()
mt5.terminal_info()
mt5.shutdown()
```

### Option 3: Standalone Server (Linux with Wine)

1. Open MetaTrader5 on Windows/Wine.

2. Start the server:

   ```bash
   wine mt5server.exe [-p/--port <port>]
   ```

   The default port is `18812`. View all options with:
   ```bash
   wine mt5server.exe --help
   ```

3. Connect from Linux Python:

   ```python
   from mt5linux import MetaTrader5

   mt5 = MetaTrader5()
   mt5.initialize(server=<server_ip>, login=<login_id>, password=<password>)
   # Or simply: mt5.initialize() to auto-search for the server
   mt5.terminal_info()
   mt5.shutdown()
   ```

### Accessing Container Properties

When using library-managed containers, access the container manager via the `container` property:

```python
mt5 = MetaTrader5(mt5_login=12345678, mt5_password="password")

print(mt5.container.name)        # Container name
print(mt5.container.status())   # 'running', 'exited', etc.
print(mt5.container.ui_port)     # noVNC port
print(mt5.container.is_running())  # True/False

mt5.container.stop()   # Stop container
mt5.container.start()  # Start container (if using controlled containers)
mt5.container.remove() # Remove container
```

For full API documentation, see the [official MetaTrader5 Python integration](https://www.mql5.com/en/docs/integration/python_metatrader5/).

## Thanks

- [hpdeandrade](https://github.com/hpdeandrade) for many improvements and insights about [docker](https://github.com/ananta-dev).
- [ananta-dev](https://github.com/ananta-dev) for project [motivation](https://github.com/lucas-campagna/mt5linux/blob/master/docs/MOTIVATION.md#motivation-and-use-cases).
