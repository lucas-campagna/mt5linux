"""Connection lifecycle guards.

version() is on issue #57's "works normally" list: these tests should be
green today and keep regressions visible while the tracked issues are fixed.
"""

import pytest

pytestmark = pytest.mark.e2e


def test_version_returns_build_tuple(mt5_initialized):
    version = mt5_initialized.version()

    assert isinstance(version, (tuple, list)) and len(version) == 3
    assert isinstance(version[0], int) and isinstance(version[1], int)
    assert isinstance(version[2], str)


def test_shutdown_then_initialize_again(mt5_initialized, mt5_credentials):
    mt5_initialized.shutdown()

    result = mt5_initialized.initialize(**mt5_credentials)
    assert result is True, (
        f"initialize() failed after shutdown: {mt5_initialized.last_error()}"
    )
