# Issue #55 — `initialize()` returns `(-10005, 'IPC timeout')` after ~60s

Upstream: https://github.com/lucas-campagna/mt5linux/issues/55
Status: open. This document describes the issue, how to solve it, and how to validate the solution.

It covers both parts tracked in the repository:

- Part 1: `initialize()` fails with `(-10005, 'IPC timeout')` after a consistent
  ~60 seconds, even though the terminal is running and logged in.
- Note 2: container restart/container API is broken (`stop()` / `status()` /
  `is_running()` failures and a pre-existing FIFO that breaks `docker restart`).

## 1. Issue description

### Part 1: IPC timeout

Reported reproduction:

```python
from rpyc.core.protocol import DEFAULT_CONFIG
DEFAULT_CONFIG["sync_request_timeout"] = 600
from mt5linux import MetaTrader5

mt5 = MetaTrader5(host="127.0.0.1", port=18812)
ok = mt5.initialize(login=<LOGIN>, password=<PASSWORD>, server="<SERVER>")
print(ok, mt5.last_error())
```

Result:

```text
initialize(...) -> False in 60.7s   err=(-10005, 'IPC timeout')
initialize()    -> False in 60.5s   err=(-10005, 'IPC timeout')
```

Observed timings across runs: `60.5s`, `60.6s`, `60.7s`, `60.8s`, `61.6s`. The
reporter notes this consistency suggests a fixed internal timeout rather than
resource starvation.

At the same time, the terminal inside the container looks healthy:

- Exactly one `terminal64.exe` is running.
- `mt5server.exe` is running.
- Window title shows an account is loaded, for example
  `MetaTrader 5 - Netting - EURUSD,H1`.
- Generated config contains the expected login/server.
- RPyC transport works (`conn.modules.sys.version`, package version respond).
- The MT5 terminal log contains no API/IPC entries, suggesting the terminal
  never sees the connection attempt.

The reporter ruled out RPyC version skew, low `sync_request_timeout`, Experts
`Enabled=0`, `/portable`, wrong `path=`, missing credentials, CPU/RAM, and
client code.

Important related note: without raising RPyC `sync_request_timeout` first,
`initialize()` raises RPyC `result expired` at ~30s because the call takes ~60s.
Raising the timeout converts that into clean `False` + `IPC timeout`. This links
the symptom to closed issue #22 (“result expired … but it actually logs me
in”).

### Note 2: restart/API breakage

Separately reported while debugging #55:

- `mt5.container.stop()` and `status()` / `is_running()` raise `AttributeError`.
- `start()` does not exist in the current API.
- A stopped container cannot be restarted because the entrypoint dies on the
  pre-existing FIFO:

```text
mkfifo: /opt/wineprefix/drive_c/server: File exists
```

under `set -e`, so `docker restart` permanently breaks a container.

Evidence in the current tree:

- `mt5linux/_container_manager.py::run`, `stop`, `remove`, and `status` use
  `self._name`, but `ContainerManager.__init__` does not set `self._name`; the
  live name accessor is the `name` property backed by
  `self._runtime.container_name`.
- `docker/src/automation.sh::init_wine()` contains a malformed FIFO guard:

```sh
[-e $WIN_ROOT/server ] || mkfifo -m 666 $WIN_ROOT/server
```

The missing spaces make `[-e` not behave as a `[ -e ... ]` test, so the restart
path is fragile/broken as reported.

## 2. Reproduction steps

### Part 1

1. Start a library-managed container with valid broker credentials.
2. Wait for MT5 terminal startup and broker login.
3. Call either:
   - `mt5.initialize(login=..., password=..., server=...)`, or
   - bare `mt5.initialize()`.
4. Observe `False` plus `(-10005, 'IPC timeout')` after ~60 seconds.

The repository’s tracking tests encode the desired behavior:

```python
result = mt5.initialize(**mt5_credentials)
assert result is True
```

and:

```python
result = mt5.initialize()
assert result is True
```

### Note 2

1. Use the library-managed Docker container.
2. Call:

```python
manager = mt5.container
assert manager.is_running()
manager.stop()
assert manager.status() == "exited"
manager.start()
assert manager.is_running()
```

Current behavior: `AttributeError` and/or restart failure on the FIFO.

## 3. Root cause and investigation status

Part 1 is still an open root-cause investigation. The strongest evidence so far:

- RPyC transport is healthy.
- Terminal process and login state look healthy.
- No API/IPC entries in terminal logs.
- Failure timing is highly consistent around 60 seconds.
- Neither broker credentials, `path=`, `/portable`, Experts config, RPyC
  timeout/version, nor container CPU/RAM changes the outcome in the report.

That points away from pure transport failure and toward the MT5 terminal IPC
handshake / terminal-side API listener state, container terminal launch flags,
or the interaction between `initialize()` arguments and the already-running
logged-in terminal.

Note 2 has a much clearer local cause:

- Missing/incorrect container-name attribute (`self._name` vs runtime-backed
  `name`).
- Missing `start()` API despite README examples using
  `mt5.container.stop()` / `start()` / `is_running()`.
- FIFO setup is not restart-safe.

## 4. How to solve it

### Part 1: `initialize()` IPC timeout

Work through this sequence and record which step changes the result:

1. Capture the exact terminal command line and config in the failing container:
   - `terminal64.exe` arguments, especially `/portable` and `/config`.
   - generated `common.ini` login/server/password handling.
   - MT5 terminal logs/journal around the `initialize()` window.
