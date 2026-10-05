"""Client-side typed classes for MetaTrader5 results.

The MetaTrader5 package defines its result types (TerminalInfo, AccountInfo,
SymbolInfo, ...) inside a C extension, where pickle cannot look them up by
module. Obtaining them across RPyC therefore fails with PicklingError
(issue #57). ``ContainerManager.eval()`` converts them server-side into
plain tagged structures (``_mt5linux_to_plain``, installed by
``_container_manager``) and reconstructs them into these classes with
``materialize()``.

The classes mirror the parts of the namedtuple API that user code relies on:

- ``_fields``: tuple of field names, in declaration order
- ``_asdict()``: mapping of field name to value (backwards compatibility)
- iteration/unpacking: yields the field values, in declaration order

``tests/e2e/test_serialization.py`` checks the field lists dynamically
against the currently running MetaTrader5 package version, so a version
drift is reported instead of silently corrupting results.
"""

import warnings
from collections.abc import Iterator
from dataclasses import dataclass
from typing import ClassVar

MT5_TYPE_TAG = "__mt5linux_type__"


class MT5Record:
    """Base class providing the namedtuple-like API for typed records."""

    _fields: ClassVar[tuple] = ()

    def _asdict(self) -> dict:
        """Return the fields as a dict, like namedtuple._asdict()."""
        return {name: getattr(self, name) for name in self._fields}

    def __iter__(self) -> Iterator:
        """Iterate over the field values, like a namedtuple."""
        return iter(getattr(self, name) for name in self._fields)


@dataclass(frozen=True)
class TerminalInfo(MT5Record):
    """Result of MetaTrader5 ``terminal_info()``."""

    community_account: bool
    community_connection: bool
    connected: bool
    dlls_allowed: bool
    trade_allowed: bool
    tradeapi_disabled: bool
    email_enabled: bool
    ftp_enabled: bool
    notifications_enabled: bool
    mqid: bool
    build: int
    maxbars: int
    codepage: int
    ping_last: int
    community_balance: float
    retransmission: float
    company: str
    name: str
    language: str
    path: str
    data_path: str
    commondata_path: str

    _fields = (
        "community_account",
        "community_connection",
        "connected",
        "dlls_allowed",
        "trade_allowed",
        "tradeapi_disabled",
        "email_enabled",
        "ftp_enabled",
        "notifications_enabled",
        "mqid",
        "build",
        "maxbars",
        "codepage",
        "ping_last",
        "community_balance",
        "retransmission",
        "company",
        "name",
        "language",
        "path",
        "data_path",
        "commondata_path",
    )


@dataclass(frozen=True)
class AccountInfo(MT5Record):
    """Result of MetaTrader5 ``account_info()``."""

    login: int
    trade_mode: int
    leverage: int
    limit_orders: int
    margin_so_mode: int
    trade_allowed: bool
    trade_expert: bool
    margin_mode: int
    currency_digits: int
    fifo_close: bool
    balance: float
    credit: float
    profit: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    margin_so_call: float
    margin_so_so: float
    margin_initial: float
    margin_maintenance: float
    assets: float
    liabilities: float
    commission_blocked: float
    name: str
    server: str
    currency: str
    company: str

    _fields = (
        "login",
        "trade_mode",
        "leverage",
        "limit_orders",
        "margin_so_mode",
        "trade_allowed",
        "trade_expert",
        "margin_mode",
        "currency_digits",
        "fifo_close",
        "balance",
        "credit",
        "profit",
        "equity",
        "margin",
        "margin_free",
        "margin_level",
        "margin_so_call",
        "margin_so_so",
        "margin_initial",
        "margin_maintenance",
        "assets",
        "liabilities",
        "commission_blocked",
        "name",
        "server",
        "currency",
        "company",
    )


