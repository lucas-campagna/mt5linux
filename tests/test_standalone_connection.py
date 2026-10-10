"""Regression tests for the standalone engine's rpyc connection (issues #50 + #57).

These run OFFLINE: a real rpyc classic server is started in-process, so no
MetaTrader5, Wine, Docker or network is required.

WHY THESE EXIST. The standalone engine and the issue-#57 materialize() rescue
were each covered by their own test, and the combination was not:
``test_standalone_engine.py`` asserts only ``initialize() is True``, and a bool
crosses rpyc intact, so it passes on a build where every MT5 call returning a
namedtuple fails. ``test_serialization.py`` does exercise the namedtuples, but
``resolve_mode()`` prefers container mode whenever the Docker daemon answers.
Two green suites, one per feature, and nothing testing them together.

The defect those suites missed: ``_connect_fallback`` built its connection with
an empty config, inheriting rpyc's DEFAULT_CONFIG where
``instantiate_custom_exceptions`` is False. vinegar then cannot resolve a
non-builtin remote exception and fabricates a GenericException subclass that
merely *prints* as ``_pickle.PicklingError``, so the ``except PicklingError`` in
``ContainerManager.eval()`` stopped matching and the rescue never ran.
"""

import threading
from collections import namedtuple
from pickle import PicklingError

import pytest
from rpyc.core.service import SlaveService
from rpyc.utils.server import ThreadedServer

from mt5linux._container_manager import ContainerManager
from mt5linux.types import Tick

# A namedtuple that cannot be unpickled by the client, which is precisely the
# situation MetaTrader5's C-extension result types create: __module__ claims
# "builtins" but the class is not there, so attribute lookup fails with
# "Can't pickle <class 'Tick'>: attribute lookup Tick on builtins failed".
REMOTE_SETUP = """
from collections import namedtuple as _nt
Tick = _nt('Tick', ['time','bid','ask','last','volume','time_msc','flags','volume_real'])
Tick.__module__ = 'builtins'
a_tick = Tick(1700000000, 1.0825, 1.0827, 0.0, 7, 1700000000123, 6, 0.0)
"""

EXPECTED = Tick(
    time=1700000000, bid=1.0825, ask=1.0827, last=0.0,
    volume=7, time_msc=1700000000123, flags=6, volume_real=0.0,
)


@pytest.fixture
def classic_server():
    """An in-process rpyc classic server, same service mt5server.exe exposes."""
    server = ThreadedServer(
        SlaveService, hostname="127.0.0.1", port=0, auto_register=False
    )
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    try:
        yield server.port
    finally:
        server.close()
        thread.join(timeout=10)


@pytest.fixture
def manager(classic_server):
    with pytest.warns(UserWarning, match="No container runtime"):
        cm = ContainerManager(
            engine="standalone", host="127.0.0.1", port=classic_server, timeout=30
        )
    cm.execute(REMOTE_SETUP)
    return cm


def test_unpicklable_namedtuple_is_materialized(manager):
    """The whole point: a result that cannot be pickled still arrives, typed.

    Before the fix this raised instead of returning, because the PicklingError
    could not be caught.
    """
    assert manager.eval("a_tick") == EXPECTED


def test_remote_pickling_error_is_a_real_PicklingError(manager):
    """The mechanism, asserted directly.

    ``isinstance`` is the assertion and not ``type(e).__name__``, because the
    fabricated lookalike passes a name check and fails this one -- which is the
    entire reason the defect was invisible.
    """
    import rpyc

    raw = manager._ContainerManager__conn.eval("a_tick")
    with pytest.raises(PicklingError):
        rpyc.classic.obtain(raw)


def test_standalone_connection_has_classic_exception_config(classic_server, manager):
    """Guard the specific flags, so an upgrade that drops them fails here."""
    config = manager._ContainerManager__conn._config
    assert config["instantiate_custom_exceptions"] is True
    assert config["import_custom_exceptions"] is True
    assert config["allow_pickle"] is True


def test_scalars_and_sequences_still_cross_unchanged(manager):
    """A bool crossing intact is why the pre-existing standalone test passed."""
    assert manager.eval("True") is True
    assert manager.eval("2 + 2") == 4
    assert manager.eval("[1, 2, 3]") == [1, 2, 3]
    assert manager.eval("'EURUSD'") == "EURUSD"
