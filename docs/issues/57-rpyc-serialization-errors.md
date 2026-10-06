# Issue #57 — RPyC Serialization Errors for MT5 Result Objects

## Table of Contents

1. [Issue Description](#issue-description)
2. [Symptoms](#symptoms)
3. [Root Cause Analysis](#root-cause-analysis)
4. [Affected Types](#affected-types)
5. [Solution](#solution)
6. [The `materialized` Feature Flag](#the-materialized-feature-flag)
7. [How It Works Internally](#how-it-works-internally)
8. [Validating the Fix](#validating-the-fix)
9. [Performance Implications](#performance-implications)
10. [Test Coverage](#test-coverage)
11. [Migration Guide](#migration-guide)

---

## Issue Description

**Issue:** [#57 — Standalone Wine server + RPyC serialization errors for TerminalInfo, AccountInfo and SymbolInfo](https://github.com/lucas-campagna/mt5linux/issues/57)

When using `mt5linux` with a standalone Wine/MT5 server (without Docker), any call that returns MT5 C-extension result objects — such as `terminal_info()`, `account_info()`, `symbols_get()`, `symbol_info_tick()`, `order_check()`, `order_send()` — raises a `PicklingError` at the RPyC layer:

```
_pickle.PicklingError: Can't pickle <class 'TerminalInfo'>: attribute lookup TerminalInfo on builtins failed
```

This error does **not** occur with the Docker runtime in older versions because RPyC could transfer the objects as netrefs within the same process. After upgrading to newer RPyC versions or when using the standalone Wine server, the netref path fails and pickle is attempted instead.

---

## Symptoms

The following call patterns all fail with `PicklingError`:

```python
from mt5linux import MetaTrader5

mt5 = MetaTrader5(host="192.168.1.100", port=18812)
mt5.initialize(login=1192081018, password="...", server="ClearInvestimentos-DEMO")

# All of these raise PicklingError:
terminal = mt5.terminal_info()
account  = mt5.account_info()
tick     = mt5.symbol_info_tick("EURUSD")
symbols  = mt5.symbols_get()
result   = mt5.order_check({...})
response = mt5.order_send({...})
positions = mt5.positions_get()  # even empty tuples fail
```

The error always mentions the MT5 type name (`TerminalInfo`, `SymbolInfo`, `Tick`, etc.) in the message.

---

## Root Cause Analysis

### Why Pickle Fails

Python's `pickle` protocol requires that every pickled class can be resolved by looking up its module and name in `sys.modules`. For example, when pickle encounters a `TerminalInfo` object, it tries to find `builtins.TerminalInfo` — but `TerminalInfo` is defined inside the MetaTrader5 C-extension DLL, not in any importable Python module.

MT5 result types are **C-extension namedtuples**. They have `_asdict()` and can be iterated, but they are not real `collections.namedtuple` instances and are not registered in any pickleable location.

```
MT5 DLL (C code)
  └── defines TerminalInfo, AccountInfo, SymbolInfo, Tick, ...
        └── these types are NOT in any Python module's namespace
              └── pickle.lookup("builtins", "TerminalInfo") → AttributeError
                    └── PicklingError raised
```

### Why RPyC Netrefs Don't Always Work

RPyC normally transfers complex objects as **netrefs** (network references) — a cheap pointer that the client dereferences on demand. For this to work, the server must be able to serialize the netref itself.

When the MT5 result object is returned from `mt5.terminal_info()`, RPyC on the server side attempts to serialize it. Depending on RPyC version and timing, it may try to pickle it (fails) instead of creating a netref (would work). This is why the Docker runtime sometimes worked before — the in-process RPyC connection handled it differently than a TCP connection to a standalone Wine server.

### Empty Tuples Also Fail

Even `positions_get()` returning an empty tuple `()` fails because RPyC may attempt to inspect its contents. This was part of the original bug report.

---

## Affected Types

The following MT5 C-extension types are affected. All are **C-extension namedtuples** with `_asdict()` but **no `_fields` attribute**:

| Type | Fields (verified) | Returned By |
|---|---|---|
| `TerminalInfo` | 22 | `terminal_info()` |
| `AccountInfo` | 28 | `account_info()` |
| `SymbolInfo` | 94 | `symbols_get()`, `symbol_info()` |
| `Tick` | 8 | `symbol_info_tick()` |
| `BookInfo` | 4 | `market_book_get()` |
| `TradeRequest` | 17 | `order_check().request`, `order_send().request` |
| `OrderCheckResult` | 9 | `order_check()` |
| `OrderSendResult` | 11 | `order_send()` |
| `TradeOrder` | 24 | `orders_get()`, `history_orders_get()` |
| `TradePosition` | 20 | `positions_get()`, `history_positions_get()` |
| `TradeDeal` | 18 | `history_deals_get()` |

**Note:** `copy_rates_*` and `copy_ticks_*` return **numpy structured arrays** — these are plain numpy objects and do **not** go through the RPyC pickle path. They work without any conversion.

---

## Solution

### Overview

The fix is implemented in two layers:

1. **Server-side** (`_container_manager.py`): At connect time, a helper function `_mt5linux_to_plain()` is installed in the container via `conn.execute()`. This function recursively converts MT5 C-extension objects into plain Python dicts tagged with the type name, all in a single server round-trip.

2. **Client-side** (`types.py` + `materialize()`): Tagged plain dicts are transferred to the client and reconstructed into frozen dataclass instances (`TerminalInfo`, `AccountInfo`, `SymbolInfo`, etc.) that match the MT5 API contract (`_asdict()`, `_fields`, `__iter__`).

### Architecture

```
Client                                    Server (MT5 Docker/Wine)
────────────────────────────────────────  ────────────────────────────────────────
MetaTrader5.eval(code)
  │
  │  raw = conn.eval(code)                mt5.terminal_info()
  │  ← returns MT5 C-extension object         (cannot cross RPyC alone)
  │
  │  try: obtain(raw)  ←── PicklingError!
  │
  │  if materialized:
  │    plain = obtain(__to_plain(raw))    _mt5linux_to_plain(obj)
  │    ← {"__MT5_TYPE__": "TerminalInfo",   └── recursively converts
  │        "build": 3331,                     C-ext objects → tagged dicts
  │        "name": "MetaTrader 5"}         in ONE server round-trip
  │
  │    return materialize(plain)           (no per-item round-trips)
  │    └── TerminalInfo(build=3331,
  │                     name="MetaTrader 5",
  │                     ...)
  │  else:
  │    raise PicklingError  # user opted out
```

### Key Design Decisions

- **Server-side conversion in one round-trip**: Converting `symbols_get()` with 49,809 symbols requires only ONE additional server call, not 49,809 calls. The helper converts all items server-side and returns a single pickleable structure.

- **Tagged dicts**: Each converted object is tagged with `__MT5_TYPE__` so the client knows which dataclass to instantiate.

- **Frozen dataclasses**: Chosen over namedtuples because:
  - MT5 types have `_asdict()` but no `_fields` (not real namedtuples)
  - Frozen provides immutability matching MT5's semantics
  - `__iter__` + `_fields` + `_asdict()` added for full API compatibility
  - Type annotations provide lint/IDE support

- **Unknown fields are dropped with a warning**: If a future MT5 version adds fields, existing code won't crash — it will log a warning and drop the unknown fields.

---

## The `materialized` Feature Flag

```python
class MetaTrader5:
    def __init__(self, ..., materialized: bool = True):
        """
        materialized: bool
            When True (default), MT5 result objects are reconstructed into
            typed frozen dataclasses from mt5linux.types, solving issue #57.
            When False, results are returned as plain dicts / netrefs
            without any reconstruction — the pre-fix behaviour.
        """
```

| Flag | Behaviour | Use Case |
|---|---|---|
| `materialized=True` (default) | Full conversion to typed dataclasses. Issue #57 solved. | Normal use |
| `materialized=False` | `PicklingError` propagates for C-extension results. Raw netrefs/dicts returned. | Debugging, custom pickling, migrating legacy code |

### Example

```python
from mt5linux import MetaTrader5

# Default: typed dataclasses (recommended)
mt5 = MetaTrader5(host="192.168.1.100", port=18812)
info = mt5.terminal_info()
assert isinstance(info, TerminalInfo)        # ✓
assert info.build == 3331                   # ✓
assert info._asdict()["build"] == 3331      # ✓ namedtuple compat

# Opt-out: raw behaviour (pre-fix)
mt5_legacy = MetaTrader5(host="192.168.1.100", port=18812, materialized=False)
try:
    info = mt5_legacy.terminal_info()       # raises PicklingError
except PicklingError:
    print("Expected — serialization not fixed in legacy mode")
```

---

## How It Works Internally

### 1. At Connection Time (`ContainerManager.__init__`)

```python
self.__to_plain = self._install_conversion_helper() if materialized else None
```

`_install_conversion_helper()` executes this code in the container:

```python
HELPER_CODE = '''
def _mt5linux_to_plain(obj):
    if hasattr(obj, "_asdict"):
        plain = {"__MT5_TYPE__": type(obj).__name__}
        for key, value in obj._asdict().items():
            plain[key] = _mt5linux_to_plain(value)
        return plain
    if isinstance(obj, dict):
        return {key: _mt5linux_to_plain(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_mt5linux_to_plain(item) for item in obj)
    return obj
'''
```

The helper is installed once and reused for all calls. If installation fails, `__to_plain` is `None`.

### 2. In `ContainerManager.eval()`

```python
def eval(self, code: str):
    raw = self.__conn.eval(code)
    try:
        return rpyc.classic.obtain(raw)           # fast path — works for primitives
    except PicklingError:
        if not self._materialized:
            raise                                 # user opted out
    if self.__to_plain is None:
        return raw                                # helper failed to install
    try:
        plain = rpyc.classic.obtain(self.__to_plain(raw))
    except Exception:                             # noqa: BLE001
        return raw
    return materialize(plain)
```

The fast `obtain()` path handles results that RPyC can already transfer (primitives, plain dicts, empty tuples). Only MT5 C-extension objects trigger the conversion path.

### 3. Client-Side Reconstruction (`materialize()`)

```python
def materialize(obj: dict | list | tuple) -> Any:
    if MT5_TYPE_TAG in obj:
        type_name = obj.pop(MT5_TYPE_TAG)
        cls = MT5_TYPES.get(type_name)
        if cls is None:
            warnings.warn(f"Unknown MT5 type: {type_name!r}; returning plain dict")
            return obj
        known_fields = set(cls._fields)
        received_fields = set(obj.keys())
        unknown = received_fields - known_fields
        if unknown:
            warnings.warn(f"Unknown fields for {type_name}: {unknown}; dropped")
        filtered = {k: obj[k] for k in known_fields if k in obj}
        return cls(**filtered)
    if isinstance(obj, dict):
        return {k: materialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(materialize(item) for item in obj)
    return obj
```

The `MT5_TYPES` registry maps type names to dataclass constructors:

```python
MT5_TYPES = {
    "TerminalInfo":    TerminalInfo,
    "AccountInfo":    AccountInfo,
    "SymbolInfo":     SymbolInfo,
    "Tick":           Tick,
    "BookInfo":       BookInfo,
    "TradeRequest":   TradeRequest,
    "OrderCheckResult": OrderCheckResult,
    "OrderSendResult": OrderSendResult,
    "TradeOrder":     TradeOrder,
    "TradePosition":  TradePosition,
    "TradeDeal":      TradeDeal,
}
```

---

## Validating the Fix

### Automated Tests

Run the full end-to-end suite:

```bash
# All e2e tests
pytest tests/e2e -v

# Serialization tests only
pytest tests/e2e/test_serialization.py -v

# Unit tests (no container needed)
pytest tests/test_types.py tests/test_01.py tests/test_order_check.py -v
```

**Expected results:**
- `tests/e2e/test_serialization.py` — **19 passed, 4 skipped** (no positions/orders/history data on demo account)
- `tests/e2e/test_serialization.py::TestMaterializedFalse` — **4 passed** (PicklingError propagates when `materialized=False`)
- Unit tests — **12 passed**

### Manual Verification

```python
from mt5linux import MetaTrader5, TerminalInfo, AccountInfo, SymbolInfo, Tick

mt5 = MetaTrader5(host="192.168.1.100", port=18812)
mt5.initialize(login=1192081018, password="...", server="ClearInvestimentos-DEMO")

# 1. Basic types
info = mt5.terminal_info()
assert isinstance(info, TerminalInfo), f"Expected TerminalInfo, got {type(info)}"
assert hasattr(info, "_fields")
assert hasattr(info, "_asdict")
assert info.build > 0

account = mt5.account_info()
assert isinstance(account, AccountInfo)
assert account.login == 1192081018

# 2. Namedtuple compatibility
assert info._asdict()["build"] == info.build
a, b, c = info  # __iter__ works
_ = tuple(info)  # tuple() works

# 3. Symbols (large result)
symbols = mt5.symbols_get()
assert isinstance(symbols, tuple)
assert len(symbols) > 0
assert all(isinstance(s, SymbolInfo) for s in symbols)
assert symbols[0]._asdict()["name"] == symbols[0].name

# 4. Tick
tick = mt5.symbol_info_tick("EURUSD")
assert isinstance(tick, Tick)
assert tick.bid > 0

# 5. Order check with nested TradeRequest
request = {
    "action":     1,       # TRADE_ACTION_DEAL
    "symbol":     "EURUSD",
    "volume":     0.1,
    "type":       0,       # ORDER_TYPE_BUY
    "price":      mt5.symbol_info_tick("EURUSD").bid,
    "deviation":  10,
    "magic":      0,
    "comment":    "test",
    "type_time":  0,       # ORDER_TIME_GTC
    "type_filling": 2,     # ORDER_FILLING_IOC
}
result = mt5.order_check(request)
assert isinstance(result, OrderCheckResult)
assert isinstance(result.request, TradeRequest)     # nested type reconstructed
assert result.request.symbol == "EURUSD"

# 6. Opt-out mode
mt5_legacy = MetaTrader5(host="192.168.1.100", port=18812, materialized=False)
try:
    mt5_legacy.terminal_info()
    assert False, "Should have raised PicklingError"
except PicklingError as e:
    print(f"Expected error: {e}")
```

### Dynamic Field Verification

The test `test_fields_match_current_mt5_version` fetches actual field names from the live MT5 server and compares them against `types.py`. This catches version drift automatically:

```bash
pytest tests/e2e/test_serialization.py -k fields -v
```

```
tests/e2e/test_serialization.py::test_fields_match_current_mt5_version[TerminalInfo] PASSED
tests/e2e/test_serialization.py::test_fields_match_current_mt5_version[AccountInfo] PASSED
tests/e2e/test_serialization.py::test_fields_match_current_mt5_version[SymbolInfo] PASSED
tests/e2e/test_serialization.py::test_fields_match_current_mt5_version[Tick] PASSED
tests/e2e/test_serialization.py::test_fields_match_current_mt5_version[OrderCheckResult] PASSED
tests/e2e/test_serialization.py::test_fields_match_current_mt5_version[TradeRequest] PASSED
```

If MT5 is updated and adds/removes fields, these tests will fail with a clear message showing which fields changed.

---

## Performance Implications

| Operation | Time (this broker, 49,809 symbols) |
|---|---|
| `mt5.symbols_get()` server-side build | ~30–60s (server-dependent, same as before) |
| + `_mt5linux_to_plain()` conversion | +5–15s (server-side, single pass) |
| + RPyC transfer (49,809 tagged dicts) | +5–10s (localhost, ~40–60 MB) |
| + `materialize()` client-side | +10–30s (49,809 dataclass instantiations) |
| **Total** | **~60–120s** |

For small result sets (terminal_info, account_info, tick, order_check) the overhead is negligible (<1s). The cost is dominated by the server-side MT5 call, not by the conversion layer.

For brokers with fewer symbols, the full `symbols_get()` round-trip is proportionally faster.

---

## Test Coverage

| Test File | Tests | What It Covers |
|---|---|---|
| `tests/test_types.py` | 12 | Unit tests for `materialize()` function |
| `tests/e2e/test_serialization.py::test_fields_match_*` | 6 | Dynamic field verification against live MT5 |
| `tests/e2e/test_serialization.py::test_*_returns_typed_record` | 9 | Typed reconstruction of all major result types |
| `tests/e2e/test_serialization.py::TestMaterializedFalse::*` | 4 | `materialized=False` opt-out path |
| `tests/e2e/test_initialization.py` | 2 | Initialization lifecycle |
| `tests/e2e/test_lifecycle.py` | 2 | Startup/shutdown lifecycle |
| `tests/e2e/test_standalone_engine.py` | 1 (skipped) | Standalone engine attach (blocked by #50) |
| `tests/e2e/test_trading.py` | 1 (skipped) | Algo trading enable (blocked by #51) |
| `tests/e2e/test_z_container_restart.py` | 1 (skipped) | Container restart (blocked by #55) |

**Gaps (not covered by current tests):**
- `market_book_get()` / `BookInfo` — requires a symbol with a market book subscription
- `order_send()` / `OrderSendResult` — blocked by #51 (AutoTrading disabled on demo)
- `copy_rates_*` / `copy_ticks_*` — these return numpy arrays, not MT5 C-ext types; they bypass the pickle path entirely

---

## Migration Guide

### For Existing Users

**No action required.** The default behaviour (`materialized=True`) is backward-compatible:

- Result objects still have `_asdict()` and `_fields` (namedtuple compatibility)
- Result objects are still iterable and can be unpacked
- `isinstance(result, tuple)` still returns `True` for tuple subtypes

```python
# Before (broken):
info = mt5.terminal_info()  # PicklingError

# After (fixed by default):
info = mt5.terminal_info()  # ✓ TerminalInfo instance
info._asdict()               # ✓ dict
info._fields                 # ✓ tuple of field names
a, b, c = info               # ✓ unpacking works
```

### For Users Who Need the Old Behaviour

If you were working around #57 by processing netrefs directly, or if you need `materialized=False` for other reasons:

```python
mt5 = MetaTrader5(host="...", port=18812, materialized=False)

# Now raises PicklingError as before — you handle it
try:
    info = mt5.terminal_info()
except PicklingError:
    print("Cannot cross RPyC — use Docker runtime or handle netref directly")
```

### For Library Authors

If you are wrapping `mt5linux`:

```python
# Support both modes
mt5 = MetaTrader5(..., materialized=self._use_dataclasses)
result = mt5.symbols_get()

# Your code works with both:
if self._use_dataclasses:
    assert isinstance(result[0], SymbolInfo)
    name = result[0].name
else:
    assert isinstance(result[0], dict)
    name = result[0]["name"]
```

---

## Related Issues

| Issue | Status | Relationship |
|---|---|---|
| [#57](https://github.com/lucas-campagna/mt5linux/issues/57) | **Open** | This issue — RPyC serialization of MT5 C-ext types |
| [#50](https://github.com/lucas-campagna/mt5linux/issues/50) | Open | Standalone Wine engine attach — blocks `test_standalone_engine.py` |
| [#51](https://github.com/lucas-campagna/mt5linux/issues/51) | Open | AutoTrading disabled — blocks `order_send()` / `OrderSendResult` test |
| [#55](https://github.com/lucas-campagna/mt5linux/issues/55) | Open | IPC timeout after 60s — blocks `test_z_container_restart.py` |
| [#4](https://github.com/lucas-campagna/mt5linux/issues/4) | Closed | `terminal_info` fail — likely same root cause, superseded by #57 |

---

*Last updated: October 2026 — verified against MetaTrader5 build 6092 (MT5 5.0.6092, 4 Aug 2026)*
