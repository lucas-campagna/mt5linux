"""End-to-end tracking of issue #55.

initialize() must return True promptly against a library-managed container.
Reported failure mode: False with last_error() == (-10005, 'IPC timeout')
after a consistent ~60 seconds, while the terminal inside the container is
up and logged in.

https://github.com/lucas-campagna/mt5linux/issues/55
"""

import time

import pytest

pytestmark = pytest.mark.e2e

ISSUE = "https://github.com/lucas-campagna/mt5linux/issues/55"
MAX_SECONDS = 120


def test_initialize_with_credentials_returns_true(mt5, mt5_credentials):
    started = time.monotonic()
    result = mt5.initialize(**mt5_credentials)
    elapsed = time.monotonic() - started

    assert result is True, (
        f"initialize() failed after {elapsed:.1f}s: {mt5.last_error()} ({ISSUE})"
    )
    assert elapsed < MAX_SECONDS, (
        f"initialize() took {elapsed:.1f}s (> {MAX_SECONDS}s) ({ISSUE})"
    )


def test_initialize_without_arguments_returns_true(mt5):
    # The container was spawned with autologin credentials, so a bare
    # initialize() must find and attach to the running terminal.
    result = mt5.initialize()

    assert result is True, (
        f"initialize() failed: {mt5.last_error()} ({ISSUE})"
    )
