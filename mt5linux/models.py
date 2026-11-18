"""Pydantic 2 models for mt5linux.

Type-safe models for MetaTrader5 trading data structures.
Compatible with neptor's MT5Bridge models.

Hierarchy Level: 2
- Imports: MT5Constants (Level 0), MT5Settings (Level 1)
- Used by: client.py, server.py (optional)

Usage:

    # Create order request
    request = MT5Models.OrderRequest(...)

    # Parse MT5 response
    result = MT5Models.OrderResult.from_mt5(response)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Self, cast

from pydantic import BaseModel, ConfigDict, Field

from mt5linux.grpc_constants import MT5Constants as c
from mt5linux.settings import MT5Settings

# Default config instance for model defaults
_settings = MT5Settings()

if TYPE_CHECKING:
    from collections.abc import Callable


def _mt5_record_dict(obj: object) -> dict[str, object] | None:
    """Return namedtuple-like MT5 record data without direct private access."""
    as_dict = getattr(obj, "_asdict", None)
    if not callable(as_dict):
        return None
    return dict(cast("Callable[[], dict[str, object]]", as_dict)())


class MT5Models:
    """Container for all MT5 Pydantic models.

    All models are nested for clean namespace:
    - Base: Base class for MT5 data models
    - OrderRequest: Order request with validation
    - OrderResult: Order execution result
    - AccountInfo: Account information
    - SymbolInfo: Symbol information
    - Position: Open position
    - Tick: Price tick
    """

    class Base(BaseModel):
        """Base class for MT5 data models.

        Provides a generic `from_mt5()` factory method that handles:
        - None input (returns None)
        - Objects with `_asdict()` method (namedtuples)
        - Objects with attributes (MT5 objects)

        Subclasses can override `from_mt5()` for custom handling.
        """

        model_config = ConfigDict(frozen=True, from_attributes=True)

        @classmethod
        def from_mt5(cls, obj: object) -> Self | None:
            """Create model from MT5 object.

            Args:
                obj: MT5 object, namedtuple, or dict.

            Returns:
                Model instance or None if obj is None.

            """
            if obj is None:
                return None
            # Check for real namedtuple (_asdict returns actual dict)
            result = _mt5_record_dict(obj)
            if result is not None:
                return cls.model_validate(result)
            # Use from_attributes for objects with direct attribute access
            return cls.model_validate(obj)

    class OrderRequest(BaseModel):
        """MT5 order request with validation.

        Example:
            >>> request = MT5Models.OrderRequest(
            ...     action=c.Order.TradeAction.DEAL,
            ...     symbol="EURUSD",
            ...     volume=0.1,
            ...     type=c.Order.OrderType.BUY,
            ...     price=1.1000,
            ... )
            >>> mt5.order_send(request.to_mt5_request())

        """

        model_config = ConfigDict(frozen=True, use_enum_values=True)

        action: c.Order.TradeAction
        symbol: str
        volume: float = Field(gt=0, le=1000)
        type: c.Order.OrderType
        price: float = Field(ge=0, default=0.0)
        sl: float = Field(ge=0, default=0.0)
        tp: float = Field(ge=0, default=0.0)
        deviation: int = Field(ge=0, default=_settings.order_deviation)
        magic: int = Field(ge=0, default=_settings.order_magic)
        comment: str = Field(max_length=31, default="")
        type_time: int = Field(default=_settings.order_time)
        expiration: datetime | None = None
        type_filling: int = Field(default=_settings.order_filling)
        position: int = Field(ge=0, default=0)
        position_by: int = Field(ge=0, default=0)

        @property
        def is_market_order(self) -> bool:
            """Check if this is a market order."""
            market_types = {
                c.Order.OrderType.BUY,
                c.Order.OrderType.SELL,
            }
            return self.type in market_types

        def to_mt5_request(self) -> dict[str, int | float | str]:
            """Export to MT5 API format.

            Returns:
                Dict with only non-default, non-zero values for optional fields.

            """
            d: dict[str, int | float | str] = {
                "action": self.action,
                "symbol": self.symbol,
                "volume": self.volume,
                "type": self.type,
                "price": self.price,
                "deviation": self.deviation,
                "magic": self.magic,
                "comment": self.comment,
                "type_time": self.type_time,
                "type_filling": self.type_filling,
            }
            if self.sl > 0:
                d["sl"] = self.sl
            if self.tp > 0:
                d["tp"] = self.tp
            if self.position > 0:
                d["position"] = self.position
            if self.position_by > 0:
                d["position_by"] = self.position_by
            if self.expiration:
                d["expiration"] = int(self.expiration.timestamp())
            return d

    class OrderResult(Base):
        """MT5 order execution result.

        Example:
            >>> result = mt5.order_send(request)
            >>> order_result = MT5Models.OrderResult.from_mt5(result)
            >>> if order_result.is_success:
            ...     print(f"Order placed: {order_result.order}")

        """

        retcode: int
        deal: int = 0
        order: int = 0
        volume: float = 0.0
        price: float = 0.0
        bid: float = 0.0
        ask: float = 0.0
        comment: str = ""
        request_id: int = 0
        retcode_external: int = 0

        @property
        def is_success(self) -> bool:
            """Check if order was successful."""
            return self.retcode == c.Order.TradeRetcode.DONE

        @property
        def is_partial(self) -> bool:
            """Check if order was partially filled."""
            return self.retcode == c.Order.TradeRetcode.DONE_PARTIAL

        @classmethod
        def from_mt5(cls, obj: object) -> Self | None:
            """Create from MT5 OrderSendResult.

            Special handling: returns error result instead of None for None input.

            Args:
                obj: MT5 OrderSendResult object or dict.

            Returns:
                OrderResult instance (error result if input is None).

            """
            if obj is None:
                return cls(
                    retcode=c.Order.TradeRetcode.ERROR,
                    comment="No result from MT5",
                )
            return super().from_mt5(obj)

    class OrderCheckResult(Base):
        """MT5 order check result.

        Result of order_check() which validates an order without sending it.
        Contains information about margin requirements and feasibility.

        Example:
            >>> result = mt5.order_check(request)
            >>> check_result = MT5Models.OrderCheckResult.from_mt5(result)
            >>> if check_result.is_valid:
            ...     print(f"Order is valid, required margin: {check_result.margin}")

        """

        retcode: int
        balance: float = 0.0
        equity: float = 0.0
        profit: float = 0.0
        margin: float = 0.0
        margin_free: float = 0.0
        margin_level: float = 0.0
        comment: str = ""

        @property
        def is_valid(self) -> bool:
            """Check if order check passed validation."""
            return self.retcode == c.Order.TradeRetcode.DONE

        @classmethod
        def from_mt5(cls, obj: object) -> Self | None:
            """Create from MT5 OrderCheckResult.

            Args:
                obj: MT5 OrderCheckResult object or dict.

            Returns:
                OrderCheckResult instance or None if input is None.

            """
            if obj is None:
                return None
            return super().from_mt5(obj)

    class AccountInfo(Base):
        """MT5 account information (28 fields, positional order from real MT5)."""

        # Positional order matching real MT5 namedtuple
        login: int  # 0: Required field
        trade_mode: int = 0  # 1
        leverage: int = 0  # 2
        limit_orders: int = 0  # 3
        margin_so_mode: int = 0  # 4
        trade_allowed: bool = False  # 5
        trade_expert: bool = False  # 6
        margin_mode: int = 0  # 7
        currency_digits: int = 2  # 8
        fifo_close: bool = False  # 9
        balance: float = 0.0  # 10
        credit: float = 0.0  # 11
        profit: float = 0.0  # 12
        equity: float = 0.0  # 13
        margin: float = 0.0  # 14
        margin_free: float = 0.0  # 15
        margin_level: float = 0.0  # 16
        margin_so_call: float = 0.0  # 17
        margin_so_so: float = 0.0  # 18
        margin_initial: float = 0.0  # 19
        margin_maintenance: float = 0.0  # 20
        assets: float = 0.0  # 21
        liabilities: float = 0.0  # 22
        commission_blocked: float = 0.0  # 23
        name: str = ""  # 24
        server: str = ""  # 25
        currency: str = "USD"  # 26
        company: str = ""  # 27

    class CurrentAccount(Base):
        """Unified "who am I" view of a container's account (mt5linux extension).

        Combines connection/health state with the live account so a caller can
        answer "which broker/login is this mt5docker container on" -- and still
        get host/port + connected=False when the terminal is not logged in.
        """

        host: str
        port: int
        connected: bool = False
        trade_allowed: bool = False
        build: int | None = None
        login: int | None = None
        server: str | None = None
        company: str | None = None
        name: str | None = None
        balance: float | None = None
        currency: str | None = None

    class ProvisionedAccount(Base):
        """The account a container provisioned, recovered from auto_demo.json.

        Lets a client recover an AUTO-created demo's identity (login/server/email)
        even when the terminal is offline. The password is never included;
        `connected` is the live terminal state.
        """

        login: int = 0
        server: str = ""
        email: str = ""
        created_at: str = ""
        login_confirmed: bool = False
        credentials_persisted: bool = False
        connected: bool = False
        source: str = ""

    class CreateDemoSpec(Base):
        """Parameters for create_demo_account() (maps 1:1 to the bridge request).

        Empty fields fall back to the wizard defaults server-side. The common ask
        is server/email/phone; name + birth-year have sensible defaults.
        """

        server: str = ""
        email: str = ""
        phone: str = ""
        first_name: str = ""
        last_name: str = ""
        dob_year: str = ""

    class SymbolInfo(Base):
        """MT5 symbol information (complete 96 fields from real MT5)."""

        # Core identification
        name: str
        description: str = ""
        path: str = ""
        isin: str = ""
        bank: str = ""
        page: str = ""
        category: str = ""
        exchange: str = ""
        formula: str = ""
        basis: str = ""

        # Currency
        currency_base: str = ""
        currency_profit: str = ""
        currency_margin: str = ""

        # Selection/Visibility
        visible: bool = False
        select: bool = False
        custom: bool = False

        # Time
        time: int = 0
        start_time: int = 0
        expiration_time: int = 0

        # Digits/Spread
        digits: int = 0
        spread: int = 0
        spread_float: bool = False

        # Trade mode/settings
        trade_mode: int = 0
        trade_calc_mode: int = 0
        trade_stops_level: int = 0
        trade_freeze_level: int = 0
        trade_exemode: int = 0
        chart_mode: int = 0
        filling_mode: int = 0
        expiration_mode: int = 0
        order_mode: int = 0
        order_gtc_mode: int = 0

        # Option fields
        option_mode: int = 0
        option_right: int = 0
        option_strike: float = 0.0

        # Prices - current
        bid: float = 0.0
        ask: float = 0.0
        last: float = 0.0

        # Prices - high/low
        bidhigh: float = 0.0
        bidlow: float = 0.0
        askhigh: float = 0.0
        asklow: float = 0.0
        lasthigh: float = 0.0
        lastlow: float = 0.0

        # Price change/volatility
        price_change: float = 0.0
        price_volatility: float = 0.0
        price_theoretical: float = 0.0
        price_sensitivity: float = 0.0

        # Greeks
        price_greeks_delta: float = 0.0
        price_greeks_gamma: float = 0.0
        price_greeks_theta: float = 0.0
        price_greeks_vega: float = 0.0
        price_greeks_rho: float = 0.0
        price_greeks_omega: float = 0.0

        # Point/Tick
        point: float = 0.0
        trade_tick_value: float = 0.0
        trade_tick_value_profit: float = 0.0
        trade_tick_value_loss: float = 0.0
        trade_tick_size: float = 0.0
        ticks_bookdepth: int = 0

        # Contract
        trade_contract_size: float = 0.0
        trade_face_value: float = 0.0
        trade_accrued_interest: float = 0.0
        trade_liquidity_rate: float = 0.0

        # Volume
        volume: float = 0.0
        volume_real: float = 0.0
        volume_min: float = 0.0
        volume_max: float = 0.0
        volume_step: float = 0.0
        volume_limit: float = 0.0
        volumehigh: float = 0.0
        volumehigh_real: float = 0.0
        volumelow: float = 0.0
        volumelow_real: float = 0.0

        # Margin
        margin_initial: float = 0.0
        margin_maintenance: float = 0.0
        margin_hedged: float = 0.0
        margin_hedged_use_leg: bool = False

        # Swap
        swap_mode: int = 0
        swap_long: float = 0.0
        swap_short: float = 0.0
        swap_rollover3days: int = 0

        # Session data
        session_volume: float = 0.0
        session_turnover: float = 0.0
        session_interest: float = 0.0
        session_deals: float = 0.0
        session_buy_orders: float = 0.0
        session_buy_orders_volume: float = 0.0
        session_sell_orders: float = 0.0
        session_sell_orders_volume: float = 0.0
        session_open: float = 0.0
        session_close: float = 0.0
        session_aw: float = 0.0
        session_price_settlement: float = 0.0
        session_price_limit_min: float = 0.0
        session_price_limit_max: float = 0.0

    class Position(Base):
        """MT5 open position."""

        ticket: int
        time: int = 0
        time_msc: int = 0
        time_update: int = 0
        time_update_msc: int = 0
        type: int = 0
        magic: int = 0
        identifier: int = 0
        reason: int = 0
        volume: float = 0.0
        price_open: float = 0.0
        sl: float = 0.0
        tp: float = 0.0
        price_current: float = 0.0
        swap: float = 0.0
        profit: float = 0.0
        symbol: str = ""
        comment: str = ""
        external_id: str = ""

    class Tick(Base):
        """MT5 price tick."""

        time: int
        bid: float = 0.0
        ask: float = 0.0
        last: float = 0.0
        volume: int = 0
        time_msc: int = 0
        flags: int = 0
        volume_real: float = 0.0

    class Order(Base):
        """MT5 pending order information.

        Represents orders in the pending state (not yet executed).
        Also used for historical orders via history_orders_get().
        """

        ticket: int
        time_setup: int = 0
        time_setup_msc: int = 0
        time_done: int = 0
        time_done_msc: int = 0
        time_expiration: int = 0
        type: int = 0
        type_time: int = 0
        type_filling: int = 0
        state: int = 0
        magic: int = 0
        position_id: int = 0
        position_by_id: int = 0
        reason: int = 0
        volume_initial: float = 0.0
        volume_current: float = 0.0
        price_open: float = 0.0
        sl: float = 0.0
        tp: float = 0.0
        price_current: float = 0.0
        price_stoplimit: float = 0.0
        symbol: str = ""
        comment: str = ""
        external_id: str = ""

    class Deal(Base):
        """MT5 historical deal information.

        Represents executed trades from history_deals_get().
        """

        ticket: int
        order: int = 0
        time: int = 0
        time_msc: int = 0
        type: int = 0
        entry: int = 0
        magic: int = 0
        position_id: int = 0
        reason: int = 0
        volume: float = 0.0
        price: float = 0.0
        commission: float = 0.0
        swap: float = 0.0
        profit: float = 0.0
        fee: float = 0.0
        symbol: str = ""
        comment: str = ""
        external_id: str = ""

    class BookEntry(Base):
        """MT5 market depth (DOM) entry.

        Represents a single entry from market_book_get().
        Fields match real MT5 BookInfo: price, type, volume, volume_dbl
        """

        price: float = 0.0
        type: int  # Required field
        volume: float = 0.0
        volume_dbl: float = 0.0

    class TerminalInfo(Base):
        """MT5 terminal information.

        Represents terminal state from terminal_info().
        Contains connection status, permissions, and path information.
        """

        community_account: bool = False
        community_connection: bool = False
        connected: bool = False
        dlls_allowed: bool = False
        trade_allowed: bool = False
        tradeapi_disabled: bool = False
        email_enabled: bool = False
        ftp_enabled: bool = False
        notifications_enabled: bool = False
        mqid: bool = False
        build: int = 0
        maxbars: int = 0
        codepage: int = 0
        ping_last: int = 0
        community_balance: float = 0.0
        retransmission: float = 0.0
        company: str = ""
        name: str = ""
        language: str = ""
        path: str = ""
        data_path: str = ""
        commondata_path: str = ""


m = MT5Models