@dataclass(frozen=True)
class SymbolInfo(MT5Record):
    """Result of MetaTrader5 ``symbol_info()`` / ``symbols_get()`` items."""

    custom: bool
    chart_mode: int
    select: bool
    visible: bool
    session_deals: int
    session_buy_orders: int
    session_sell_orders: int
    volume: int
    volumehigh: int
    volumelow: int
    time: int
    digits: int
    spread: int
    spread_float: bool
    ticks_bookdepth: int
    trade_calc_mode: int
    trade_mode: int
    start_time: int
    expiration_time: int
    trade_stops_level: int
    trade_freeze_level: int
    trade_exemode: int
    swap_mode: int
    swap_rollover3days: int
    margin_hedged_use_leg: bool
    expiration_mode: int
    filling_mode: int
    order_mode: int
    order_gtc_mode: int
    option_mode: int
    option_right: int
    bid: float
    bidhigh: float
    bidlow: float
    ask: float
    askhigh: float
    asklow: float
    last: float
    lasthigh: float
    lastlow: float
    volume_real: float
    volumehigh_real: float
    volumelow_real: float
    option_strike: float
    point: float
    trade_tick_value: float
    trade_tick_value_profit: float
    trade_tick_value_loss: float
    trade_tick_size: float
    trade_contract_size: float
    trade_accrued_interest: float
    trade_face_value: float
    trade_liquidity_rate: float
    volume_min: float
    volume_max: float
    volume_step: float
    volume_limit: float
    swap_long: float
    swap_short: float
    margin_initial: float
    margin_maintenance: float
    session_volume: float
    session_turnover: float
    session_interest: float
    session_buy_orders_volume: float
    session_sell_orders_volume: float
    session_open: float
    session_close: float
    session_aw: float
    session_price_settlement: float
    session_price_limit_min: float
    session_price_limit_max: float
    margin_hedged: float
    price_change: float
    price_volatility: float
    price_theoretical: float
    price_greeks_delta: float
    price_greeks_theta: float
    price_greeks_gamma: float
    price_greeks_vega: float
    price_greeks_rho: float
    price_greeks_omega: float
    price_sensitivity: float
    basis: str
    category: str
    currency_base: str
    currency_profit: str
    currency_margin: str
    bank: str
    description: str
    exchange: str
    formula: str
    isin: str
    name: str
    page: str
    path: str

    _fields = (
        "custom",
        "chart_mode",
        "select",
        "visible",
        "session_deals",
        "session_buy_orders",
        "session_sell_orders",
        "volume",
        "volumehigh",
        "volumelow",
        "time",
        "digits",
        "spread",
        "spread_float",
        "ticks_bookdepth",
        "trade_calc_mode",
        "trade_mode",
        "start_time",
        "expiration_time",
        "trade_stops_level",
        "trade_freeze_level",
        "trade_exemode",
        "swap_mode",
        "swap_rollover3days",
        "margin_hedged_use_leg",
        "expiration_mode",
        "filling_mode",
        "order_mode",
        "order_gtc_mode",
        "option_mode",
        "option_right",
        "bid",
        "bidhigh",
        "bidlow",
        "ask",
        "askhigh",
        "asklow",
        "last",
        "lasthigh",
        "lastlow",
        "volume_real",
        "volumehigh_real",
        "volumelow_real",
        "option_strike",
        "point",
        "trade_tick_value",
        "trade_tick_value_profit",
        "trade_tick_value_loss",
        "trade_tick_size",
        "trade_contract_size",
        "trade_accrued_interest",
        "trade_face_value",
        "trade_liquidity_rate",
        "volume_min",
        "volume_max",
        "volume_step",
        "volume_limit",
        "swap_long",
        "swap_short",
        "margin_initial",
        "margin_maintenance",
        "session_volume",
        "session_turnover",
        "session_interest",
        "session_buy_orders_volume",
        "session_sell_orders_volume",
        "session_open",
        "session_close",
        "session_aw",
        "session_price_settlement",
        "session_price_limit_min",
        "session_price_limit_max",
        "margin_hedged",
        "price_change",
        "price_volatility",
        "price_theoretical",
        "price_greeks_delta",
        "price_greeks_theta",
        "price_greeks_gamma",
        "price_greeks_vega",
        "price_greeks_rho",
        "price_greeks_omega",
        "price_sensitivity",
        "basis",
        "category",
        "currency_base",
        "currency_profit",
        "currency_margin",
        "bank",
        "description",
        "exchange",
        "formula",
        "isin",
        "name",
        "page",
        "path",
    )


@dataclass(frozen=True)
class Tick(MT5Record):
    """Result of MetaTrader5 ``symbol_info_tick()``."""

    time: int
    bid: float
    ask: float
    last: float
    volume: int
    time_msc: int
    flags: int
    volume_real: float

    _fields = (
        "time",
        "bid",
        "ask",
        "last",
        "volume",
        "time_msc",
        "flags",
        "volume_real",
    )


@dataclass(frozen=True)
class BookInfo(MT5Record):
    """Item of MetaTrader5 ``market_book_get()`` (Market Depth entry)."""

    type: int
    price: float
    volume: int
    volume_dbl: float

    _fields = ("type", "price", "volume", "volume_dbl")


@dataclass(frozen=True)
class TradeRequest(MT5Record):
    """Trading request echoed inside OrderCheckResult/OrderSendResult."""

    action: int
    magic: int
    order: int
    symbol: str
    volume: float
    price: float
    stoplimit: float
    sl: float
    tp: float
    deviation: int
    type: int
    type_filling: int
    type_time: int
    expiration: int
    comment: str
    position: int
    position_by: int

    _fields = (
        "action",
        "magic",
        "order",
        "symbol",
        "volume",
        "price",
        "stoplimit",
        "sl",
        "tp",
        "deviation",
        "type",
        "type_filling",
        "type_time",
        "expiration",
        "comment",
        "position",
        "position_by",
    )


@dataclass(frozen=True)
class OrderCheckResult(MT5Record):
    """Result of MetaTrader5 ``order_check()``."""

    retcode: int
    balance: float
    equity: float
    profit: float
    margin: float
    margin_free: float
    margin_level: float
    comment: str
    request: TradeRequest

    _fields = (
        "retcode",
        "balance",
        "equity",
        "profit",
        "margin",
        "margin_free",
        "margin_level",
        "comment",
        "request",
    )


