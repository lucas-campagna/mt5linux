# Docker

Run mt5linux using Docker for an isolated environment with Wine and all dependencies pre-configured.

## Quick Start

```bash
cd docker
docker-compose up -d
```

## Access

- **VNC (noVNC)**: http://localhost:6081
- **MT5 Server**: localhost:18812

## Configuration

Environment variables can be configured via `.env` file or directly in `docker-compose.yml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MT5_HOST` | `0.0.0.0` | Host to bind the MT5 server |
| `VNC_PASSWORD` | `password` | VNC password for noVNC access |
| `NVC_PORT` | `6081` | Port for noVNC web interface |
| `MT5_PORT` | `18812` | Port for MT5 RPyC server |

## Example .env file

```bash
MT5_HOST=0.0.0.0
VNC_PASSWORD=your_secure_password
```

## Connect from Linux Python

Once the container is running, connect from your Linux Python:

```python
from mt5linux import MetaTrader5

mt5 = MetaTrader5(host="localhost")
mt5.initialize()
mt5.terminal_info()
mt5.shutdown()
```

## Build Image Locally

```bash
docker build -t mt5linux docker/
```

## Stop

```bash
docker-compose down
```
