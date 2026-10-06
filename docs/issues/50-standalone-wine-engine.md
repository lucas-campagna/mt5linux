# Issue #50 — v1.1.1 defaults to Docker/uDocker instead of Wine

Upstream: https://github.com/lucas-campagna/mt5linux/issues/50
Status: open. This document describes the issue, how to solve it, and how to validate the solution.

## 1. Issue description

A Wine-only user (no Docker, no uDocker installed) reports that `mt5linux==1.1.1`
fails at construction time:

```python
from mt5linux import MetaTrader5
mt5 = MetaTrader5(host="localhost", port=18812)
```

raises:

```text
RuntimeError: No container runtime available. engine='auto' but neither docker nor udocker is installed.
```

The traceback in the report goes through:

```text
mt5linux/metatrader5.py: MetaTrader5.__init__
  -> mt5linux/_container_manager.py: ContainerManager.__init__
    -> mt5linux/_runtime.py: create_runtime(engine)
```

The user states that `mt5linux==1.0.11` works fine for their Wine workflow.

So this is a regression / breaking behavior change for Wine users: v1.1.1 assumes a
container runtime exists, while v1.0.11 supported a Wine-local workflow.

## 2. Reproduction steps

Prerequisites:

- Linux host with Wine installed and configured.
- Docker not installed.
- uDocker not installed.
- `mt5linux==1.1.1` installed.

Steps:

1. Start MT5 / `mt5server` under Wine so an RPyC server is listening on
   `localhost:18812` (or omit this step to reproduce the constructor failure
   in isolation).
2. Run:

```python
from mt5linux import MetaTrader5
mt5 = MetaTrader5(host="localhost", port=18812)
```

3. Observe `RuntimeError` from `create_runtime(engine="auto")`.

Expected alternative behavior requested by the standalone-server discussion
(see also #57):

```python
MetaTrader5(host="localhost", port=18812, engine="standalone")
```

should attach to an already-running server without creating or managing a
container, and `engine="auto"` should fall back to that behavior when no
container runtime exists.

## 3. Root cause

Verified in the current tree:

- `mt5linux/_runtime.py::create_runtime()` only accepts
  `"auto"`, `"docker"`, and `"udocker"`.
- For `engine="auto"`, it returns `DockerRuntime()` if Docker is available,
  otherwise `UdockerRuntime()` if uDocker is available, otherwise raises
  `RuntimeError`.
- There is no `"standalone"` engine.
- `ContainerManager.__init__()` (`mt5linux/_container_manager.py`) always calls
  `create_runtime(engine)` followed by `self._runtime.start_container(...)`.
  Therefore construction cannot succeed without Docker/uDocker, even when the
  caller only wants to connect to an existing RPyC server.

In other words, the connection path and the container-lifecycle path are fused:
there is no attach-only mode.

## 4. How to solve it

Implement an attach-only `standalone` runtime/engine. Concrete plan:

1. Add `engine="standalone"` support:
   - Extend `create_runtime()` accepted engines to include `"standalone"`.
   - Add a `StandaloneRuntime` (for example `mt5linux/_standalone_runtime.py`)
     implementing the small subset of the runtime interface used by
     `ContainerManager`:
     - no `start_container()` side effects;
     - `container_name` / `port` / `status()` / `stop()` / `remove()` semantics
       that are safe no-ops or report “externally managed”;
     - must not attempt Docker/uDocker CLI calls.
   - Alternatively, make `ContainerManager` accept an already-connected RPyC
     connection / skip `start_container()` when `engine="standalone"`.

2. Make `engine="auto"` degrade gracefully:
   - If Docker is available, keep current container behavior.
   - Else if uDocker is available, keep current uDocker behavior.
   - Else, fall back to `standalone` attach behavior instead of raising
     `RuntimeError`.
   - Preserve an explicit opt-out or warning so users know no container is
     being managed.

3. Keep the public API stable:
   - `MetaTrader5(host=..., port=..., engine="standalone")` must work.
   - `MetaTrader5(host=..., port=...)` with no container runtime must attach
     rather than raise, when a server is reachable.
   - Do not change default container behavior when Docker is present.

4. Handle shutdown semantics:
   - `shutdown()` on a standalone-attached client must not kill an externally
     managed server.
   - Container `stop()` / `remove()` must be safe no-ops or clearly report
     that the server is externally managed.

## 5. How to validate the solution

Automated coverage already exists as tracking tests:

- `tests/e2e/test_standalone_engine.py::test_standalone_engine_attaches_to_running_server`
  - Attaches with `engine="standalone"` to either:
    - the session container’s own RPyC server in container mode, or
    - an already-running server at `DEFAULT_HOST:DEFAULT_PORT` in remote mode.
  - Calls `initialize()` and asserts it returns `True`.
- `tests/e2e/test_standalone_engine.py::test_auto_engine_attaches_when_no_container_runtime`
  - Exact #50 scenario: Docker present causes a skip; otherwise constructs
    `MetaTrader5(host, port)` with default `engine="auto"` and asserts
    `initialize()` returns `True`.

Run:

```bash
.venv/bin/python -m pytest tests/e2e/test_standalone_engine.py -v
```

Manual validation:

```bash
# Terminal 1: standalone server
wine mt5server.exe
```

```python
# Terminal 2: Wine-only host, no Docker/uDocker
from mt5linux import MetaTrader5

# Explicit standalone attach
mt5 = MetaTrader5(host="localhost", port=18812, engine="standalone")
assert mt5.initialize() is True
print(mt5.version())
mt5.shutdown()

# Implicit fallback
mt5 = MetaTrader5(host="localhost", port=18812)
assert mt5.initialize() is True
mt5.shutdown()
```

Also verify no regression in container mode:

```bash
.venv/bin/python -m pytest tests/e2e/test_initialization.py tests/e2e/test_lifecycle.py -v
```

## 6. Scope and non-goals

- This issue is about engine selection and attach-only connection.
- RPyC payload serialization is #57.
- Trading enablement is #51.
- `initialize()` IPC behavior is #55.

## 7. Related files and tests

- `mt5linux/metatrader5.py`: `MetaTrader5.__init__`
- `mt5linux/_container_manager.py`: `ContainerManager.__init__`, `_connect`
- `mt5linux/_runtime.py`: `create_runtime`
- `mt5linux/_docker_runtime.py`, `mt5linux/_udocker_runtime.py`,
  `mt5linux/_base_runtime.py`
- `tests/e2e/test_standalone_engine.py`
- `tests/e2e/helpers.py`: `resolve_mode`, `docker_available`, `server_reachable`
- Related: #57 (standalone mode was also requested there), #55 (initialize behavior)
