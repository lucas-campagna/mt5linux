"""End-to-end tracking of issues #50 and #57 (standalone engine).

Desired behavior: MetaTrader5 must be able to attach to an already-running
mt5server (e.g. `wine mt5server.exe`, or a manually started container)
without creating or managing one:

- explicitly, with engine='standalone' (requested in #57);
- implicitly, with engine='auto' when no container runtime exists
  (#50: v1.0.11 Wine users got "RuntimeError: No container runtime
  available" after upgrading to 1.1.1).

https://github.com/lucas-campagna/mt5linux/issues/50
https://github.com/lucas-campagna/mt5linux/issues/57
"""

import pytest
from helpers import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    docker_available,
    resolve_mode,
    server_reachable,
)

pytestmark = pytest.mark.e2e

ISSUES = (
    "https://github.com/lucas-campagna/mt5linux/issues/50, "
    "https://github.com/lucas-campagna/mt5linux/issues/57"
)


def test_standalone_engine_attaches_to_running_server():
    mode = resolve_mode()
    if mode is None:
        pytest.skip("no running mt5server to attach to")
    if mode == "remote":
        host, port = DEFAULT_HOST, DEFAULT_PORT
    else:
        pytest.skip("container mode requires full mt5 fixture")

    from mt5linux import MetaTrader5

    client = MetaTrader5(host=host, port=port, engine="standalone")
    try:
        assert client.initialize() is True, (
            f"initialize() through engine='standalone' failed: "
            f"{client.last_error()} ({ISSUES})"
        )
    finally:
        try:
            client.shutdown()
        except Exception:
            pass


def test_auto_engine_attaches_when_no_container_runtime():
    # Issue #50's exact scenario: Wine installed, Docker/uDocker not.
    if docker_available():
        pytest.skip("Docker is present; engine='auto' uses the container runtime")
    if not server_reachable(DEFAULT_HOST, DEFAULT_PORT):
        pytest.skip("no standalone server reachable to attach to")

    from mt5linux import MetaTrader5

    client = MetaTrader5(host=DEFAULT_HOST, port=DEFAULT_PORT)
    try:
        assert client.initialize() is True, (
            f"engine='auto' cannot attach to a running server without a "
            f"container runtime ({ISSUES})"
        )
    finally:
        try:
            client.shutdown()
        except Exception:
            pass