2. Bisect `initialize()` arguments:
   - bare `initialize()`;
   - explicit `path=r"C:\\MT5\\terminal64.exe"`;
   - full login/password/server/timeout/portable combinations.
   - The reporter already found wrong `path=` gives `-10003`, while the known
     terminal path gives `-10005`; preserve that distinction while testing.
3. Isolate the UI automation interaction:
   - `MetaTrader5.initialize()` calls `self._container.ui.search_server(...)`
     up to 3 times when `search_on_init` and `server` are present
     (`mt5linux/metatrader5.py`), swallowing exceptions and retrying.
   - Test with `search_on_init=False` and with server search disabled to see if
     the IPC handshake behavior changes.
4. Check terminal readiness before `initialize()`:
   - Add/log explicit readiness probes for terminal process, main window, login
     state, and RPyC server.
   - Record whether `initialize()` behaves differently after a longer terminal
     warm-up delay.
5. Test image variants systematically:
   - `lprett/mt5linux:latest`, `1.0.11`, `mt5-installed`.
   - Keep RPyC client/server versions aligned; the reporter found
     `mt5-installed` plus RPyC 6.0.1 gives `ValueError: invalid message type`,
     fixed client-side by `rpyc==5.2.3`, but IPC still timed out.
6. Document the RPyC timeout interaction:
   - Ensure client `sync_request_timeout` exceeds the ~60s MT5-side behavior so
     users see `False + IPC timeout` rather than RPyC `result expired`.

Do not “fix” this by lengthening timeouts alone; the goal is successful
`initialize()`, not a slower failure.

### Note 2: restart/API

1. Fix the container identity bug:
   - Replace undefined `self._name` uses in `run()`, `stop()`, `remove()`, and
     `status()` with the runtime-backed `self.name` /
     `self._runtime.container_name`.
   - Add the missing `start()` method with the same naming convention.
2. Make FIFO setup restart-safe:
   - Replace the malformed `[-e ...]` guard with valid POSIX `sh`, for example:

```sh
[ -e "$WIN_ROOT/server" ] || mkfifo -m 666 "$WIN_ROOT/server"
```

   - Or remove any pre-existing FIFO/non-FIFO path safely before `mkfifo`.
   - Ensure the change works under `set -e`.
3. Fix the misleading startup banner noted in #55:
   - `docker/src/main.sh` prints `${LOGIN:-not set}` / `${SERVER:-not set}`,
     while `docker/src/config.sh` reads `$MT5_LOGIN` / `$MT5_SERVER`.
   - Align variable names so the banner reflects the effective configuration.
4. Reconcile the README container API with the implementation:
   - `stop()`, `start()`, `status()` / `is_running()` must all exist and work.
   - Document which operations are container-scoped versus connection-scoped.

## 5. How to validate the solution

Tracking tests already exist.

Part 1:

```bash
.venv/bin/python -m pytest tests/e2e/test_initialization.py -v
```

- `test_initialize_with_credentials_returns_true`
  - Calls `mt5.initialize(**mt5_credentials)`.
  - Asserts result is `True`.
  - Asserts elapsed time is under `MAX_SECONDS = 120`.
- `test_initialize_without_arguments_returns_true`
  - Calls bare `mt5.initialize()`.
  - Asserts result is `True`.

Related guards:

```bash
.venv/bin/python -m pytest tests/e2e/test_lifecycle.py -v
```

- `test_shutdown_then_initialize_again` verifies re-initialization after shutdown.

Note 2:

```bash
.venv/bin/python -m pytest tests/e2e/test_z_container_restart.py -v
```

- `test_container_stop_start_and_reconnect`
  - Requires library-managed Docker container mode.
  - Asserts `is_running()`, then `stop()`, then `status() == "exited"`.
  - Calls `start()`, asserts `is_running()`.
  - Creates a fresh client and asserts `initialize(**mt5_credentials)` is `True`.

Manual validation for restart:

```bash
docker ps --format '{{.Names}} {{.Status}}' | grep mt5linux
docker stop <container>
docker start <container>
docker logs <container> | tail -50
```

There must be no `mkfifo: ... File exists` fatal error, and a fresh
`MetaTrader5(...).initialize(...)` must succeed.

Manual validation for Part 1 should include:

- exact elapsed time for both credential and bare `initialize()`;
- `last_error()` on failure;
- terminal logs/journal during the call window;
- RPyC version on both ends.

## 6. Scope and non-goals

- Engine selection is #50.
- Payload serialization is #57.
- Trading enablement is #51.
- This document does not claim Part 1 is fixed; it is an investigation plus a
  concrete fix for the restart/API subproblem.

## 7. Related files and tests

- `mt5linux/metatrader5.py`: `initialize`, `search_on_init`, server-search retry
- `mt5linux/_container_manager.py`: `run`, `stop`, `remove`, `status`,
  `is_running`, `name`
- `mt5linux/_runtime.py`, `mt5linux/_docker_runtime.py`,
  `mt5linux/_udocker_runtime.py`, `mt5linux/_base_runtime.py`
- `mt5linux/ui.py`
- `docker/src/main.sh`: startup banner variables
- `docker/src/config.sh`: `MT5_LOGIN` / `MT5_SERVER` handling
- `docker/src/automation.sh`: `init_wine`, FIFO setup, server-search automation
- `docker/src/mt5.sh`: terminal launch flags
- `tests/e2e/test_initialization.py`
- `tests/e2e/test_lifecycle.py`
- `tests/e2e/test_z_container_restart.py`
- Related: #22 (`result expired`), #50, #57
