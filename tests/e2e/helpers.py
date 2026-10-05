"""Shared helpers for the end-to-end test suite.

Connection modes (MT5_E2E_MODE, default 'auto'):
- 'container': let the library spawn and manage a Docker container.
- 'remote': attach to an already-running mt5server at MT5_E2E_HOST:MT5_E2E_PORT
  (e.g. `wine mt5server.exe`); meaningful once the standalone engine from
  issues #50/#57 exists.
- 'auto': prefer 'container' when the Docker daemon is reachable, otherwise
  'remote' when a server is listening, otherwise None (nothing to test).

Credentials are read from .env (LOGIN, PASSWORD, SERVER), the same keys used
by tests/integration/test_01.py. SYMBOL optionally selects the instrument for
trading tests (default EURUSD).
"""

import os
import socket
import subprocess

DEFAULT_HOST = os.environ.get("MT5_E2E_HOST", "localhost")
DEFAULT_PORT = int(os.environ.get("MT5_E2E_PORT", "18812"))
MODE = os.environ.get("MT5_E2E_MODE", "auto").lower()
SYMBOL = os.environ.get("SYMBOL", "EURUSD")


def server_reachable(host: str, port: int) -> bool:
    """True when an RPyC server is listening on host:port."""
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False


def docker_available() -> bool:
    """True when the Docker daemon is usable (not just the CLI installed)."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def resolve_mode():
    """Resolve the e2e connection mode: 'container', 'remote' or None."""
    if MODE in ("container", "remote"):
        return MODE
    if docker_available():
        return "container"
    if server_reachable(DEFAULT_HOST, DEFAULT_PORT):
        return "remote"
    return None


def find_clean_port(start: int = 18812) -> int:
    """First free port with no stopped 'mt5linux-<port>' container attached.

    Reusing a port bound to a stopped container makes ContainerManager take
    the 'start existing container' path, which dies on the pre-existing FIFO
    (issue #55, note 2) and would hang the whole session in _connect retries.
    """
    from mt5linux._runtime import find_available_port

    port = find_available_port(start)
    while _container_named(f"mt5linux-{port}"):
        port = find_available_port(port + 1)
    return port


def _container_named(name: str) -> bool:
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if result.returncode != 0:
        return False
    return name in result.stdout.split()
