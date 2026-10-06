# Issue #51 — `order_send()` fails with retcode 10027 (AutoTrading disabled)

Upstream: https://github.com/lucas-campagna/mt5linux/issues/51
Status: open. This document describes the issue, how to solve it, and how to validate the solution.

## 1. Issue description

Market-data calls work, but placing an order fails:

```python
res = mt5.order_send(request)
print(res.retcode)  # 10027 — “AutoTrading disabled by client”
```

Reported root cause: `docker/src/config.sh` writes `common.ini` with:

```ini
[Experts]
Enabled=0
```

and nothing enables the AutoTrading toolbar. The container can log in and read
data, but cannot trade out of the box. There is no environment switch to opt in.

Expected: an opt-in environment variable that enables algorithmic trading so
`order_send()` works, with the default left off so data-only users are unaffected.

Two gotchas flagged by the reporter:

1. `common.ini` contains four `Enabled=0` lines (`[Experts]`, `[News]`,
   `[Signal]`, `[MarketWatch]`), so a fix must scope to `[Experts]` only.
2. `AllowLiveTrading=1` in `common.ini` sets the global option, but the toolbar
   AutoTrading button is a session toggle that MT5 does not reliably restore from
   config. A persisted-off state can still yield 10027. The reporter recommends
   belt-and-suspenders: a runtime toolbar-enable plus journal confirmation.

## 2. Reproduction steps

Prerequisites:

- Library-managed Docker container with autologin credentials.
- Configured trading symbol (default `EURUSD`; override with `SYMBOL=...`).

Safe check (places no order):

```python
allowed = mt5.container.eval("mt5.terminal_info().trade_allowed")
assert allowed is True
```

Current behavior on an affected container: `allowed` is `False`, which means a
later `order_send()` will be rejected with retcode `10027`.

Opt-in real-order check:

```bash
MT5_E2E_ALLOW_ORDER_SEND=1 .venv/bin/python -m pytest tests/e2e/test_trading.py -v
```

The test builds a minimum-volume market order from live `volume_min` and current
ask price, calls `order_send()`, asserts the retcode is not `10027`, then
best-effort closes positions opened for the test symbol.

## 3. Root cause

Verified in the current tree:

- `docker/src/config.sh::apply_mt5_config()` writes a fresh `common.ini` with:

```ini
[Experts]
Enabled=0
```

- There is no opt-in path in `docker/src/config.sh`, `docker/src/env.sh`,
  `docker/src/main.sh`, or `docker/src/automation.sh` that sets
  `[Experts] Enabled=1` or otherwise enables the AutoTrading toolbar.
- `docker/src/automation.sh` currently automates server search, LiveUpdate
  dismissal, login confirmation, and Wine/FIFO setup, but contains no
  AutoTrading-toolbar automation.

Therefore the terminal starts in a data-only posture by default with no supported
way to enable trading.

## 4. How to solve it

Recommended fix has two layers.

### A. Config layer: opt-in environment variable

1. Add an explicit opt-in variable, for example `MT5_ALGO_TRADING=1`.
2. Default behavior stays unchanged (`[Experts] Enabled=0`).
3. When the opt-in variable is set, `apply_mt5_config()` must:
   - set only the `[Experts]` section’s `Enabled` value to `1`;
   - leave `[News]`, `[Signal]`, and `[MarketWatch]` untouched;
   - optionally set the global live-trading option if appropriate, without
     relying on it alone.
4. Plumb the variable through container startup:
   - `docker/docker-compose.yml` / image runtime environment;
   - `docker/src/env.sh`;
   - `ContainerManager` / runtime `start_container()` parameters if credentials
     and UI options are passed that way today.
5. Keep the setting scoped and documented so data-only users are unaffected.

### B. Runtime layer: toolbar/session toggle

Because MT5 may not restore the toolbar AutoTrading button from config
reliably:

1. Add automation that enables the AutoTrading toolbar at runtime when the
   opt-in variable is set.
2. Confirm enablement through the terminal journal/status rather than assuming
   config-file state is sufficient.
3. Make the automation idempotent and safe when the variable is unset.

Suggested implementation order:

1. Implement the config opt-in first; verify `terminal_info().trade_allowed`
   becomes `True`.
2. If 10027 persists despite config, implement runtime toolbar automation.
3. Add journal confirmation to distinguish “config applied” from “terminal
   actually allows trading”.

## 5. How to validate the solution

Automated coverage already exists as tracking tests in
`tests/e2e/test_trading.py`:

- `test_terminal_reports_trading_allowed`
  - Extracts `mt5.terminal_info().trade_allowed` server-side through
    `container.eval()`.
  - Asserts it is `True`.
  - Safe: places no order.
  - Note: scalar extraction through `container.eval()` intentionally avoids the
    #57 serialization path.

- `test_order_send_is_not_blocked_by_autotrading`
  - Marked `pytest.mark.trading`.
  - Skipped unless `MT5_E2E_ALLOW_ORDER_SEND=1`.
  - Places a minimum-volume market order, asserts retcode is not `10027`, then
    closes test positions.

Run the safe check:

```bash
.venv/bin/python -m pytest tests/e2e/test_trading.py::test_terminal_reports_trading_allowed -v
```

Run the real-order check only on an account where trading is acceptable:

```bash
MT5_E2E_ALLOW_ORDER_SEND=1 .venv/bin/python -m pytest tests/e2e/test_trading.py -v
```

Manual validation:

```python
# Safe check
allowed = mt5.container.eval("mt5.terminal_info().trade_allowed")
assert allowed is True

# Real order check (only where appropriate)
retcode = mt5.container.eval(f"mt5.order_send({request!r}).retcode")
assert retcode != 10027
```

Also verify the default remains data-only:

- Without the new opt-in variable, a fresh container must still report
  `trade_allowed is False` / preserve existing safe behavior.

## 6. Scope and non-goals

- This issue is about terminal/container trading enablement, not RPyC payload
  shape (#57) or engine selection (#50).
- Changing default behavior to always enable trading is explicitly out of scope;
  the requested fix is opt-in.
- Broker-side rejections other than `10027` are separate issues.

## 7. Related files and tests

- `docker/src/config.sh`: `apply_mt5_config`, `[Experts] Enabled=0`
- `docker/src/automation.sh`: login/server-search automation; no trading automation
- `docker/src/env.sh`, `docker/src/main.sh`, `docker/docker-compose.yml`
- `mt5linux/_container_manager.py`, `mt5linux/_docker_runtime.py`
- `tests/e2e/test_trading.py`
- `tests/e2e/helpers.py`: `SYMBOL`
- Related: #57 (result-type handling for `order_send()` responses)
