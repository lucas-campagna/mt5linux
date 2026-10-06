"""End-to-end coverage for issue #57 (RPyC serialization of MT5 results).

The MetaTrader5 result types (TerminalInfo, AccountInfo, SymbolInfo, ...) are
C-extension namedtuples that pickle cannot look up, so obtaining them across
RPyC fails with PicklingError. ContainerManager.eval() converts them
server-side and reconstructs the typed classes from mt5linux.types.

test_fields_match_current_mt5_version keeps the field lists in
mt5linux/types.py in sync with the running MetaTrader5 package version: it
fetches the field names dynamically from the server and compares them with
the local class definitions.

https://github.com/lucas-campagna/mt5linux/issues/57
"""

from datetime import datetime, timedelta, timezone
from pickle import PicklingError

import pytest

from mt5linux.types import (
    AccountInfo,
    OrderCheckResult,
    SymbolInfo,
    TerminalInfo,
    Tick,
    TradeDeal,
    TradeOrder,
    TradePosition,
    TradeRequest,
)

pytestmark = pytest.mark.e2e

ISSUE = "https://github.com/lucas-campagna/mt5linux/issues/57"

_SYMBOL_CACHE = {}


def _first_symbol(mt5_initialized):
    """First symbol name on the account (cached: symbols_get is slow)."""
    if "name" not in _SYMBOL_CACHE:
        _SYMBOL_CACHE["name"] = mt5_initialized.container.eval(
            "mt5.symbols_get()[0].name"
        )
    return _SYMBOL_CACHE["name"]


def _order_request(mt5_initialized, symbol):
    """A buy request for order_check() (non-mutating)."""
    ask = mt5_initialized.container.eval(
        f"mt5.symbol_info_tick({symbol!r}).ask"
    )
    return {
        "action": 1,
        "symbol": symbol,
        "volume": 0.01,
        "type": 0,
        "price": float(ask),
        "deviation": 20,
        "magic": 0,
        "comment": "mt5linux e2e (issue #57)",
        "type_time": 0,
        "type_filling": 2,
    }


FIELDS_CHECKS = [
    ("list(mt5.terminal_info()._asdict().keys())", TerminalInfo),
    ("list(mt5.account_info()._asdict().keys())", AccountInfo),
    ("list(mt5.symbols_get()[0]._asdict().keys())", SymbolInfo),
    ("list(mt5.symbol_info_tick({symbol!r})._asdict().keys())", Tick),
    ("list(mt5.order_check({request!r})._asdict().keys())", OrderCheckResult),
    (
        "list(mt5.order_check({request!r}).request._asdict().keys())",
        TradeRequest,
    ),
    (
        (
            "list(mt5.positions_get()[0]._asdict().keys()) "
            "if mt5.positions_get() else None"
        ),
        TradePosition,
    ),
    (
        (
            "list(mt5.orders_get()[0]._asdict().keys()) "
            "if mt5.orders_get() else None"
        ),
        TradeOrder,
    ),
    (
        (
            "list(mt5.history_orders_get({date_from!r}, {date_to!r})"
            "[0]._asdict().keys()) if mt5.history_orders_get("
            "{date_from!r}, {date_to!r}) else None"
        ),
        TradeOrder,
    ),
    (
        (
            "list(mt5.history_deals_get({date_from!r}, {date_to!r})"
            "[0]._asdict().keys()) if mt5.history_deals_get("
            "{date_from!r}, {date_to!r}) else None"
        ),
        TradeDeal,
    ),
]


@pytest.mark.parametrize(("template", "expected"), FIELDS_CHECKS)
def test_fields_match_current_mt5_version(mt5_initialized, template, expected):
    symbol = _first_symbol(mt5_initialized)
    request = _order_request(mt5_initialized, symbol)
    date_to = datetime.now(tz=timezone.utc)
    date_from = date_to - timedelta(days=90)
    expr = template.format(
        symbol=symbol,
        request=request,
        date_from=date_from,
        date_to=date_to,
    )
    remote_fields = mt5_initialized.container.eval(expr)
    if remote_fields is None:
        pytest.skip(f"no {expected.__name__} records on this account")
    assert tuple(remote_fields) == expected._fields, (
        f"{expected.__name__} is out of sync with the running MetaTrader5 "
        f"package: server={tuple(remote_fields)} local={expected._fields} "
        f"({ISSUE})"
    )


def test_terminal_info_returns_typed_record(mt5_initialized):
    info = mt5_initialized.terminal_info()

    assert isinstance(info, TerminalInfo), f"({ISSUE})"
    assert info.build > 0
    as_dict = info._asdict()
    assert as_dict["build"] == info.build