@dataclass(frozen=True)
class OrderSendResult(MT5Record):
    """Result of MetaTrader5 ``order_send()``."""

    retcode: int
    deal: int
    order: int
    volume: float
    price: float
    bid: float
    ask: float
    comment: str
    request_id: int
    retcode_external: int
    request: TradeRequest

    _fields = (
        "retcode",
        "deal",
        "order",
        "volume",
        "price",
        "bid",
        "ask",
        "comment",
        "request_id",
        "retcode_external",
        "request",
    )


@dataclass(frozen=True)
class TradeOrder(MT5Record):
    """Item of MetaTrader5 ``orders_get()`` / ``history_orders_get()``."""

    ticket: int
    time_setup: int
    time_setup_msc: int
    time_done: int
    time_done_msc: int
    time_expiration: int
    type: int
    type_time: int
    type_filling: int
    state: int
    magic: int
    position_id: int
    position_by_id: int
    reason: int
    volume_current: float
    volume_initial: float
    price_open: float
    price_stoplimit: float
    sl: float
    tp: float
    price_current: float
    symbol: str
    comment: str
    external_id: str

    _fields = (
        "ticket",
        "time_setup",
        "time_setup_msc",
        "time_done",
        "time_done_msc",
        "time_expiration",
        "type",
        "type_time",
        "type_filling",
        "state",
        "magic",
        "position_id",
        "position_by_id",
        "reason",
        "volume_current",
        "volume_initial",
        "price_open",
        "price_stoplimit",
        "sl",
        "tp",
        "price_current",
        "symbol",
        "comment",
        "external_id",
    )


@dataclass(frozen=True)
class TradePosition(MT5Record):
    """Item of MetaTrader5 ``positions_get()``."""

    ticket: int
    time: int
    time_msc: int
    time_update: int
    time_update_msc: int
    position_id: int
    magic: int
    identifier: int
    reason: int
    type: int
    volume: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    swap: float
    profit: float
    symbol: str
    comment: str
    external_id: str

    _fields = (
        "ticket",
        "time",
        "time_msc",
        "time_update",
        "time_update_msc",
        "position_id",
        "magic",
        "identifier",
        "reason",
        "type",
        "volume",
        "price_open",
        "sl",
        "tp",
        "price_current",
        "swap",
        "profit",
        "symbol",
        "comment",
        "external_id",
    )


@dataclass(frozen=True)
class TradeDeal(MT5Record):
    """Item of MetaTrader5 ``history_deals_get()``."""

    ticket: int
    order: int
    time: int
    time_msc: int
    type: int
    entry: int
    magic: int
    position_id: int
    reason: int
    volume: float
    price: float
    commission: float
    swap: float
    profit: float
    fee: float
    symbol: str
    comment: str
    external_id: str

    _fields = (
        "ticket",
        "order",
        "time",
        "time_msc",
        "type",
        "entry",
        "magic",
        "position_id",
        "reason",
        "volume",
        "price",
        "commission",
        "swap",
        "profit",
        "fee",
        "symbol",
        "comment",
        "external_id",
    )


MT5_TYPES: dict[str, type[MT5Record]] = {
    "TerminalInfo": TerminalInfo,
    "AccountInfo": AccountInfo,
    "SymbolInfo": SymbolInfo,
    "Tick": Tick,
    "BookInfo": BookInfo,
    "TradeRequest": TradeRequest,
    "OrderCheckResult": OrderCheckResult,
    "OrderSendResult": OrderSendResult,
    "TradeOrder": TradeOrder,
    "TradePosition": TradePosition,
    "TradeDeal": TradeDeal,
}


def materialize(plain):
    """Reconstruct typed MT5 records from a plain tagged structure.

    Mirrors ``_mt5linux_to_plain`` (server side): tagged dicts become the
    corresponding MT5Record class, sequences are converted recursively.

    Unknown extra fields (a MetaTrader5 version newer than these classes)
    are dropped with a warning; missing fields fail loudly so the classes
    can be updated.
    """
    if isinstance(plain, dict):
        tag = plain.get(MT5_TYPE_TAG)
        data = {key: value for key, value in plain.items() if key != MT5_TYPE_TAG}
        if not isinstance(tag, str):
            return {key: materialize(value) for key, value in plain.items()}
        cls = MT5_TYPES.get(tag)
        if cls is None:
            return {key: materialize(value) for key, value in data.items()}
        unknown = set(data) - set(cls._fields)
        if unknown:
            warnings.warn(
                f"MetaTrader5 {tag} has unknown fields {sorted(unknown)}: "
                "update mt5linux.types",
            )
            data = {key: value for key, value in data.items() if key in cls._fields}
        return cls(**{key: materialize(value) for key, value in data.items()})
    if isinstance(plain, (list, tuple)):
        return type(plain)(materialize(item) for item in plain)
    return plain
