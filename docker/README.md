# Docker

Run mt5linux using Docker for an isolated environment with Wine and all dependencies pre-configured.

## Quick Start

You have two options:

### Option 1: Use pre-built image (recommended)

Simply copy the `docker-compose.yml` file locally and run:

```bash
docker compose up -d
```

Or run directly with docker:

```bash
docker run -d \
  --name mt5linux \
  -p 6081:6081 \
  -p 18812:18812 \
  -e MT5_HOST=0.0.0.0 \
  -e VNC_PASSWORD=password \
  -e MT5_LOGIN=12345678 \
  -e MT5_PASSWORD=your_password \
  -e MT5_SERVER=Broker-Server \
  lprett/mt5linux:latest
```

> The `latest` image tag is pre MT5 installation, there is a `mt5-installed` image tag which contains MT5 already installed.

### Option 2: Build locally

```bash
docker build -t mt5linux docker/
docker run -d \
  --name mt5linux \
  -p 6081:6081 \
  -p 18812:18812 \
  -e MT5_HOST=0.0.0.0 \
  -e VNC_PASSWORD=password \
  -e MT5_LOGIN=12345678 \
  -e MT5_PASSWORD=your_password \
  -e MT5_SERVER=Broker-Server \
  mt5linux
```

## Access

- **VNC (noVNC)**: http://localhost:6081
- **MT5 Server**: localhost:18812

## Configuration

Environment variables can be configured via `.env` file or directly in `docker-compose.yml`:

| Variable         | Default    | Description                                      |
| ---------------- | ---------- | ------------------------------------------------ |
| `MT5_HOST`       | `0.0.0.0`  | Host to bind the MT5 server                      |
| `VNC_PASSWORD`   | `password` | VNC password for noVNC access                    |
| `MT5_LOGIN`      | (none)     | MT5 account number for autologin                 |
| `MT5_PASSWORD`   | (none)     | MT5 password for autologin                       |
| `MT5_SERVER`     | (none)     | MT5 server name for autologin                    |

## Autologin

To automatically login to an MT5 account when the container starts, provide the account credentials:

```bash
docker run -d \
  --name mt5linux \
  -p 6081:6081 \
  -p 18812:18812 \
  -e MT5_HOST=0.0.0.0 \
  -e VNC_PASSWORD=password \
  -e MT5_LOGIN=12345678 \
  -e MT5_PASSWORD=your_password \
  -e MT5_SERVER=Broker-Server \
  lprett/mt5linux:latest
```

Or via docker-compose with a `.env` file:

```bash
MT5_HOST=0.0.0.0
VNC_PASSWORD=your_secure_password
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=Broker-Server
```

> Note: If credentials are not provided, the MT5 terminal will start without auto-login and you can connect manually via the Python API.

## Crash Recovery

The container includes a watchdog process that automatically:
- Detects if the MT5 terminal crashes
- Dismisses any crash dialogs by pressing Enter
- Restarts the MT5 terminal if needed

This makes the container suitable for fully automated workflows without manual intervention.

## Example .env file

```bash
MT5_HOST=0.0.0.0
VNC_PASSWORD=your_secure_password
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=Broker-Server
```

## Connect from Linux Python

Once the container is running, connect from your Linux Python:

```python
from mt5linux import MetaTrader5

mt5 = MetaTrader5(host="localhost", port=18812)
mt5.initialize()
mt5.terminal_info()
mt5.shutdown()
```

## Udocker Fallback

If Docker is not available, the library automatically falls back to [udocker](https://github.com/indigo-dc/udocker), a lightweight wrapper that can run containers without Docker daemon privileges.

When using the library in `auto` mode (default), it will:
1. Try to use Docker if available
2. Fall back to udocker if Docker is not available

You can also explicitly specify which engine to use:

```python
from mt5linux import MetaTrader5

mt5 = MetaTrader5(engine="docker")   # Force Docker
mt5 = MetaTrader5(engine="udocker")  # Force udocker
mt5 = MetaTrader5(engine="auto")     # Auto-detect (default)
```

For udocker usage, install it first:
```bash
curl https://raw.githubusercontent.com/indigo-dc/udocker/master/udocker.py -o udocker
chmod +x udocker
sudo mv udocker /usr/local/bin/
```

## Stop

```bash
docker-compose down
```