def test_account_info_returns_typed_record(mt5_initialized, mt5_credentials):
    info = mt5_initialized.account_info()

    assert isinstance(info, AccountInfo), f"({ISSUE})"
    assert info.login == mt5_credentials["login"]
    assert info._asdict()["login"] == info.login


def test_symbol_info_returns_typed_record(mt5_initialized):
    symbol = _first_symbol(mt5_initialized)

    info = mt5_initialized.symbol_info(symbol)

    assert isinstance(info, SymbolInfo), f"({ISSUE})"
    assert info.name == symbol


def test_symbol_info_tick_returns_typed_record(mt5_initialized):
    symbol = _first_symbol(mt5_initialized)

    tick = mt5_initialized.symbol_info_tick(symbol)

    assert isinstance(tick, Tick), f"({ISSUE})"
    assert tick.time > 0
    assert tick._asdict()["bid"] == tick.bid


def test_symbols_get_returns_typed_records(mt5_initialized):
    symbols = mt5_initialized.symbols_get()

    assert isinstance(symbols, tuple), f"({ISSUE})"
    assert len(symbols) > 0
    assert all(isinstance(symbol, SymbolInfo) for symbol in symbols), f"({ISSUE})"
    assert isinstance(symbols[0].name, str) and symbols[0].name


def _small_group(mt5_initialized):
    """A small symbol group (from the first symbol) to exercise the
    group argument forms without converting tens of thousands of symbols."""
    return f"*{_first_symbol(mt5_initialized)[:4]}*"


def test_symbols_get_positional_group_returns_typed_records(mt5_initialized):
    symbols = mt5_initialized.symbols_get(_small_group(mt5_initialized))

    assert isinstance(symbols, tuple), f"({ISSUE})"
    assert len(symbols) > 0
    assert all(isinstance(symbol, SymbolInfo) for symbol in symbols), f"({ISSUE})"


def test_symbols_get_keyword_group_returns_typed_records(mt5_initialized):
    symbols = mt5_initialized.symbols_get(group=_small_group(mt5_initialized))

    assert isinstance(symbols, tuple), f"({ISSUE})"
    assert len(symbols) > 0
    assert all(isinstance(symbol, SymbolInfo) for symbol in symbols), f"({ISSUE})"


def test_order_check_returns_typed_record_with_nested_request(mt5_initialized):
    symbol = _first_symbol(mt5_initialized)
    request = _order_request(mt5_initialized, symbol)

    result = mt5_initialized.order_check(request)

    assert isinstance(result, OrderCheckResult), f"({ISSUE})"
    assert isinstance(result.request, TradeRequest), f"({ISSUE})"
    assert result.request.symbol == symbol
    assert isinstance(result._asdict()["request"], TradeRequest)


def test_positions_and_orders_return_tuples(mt5_initialized):
    assert isinstance(mt5_initialized.positions_get(), tuple)
    assert isinstance(mt5_initialized.orders_get(), tuple)


class TestMaterializedFalse:
    """Regression tests for materialized=False (pre-issue-#57 behaviour).

    When materialized=False the client does NOT convert MT5 C-extension
    objects — PicklingError propagates up to the caller. This is the
    trade-off users accept when they set materialized=False: they get
    raw netrefs / plain dicts with the same serialisation limitations
    that existed before issue #57 was fixed.

    ALL MT5 C-extension result types (TerminalInfo, Tick, SymbolInfo,
    OrderCheckResult, etc.) raise PicklingError when materialized=False,
    because obtain() cannot cross them over RPyC. This is the correct
    behaviour for the pre-fix API contract.
    """

    def test_terminal_info_raises_pickling_error(
        self, mt5_unmaterialized_initialized
    ):
        with pytest.raises(PicklingError, match="TerminalInfo"):
            mt5_unmaterialized_initialized.terminal_info()

    def test_symbol_info_tick_raises_pickling_error(
        self, mt5_unmaterialized_initialized
    ):
        symbol = _first_symbol(mt5_unmaterialized_initialized)
        with pytest.raises(PicklingError, match="Tick"):
            mt5_unmaterialized_initialized.symbol_info_tick(symbol)

    def test_symbols_get_raises_pickling_error(
        self, mt5_unmaterialized_initialized
    ):
        with pytest.raises(PicklingError, match="SymbolInfo"):
            mt5_unmaterialized_initialized.symbols_get(
                _small_group(mt5_unmaterialized_initialized)
            )

    def test_order_check_raises_pickling_error(
        self, mt5_unmaterialized_initialized
    ):
        symbol = _first_symbol(mt5_unmaterialized_initialized)
        request = _order_request(mt5_unmaterialized_initialized, symbol)
        with pytest.raises(PicklingError, match="OrderCheckResult"):
            mt5_unmaterialized_initialized.order_check(request)
