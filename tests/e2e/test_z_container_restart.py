"""End-to-end tracking of issue #55, note 2 (+ README-promised container API).

The README documents:

    mt5.container.stop()
    mt5.container.start()
    mt5.container.is_running()

Today stop() and status()/is_running() raise AttributeError (ContainerManager
references an undefined self._name) and start() does not exist at all.
Additionally, a stopped container cannot be restarted: the entrypoint dies
on the pre-existing FIFO ("mkfifo: /opt/wineprefix/drive_c/server: File
exists") under set -e, so docker restart permanently breaks a container.

This module sorts last ('test_z...') because it stops the shared session
container; the reconnect at the end verifies a fresh client can attach again
after the stop/start cycle.

https://github.com/lucas-campagna/mt5linux/issues/55
"""

import pytest
from helpers import resolve_mode

pytestmark = pytest.mark.e2e

ISSUE = "https://github.com/lucas-campagna/mt5linux/issues/55"


def test_container_stop_start_and_reconnect(mt5, mt5_credentials):
    if resolve_mode() != "container":
        pytest.skip("requires the library-managed Docker container")

    manager = mt5.container
    name = manager.name

    assert manager.is_running(), f"container {name} is not running"

    manager.stop()
    assert manager.status() == "exited", f"container {name} did not stop"

    manager.start()
    assert manager.is_running(), (
        f"container {name} did not survive the stop/start cycle "
        f"(pre-existing FIFO in the entrypoint?) ({ISSUE})"
    )

    from mt5linux import MetaTrader5

    client = MetaTrader5(host=manager.host, port=manager.port)
    try:
        result = client.initialize(**mt5_credentials)
        assert result is True, (
            f"initialize() failed after container restart: "
            f"{client.last_error()} ({ISSUE})"
        )
    finally:
        try:
            client.shutdown()
        except Exception:
            pass
