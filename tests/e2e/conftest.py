"""Fixtures for the mt5linux end-to-end test suite.

The session client is a library-managed Docker container spawned with the
autologin credentials from .env. Tests that need an initialized terminal use
the function-scoped mt5_initialized fixture so that shutdown()/second-client
side effects from one test cannot break the next one.
"""

import os

import pytest
from dotenv import load_dotenv
from helpers import DEFAULT_HOST, DEFAULT_PORT, resolve_mode

load_dotenv()


@pytest.fixture(scope="session")
def mt5_credentials():
    login = os.environ.get("LOGIN")
    password = os.environ.get("PASSWORD")
    server = os.environ.get("SERVER")
    if not (login and password and server):
        pytest.skip(
            "LOGIN/PASSWORD/SERVER not set in .env "
            "(same keys as tests/integration/test_01.py)"
        )
    return {"login": int(login), "password": password, "server": server}


@pytest.fixture(scope="session")
def mt5(mt5_credentials):
    mode = resolve_mode()
    if mode is None:
        pytest.skip(
            f"no Docker daemon and no server at {DEFAULT_HOST}:{DEFAULT_PORT}; "
            "nothing to run end-to-end"
        )
    if mode == "remote":
        pytest.skip(
            "only a remote mt5server is available; attaching to it requires "
            "the standalone engine (issues #50 and #57) covered by "
            "test_standalone_engine.py"
        )

    from helpers import find_clean_port

    from mt5linux import MetaTrader5
    from mt5linux._runtime import find_available_port

    client = MetaTrader5(
        host="127.0.0.1",
        port=find_clean_port(),
        vnc_port=find_available_port(5901),
        mt5_login=str(mt5_credentials["login"]),
        mt5_password=mt5_credentials["password"],
        mt5_server=mt5_credentials["server"],
    )
    yield client
    try:
        client.shutdown()
    except Exception:
        pass
    try:
        runtime = client.container.get_runtime()
        name = client.container.name
        runtime.stop(name)
        runtime.remove(name)
    except Exception:
        pass


@pytest.fixture()
def mt5_initialized(mt5, mt5_credentials):
    """A client with initialize() freshly (re)established."""
    result = mt5.initialize(**mt5_credentials)
    if result is not True:
        pytest.fail(
            f"session initialize() failed: {mt5.last_error()} "
            "(issue #55: https://github.com/lucas-campagna/mt5linux/issues/55)"
        )
    return mt5


@pytest.fixture(scope="session")
def mt5_unmaterialized(mt5_credentials):
    """A MetaTrader5 client with materialized=False (old behaviour).

    Results are returned as plain dicts / netrefs without reconstruction into
    typed dataclasses. This is a regression fixture for issue #57: it verifies
    that users who set materialized=False get the pre-fix behaviour.
    """
    mode = resolve_mode()
    if mode is None:
        pytest.skip(
            f"no Docker daemon and no server at {DEFAULT_HOST}:{DEFAULT_PORT}; "
            "nothing to run end-to-end"
        )
    if mode == "remote":
        pytest.skip("remote mode not applicable for this fixture")

    from helpers import find_clean_port

    from mt5linux import MetaTrader5
    from mt5linux._runtime import find_available_port

    client = MetaTrader5(
        host="127.0.0.1",
        port=find_clean_port(),
        vnc_port=find_available_port(5901),
        mt5_login=str(mt5_credentials["login"]),
        mt5_password=mt5_credentials["password"],
        mt5_server=mt5_credentials["server"],
        materialized=False,
    )
    yield client
    try:
        client.shutdown()
    except Exception:
        pass
    try:
        runtime = client.container.get_runtime()
        name = client.container.name
        runtime.stop(name)
        runtime.remove(name)
    except Exception:
        pass


@pytest.fixture()
def mt5_unmaterialized_initialized(mt5_unmaterialized, mt5_credentials):
    """An unmaterialized client with initialize() freshly (re)established."""
    result = mt5_unmaterialized.initialize(**mt5_credentials)
    if result is not True:
        pytest.fail(
            f"session initialize() failed: {mt5_unmaterialized.last_error()} "
            "(issue #55)"
        )
    return mt5_unmaterialized
