"""MetaTrader5 synchronous client for mt5linux.

Thin synchronous wrapper around AsyncMetaTrader5.
All business logic, resilience, and gRPC handling is in async_client.py.

Features:
- Synchronous API matching MetaTrader5 PyPI exactly
- Delegates ALL logic to AsyncMetaTrader5
- Inherits resilience: CircuitBreaker, auto-reconnect, health monitoring
- Context manager support (__enter__, __exit__)
- Thread-safe via asyncio event loop isolation

Example:
    >>> from mt5linux import MetaTrader5
    >>> with MetaTrader5(host="localhost", port=50051) as mt5:
    ...     mt5.initialize(login=12345, password="pass", server="Demo")
    ...     account = mt5.account_info()
    ...     rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_H1, 0, 100)

Compatible with grpcio 1.60+ and Python 3.13+.

"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Self

from mt5linux import generated_pb2 as mt5_pb2
from mt5linux.async_client import AsyncMetaTrader5
from mt5linux.protocols import MT5Protocol
from mt5linux.settings import MT5Settings

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from datetime import datetime
    from types import TracebackType

    from mt5linux.grpc_types import MT5Types as t
    from mt5linux.models import MT5Models

log = logging.getLogger(__name__)

# Default config instance - Single Source of Truth
_settings = MT5Settings()


class MetaTrader5(MT5Protocol):
    """Synchronous MetaTrader5 client - wraps AsyncMetaTrader5.

    All operations delegate to AsyncMetaTrader5 and run synchronously.
    Inherits all resilience features: CircuitBreaker, auto-reconnect, etc.

    Implements MT5Protocol (32 methods matching MetaTrader5 PyPI exactly).

    Note: connect(), disconnect(), health_check(), is_connected are mt5linux
    extensions NOT part of the MT5Protocol (not in MetaTrader5 PyPI).

    Attributes:
        TIMEFRAME_M1, TIMEFRAME_H1, etc.: MT5 timeframe constants (via __getattr__)
        ORDER_TYPE_BUY, ORDER_TYPE_SELL, etc.: MT5 order type constants

    """

    def __init__(
        self,
        host: str = _settings.host,
        port: int = _settings.grpc_port,
        timeout: int = _settings.timeout_connection,
    ) -> None:
        """Initialize sync MT5 client.

        Args:
            host: gRPC server address.
            port: gRPC server port.
            timeout: Timeout in seconds for MT5 operations.

        """
        self._async_client = AsyncMetaTrader5(host=host, port=port, timeout=timeout)
        self._loop: asyncio.AbstractEventLoop | None = None

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop for sync operations."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
        return self._loop

    def _run[T](self, coro: Coroutine[object, object, T]) -> T:
        """Run async coroutine synchronously.

        Args:
            coro: Coroutine to execute.

        Returns:
            Result of the coroutine.

        """
        loop = self._get_loop()
        return loop.run_until_complete(coro)

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to gRPC server."""
        return self._async_client.is_connected

    def __getattr__(self, name: str) -> int:
        """Get MT5 constants (TIMEFRAME_H1, ORDER_TYPE_BUY, etc).

        Args:
            name: Constant name to retrieve.

        Returns:
            Integer value of the constant.

        Raises:
            AttributeError: If constant not found.

        """
        # Delegate to async client for constants
        return getattr(self._async_client, name)

    def __enter__(self) -> Self:
        """Context manager entry - connects to gRPC server."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit - disconnects from gRPC server."""
        self.disconnect()

    # =========================================================================
    # CONNECTION METHODS
    # =========================================================================

    def connect(self) -> None:
        """Connect to gRPC server."""
        self._run(self._async_client.connect())

    def disconnect(self) -> None:
        """Disconnect from gRPC server.

        Note: The event loop is NOT closed here to allow reconnection.
        The loop will be cleaned up when the instance is garbage collected.
        """
        self._run(self._async_client.disconnect())

    # =========================================================================
    # INTROSPECTION METHODS (mt5linux extensions for testing)
    # =========================================================================

    def get_methods(self) -> list[dict[str, object]]:
        """Get method information from the real MetaTrader5 module.

        Introspects the MetaTrader5 PyPI module running on the server to
        extract method signatures. Used for protocol validation tests.

        Returns:
            List of method info dicts with keys:
            - name: Method name
            - parameters: List of parameter dicts
            - return_type: Return type annotation
            - is_callable: True if callable

        Raises:
            ConnectionError: If not connected.

        """

        async def _async_impl() -> list[dict[str, object]]:
            stub = self._async_client.ensure_connected()
            response = await stub.GetMethods(mt5_pb2.Empty())

            methods: list[dict[str, object]] = []
            for method in response.methods:
                params: list[dict[str, object]] = [
                    {
                        "name": param.name,
                        "type_hint": param.type_hint,
                        "kind": param.kind,
                        "has_default": param.has_default,
                        "default_value": param.default_value,
                    }
                    for param in method.parameters
                ]
                methods.append(
                    {
                        "name": method.name,
                        "parameters": params,
                        "return_type": method.return_type,
                        "is_callable": method.is_callable,
                    }
                )

            return methods

        return self._run(_async_impl())

    def get_models(self) -> list[dict[str, object]]:
        """Get model (namedtuple) information from the real MetaTrader5 module.

        Introspects the MetaTrader5 PyPI module running on the server to
        extract namedtuple structures. Used for model validation tests.

        Returns:
            List of model info dicts with keys:
            - name: Model name (e.g., "AccountInfo", "SymbolInfo")
            - fields: List of field dicts with name, type_hint, index
            - is_namedtuple: True if namedtuple

        Raises:
            ConnectionError: If not connected.

        """

        async def _async_impl() -> list[dict[str, object]]:
            stub = self._async_client.ensure_connected()
            response = await stub.GetModels(mt5_pb2.Empty())

            models: list[dict[str, object]] = []
            for model in response.models:
                fields: list[dict[str, object]] = [
                    {
                        "name": field.name,
                        "type_hint": field.type_hint,
                        "index": field.index,
                    }
                    for field in model.fields
                ]
                models.append(
                    {
                        "name": model.name,
                        "fields": fields,
                        "is_namedtuple": model.is_namedtuple,
                    }
                )

            return models

        return self._run(_async_impl())

    # =========================================================================
    # TERMINAL METHODS
    # =========================================================================

    def initialize(
        self,
        path: str | None = None,
        login: int | None = None,
        password: str | None = None,
        server: str | None = None,
        timeout: int | None = None,
        *,
        portable: bool = False,
    ) -> bool:
        """Initialize MT5 terminal connection.

        Auto-connects to gRPC server if not already connected.

        Args:
            path: Path to MT5 terminal executable.
            login: Trading account number.
            password: Account password.
            server: Trade server name.
            timeout: Connection timeout in milliseconds.
            portable: Use portable mode.

        Returns:
            True if initialization successful, False otherwise.

        """
        return self._run(
            self._async_client.initialize(
                path=path,
                login=login,
                password=password,
                server=server,
                timeout=timeout,
                portable=portable,
            )
        )

    def login(
        self,
        login: int,
        password: str | None = None,
        server: str | None = None,
        timeout: int = 60000,
    ) -> bool:
        """Login to MT5 account.

        Args:
            login: Trading account number.
            password: Account password.
            server: Trade server name.
            timeout: Login timeout in milliseconds.

        Returns:
            True if login successful, False otherwise.

        """
        return self._run(
            self._async_client.login(
                login=login,
                password=password,
                server=server,
                timeout=timeout,
            )
        )

    def shutdown(self) -> None:
        """Shutdown MT5 terminal connection."""
        self._run(self._async_client.shutdown())

    def health_check(self) -> dict[str, bool | int | str]:
        """Check MT5 service health status.

        Returns:
            Dict with health status fields.

        """
        return self._run(self._async_client.health_check())

    def version(self) -> tuple[int, int, str] | None:
        """Get MT5 terminal version.

        Returns:
            Tuple of (major, minor, build_string) or None.

        """
        return self._run(self._async_client.version())

    def last_error(self) -> tuple[int, str]:
        """Get last error code and description.

        Returns:
            Tuple of (error_code, error_message).

        """
        return self._run(self._async_client.last_error())

    def terminal_info(self) -> MT5Models.TerminalInfo | None:
        """Get terminal information.

        Returns:
            TerminalInfo object or None.

        """
        return self._run(self._async_client.terminal_info())

    def account_info(self) -> MT5Models.AccountInfo | None:
        """Get account information.

        Returns:
            AccountInfo object or None.

        """
        return self._run(self._async_client.account_info())

    def current_account(self) -> MT5Models.CurrentAccount:
        """Report which broker/login this container is on (mt5linux extension).

        Returns host/port + connection state and, when connected, the live
        account (login/server/company/...). Works even when the terminal is not
        logged in (connected=False, account fields None).
        """
        return self._run(self._async_client.current_account())

    def recover_provisioned_account(self) -> MT5Models.ProvisionedAccount:
        """Recover the account this container provisioned (mt5linux extension).

        Returns the AUTO-created demo's identity (login/server/email) from the
        container's auto_demo.json, even when the terminal is offline.
        """
        return self._run(self._async_client.recover_provisioned_account())

    def create_demo_account(
        self,
        spec: MT5Models.CreateDemoSpec,
    ) -> MT5Models.ProvisionedAccount:
        """Create a fresh demo account at runtime from a CreateDemoSpec.

        Sends broker/email/phone/name to the bridge (which drives the MT5 demo
        wizard) and returns the provisioned account. Long-running.
        """
        return self._run(self._async_client.create_demo_account(spec))

    # =========================================================================
    # SYMBOL METHODS
    # =========================================================================

    def symbols_total(self) -> int:
        """Get total number of available symbols.

        Returns:
            Total count of symbols.

        """
        return self._run(self._async_client.symbols_total())

    def symbols_get(
        self, group: str | None = None
    ) -> tuple[MT5Models.SymbolInfo, ...] | None:
        """Get available symbols with optional group filter.

        Args:
            group: Optional group filter pattern.

        Returns:
            Tuple of SymbolInfo objects or None.

        """
        return self._run(self._async_client.symbols_get(group=group))

    def symbol_info(self, symbol: str) -> MT5Models.SymbolInfo | None:
        """Get detailed symbol information.

        Args:
            symbol: Symbol name (e.g., "EURUSD").

        Returns:
            SymbolInfo object or None.

        """
        return self._run(self._async_client.symbol_info(symbol))

    def symbol_info_tick(self, symbol: str) -> MT5Models.Tick | None:
        """Get current tick data for a symbol.

        Args:
            symbol: Symbol name (e.g., "EURUSD").

        Returns:
            Tick object or None.

        """
        return self._run(self._async_client.symbol_info_tick(symbol))

    def symbol_select(self, symbol: str, *, enable: bool = True) -> bool:
        """Select/deselect symbol in Market Watch.

        Args:
            symbol: Symbol name.
            enable: True to add, False to remove from Market Watch.

        Returns:
            True if successful, False otherwise.

        """
        return self._run(self._async_client.symbol_select(symbol, enable=enable))

    # =========================================================================
    # MARKET DATA METHODS
    # =========================================================================

    def copy_rates_from(
        self,
        symbol: str,
        timeframe: int,
        date_from: datetime | int,
        count: int,
    ) -> t.RatesArray | None:
        """Copy OHLCV rates from a specific date.

        Args:
            symbol: Symbol name.
            timeframe: Timeframe constant (e.g., TIMEFRAME_H1).
            date_from: Start date as datetime or Unix timestamp.
            count: Number of bars to copy.

        Returns:
            NumPy structured array with OHLCV data or None.

        """
        return self._run(
            self._async_client.copy_rates_from(symbol, timeframe, date_from, count)
        )

    def copy_rates_from_pos(
        self,
        symbol: str,
        timeframe: int,
        start_pos: int,
        count: int,
    ) -> t.RatesArray | None:
        """Copy OHLCV rates from a bar position.

        Args:
            symbol: Symbol name.
            timeframe: Timeframe constant.
            start_pos: Start position (0 = current bar).
            count: Number of bars to copy.

        Returns:
            NumPy structured array with OHLCV data or None.

        """
        return self._run(
            self._async_client.copy_rates_from_pos(symbol, timeframe, start_pos, count)
        )

    def copy_rates_range(
        self,
        symbol: str,
        timeframe: int,
        date_from: datetime | int,
        date_to: datetime | int,
    ) -> t.RatesArray | None:
        """Copy OHLCV rates in a date range.

        Args:
            symbol: Symbol name.
            timeframe: Timeframe constant.
            date_from: Start date as datetime or Unix timestamp.
            date_to: End date as datetime or Unix timestamp.

        Returns:
            NumPy structured array with OHLCV data or None.

        """
        return self._run(
            self._async_client.copy_rates_range(symbol, timeframe, date_from, date_to)
        )

    def copy_ticks_from(
        self,
        symbol: str,
        date_from: datetime | int,
        count: int,
        flags: int,
    ) -> t.TicksArray | None:
        """Copy tick data from a specific date.

        Args:
            symbol: Symbol name.
            date_from: Start date as datetime or Unix timestamp.
            count: Number of ticks to copy.
            flags: Copy ticks flags.

        Returns:
            NumPy structured array with tick data or None.

        """
        return self._run(
            self._async_client.copy_ticks_from(symbol, date_from, count, flags)
        )

    def copy_ticks_range(
        self,
        symbol: str,
        date_from: datetime | int,
        date_to: datetime | int,
        flags: int,
    ) -> t.TicksArray | None:
        """Copy tick data in a date range.

        Args:
            symbol: Symbol name.
            date_from: Start date as datetime or Unix timestamp.
            date_to: End date as datetime or Unix timestamp.
            flags: Copy ticks flags.

        Returns:
            NumPy structured array with tick data or None.

        """
        return self._run(
            self._async_client.copy_ticks_range(symbol, date_from, date_to, flags)
        )

    # =========================================================================
    # TRADING METHODS
    # =========================================================================

    def order_calc_margin(
        self,
        action: int,
        symbol: str,
        volume: float,
        price: float,
    ) -> float | None:
        """Calculate margin required for an order.

        Args:
            action: Trade action type.
            symbol: Symbol name.
            volume: Order volume in lots.
            price: Order price.

        Returns:
            Required margin or None.

        """
        return self._run(
            self._async_client.order_calc_margin(action, symbol, volume, price)
        )

    def order_calc_profit(
        self,
        action: int,
        symbol: str,
        volume: float,
        price_open: float,
        price_close: float,
    ) -> float | None:
        """Calculate potential profit for an order.

        Args:
            action: Trade action type.
            symbol: Symbol name.
            volume: Order volume in lots.
            price_open: Open price.
            price_close: Close price.

        Returns:
            Calculated profit or None.

        """
        return self._run(
            self._async_client.order_calc_profit(
                action, symbol, volume, price_open, price_close
            )
        )

    def order_check(self, request: dict[str, Any]) -> MT5Models.OrderCheckResult | None:
        """Check order validity without sending.

        Args:
            request: Order request dictionary.

        Returns:
            Order check result object or None if error occurs.

        """
        return self._run(self._async_client.order_check(request))

    def order_send(self, request: dict[str, Any]) -> MT5Models.OrderResult | None:
        """Send trading order to MT5.

        Args:
            request: Order request dictionary.

        Returns:
            Order execution result object or None.

        """
        return self._run(self._async_client.order_send(request))

    # =========================================================================
    # MT5LINUX EXTENSIONS - ASYNC ORDER METHODS
    # =========================================================================

    def order_send_async(
        self,
        request: dict[str, Any],
        on_complete: Callable[[MT5Models.OrderResult], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> str:
        """Send order asynchronously with callback notification.

        This is an mt5linux extension (not in MetaTrader5 PyPI).
        Returns immediately with request_id. Executes order in background.
        Calls on_complete(result) or on_error(exception) when done.

        Args:
            request: Order request dict (same format as order_send).
            on_complete: Callback called with OrderResult on success.
            on_error: Callback called with Exception on failure.

        Returns:
            request_id: Unique ID to track this order (also in WAL).

        Example:
            def handle_result(result):
                print(f"Order {result.order} executed: {result.retcode}")

            request_id = mt5.order_send_async(
                {"action": TRADE_ACTION_DEAL, "symbol": "EURUSD", ...},
                on_complete=handle_result,
            )
            print(f"Order queued: {request_id}")

        """
        return self._run(
            self._async_client.order_send_async(request, on_complete, on_error)
        )

    def order_send_batch(
        self,
        requests: list[dict[str, Any]],
        on_each_complete: Callable[[str, MT5Models.OrderResult], None] | None = None,
        on_each_error: Callable[[str, Exception], None] | None = None,
        on_all_complete: (
            Callable[[dict[str, MT5Models.OrderResult | Exception]], None] | None
        ) = None,
    ) -> list[str]:
        """Send multiple orders in parallel with batch callbacks.

        This is an mt5linux extension (not in MetaTrader5 PyPI).
        All orders execute SIMULTANEOUSLY (up to queue_max_concurrent).
        Each order gets individual callback, plus batch completion callback.

        Args:
            requests: List of order request dicts.
            on_each_complete: Called for each successful order (request_id, result).
            on_each_error: Called for each failed order (request_id, exception).
            on_all_complete: Called when ALL orders complete (dict of results).

        Returns:
            List of request_ids for all orders.

        Example:
            def on_each(rid, result):
                print(f"Order {rid}: {result.retcode}")

            def on_all(all_results):
                print(f"Batch complete: {len(all_results)} orders")

            request_ids = mt5.order_send_batch(
                [order1, order2, order3],
                on_each_complete=on_each,
                on_all_complete=on_all,
            )

        """
        return self._run(
            self._async_client.order_send_batch(
                requests, on_each_complete, on_each_error, on_all_complete
            )
        )

    # =========================================================================
    # POSITIONS METHODS
    # =========================================================================

    def positions_total(self) -> int:
        """Get total number of open positions.

        Returns:
            Count of open positions.

        """
        return self._run(self._async_client.positions_total())

    def positions_get(
        self,
        symbol: str | None = None,
        group: str | None = None,
        ticket: int | None = None,
    ) -> tuple[MT5Models.Position, ...] | None:
        """Get open positions with optional filters.

        Args:
            symbol: Filter by symbol name.
            group: Symbol group filter.
            ticket: Specific position ticket.

        Returns:
            Tuple of Position objects or None.

        """
        return self._run(
            self._async_client.positions_get(symbol=symbol, group=group, ticket=ticket)
        )

    # =========================================================================
    # ORDERS METHODS
    # =========================================================================

    def orders_total(self) -> int:
        """Get total number of pending orders.

        Returns:
            Count of pending orders.

        """
        return self._run(self._async_client.orders_total())

    def orders_get(
        self,
        symbol: str | None = None,
        group: str | None = None,
        ticket: int | None = None,
    ) -> tuple[MT5Models.Order, ...] | None:
        """Get pending orders with optional filters.

        Args:
            symbol: Filter by symbol name.
            group: Symbol group filter.
            ticket: Specific order ticket.

        Returns:
            Tuple of Order objects or None.

        """
        return self._run(
            self._async_client.orders_get(symbol=symbol, group=group, ticket=ticket)
        )

    # =========================================================================
    # HISTORY METHODS
    # =========================================================================

    def history_orders_total(
        self,
        date_from: datetime | int,
        date_to: datetime | int,
    ) -> int:
        """Get total count of historical orders in date range.

        Args:
            date_from: Start date.
            date_to: End date.

        Returns:
            Count of historical orders.

        """
        return self._run(self._async_client.history_orders_total(date_from, date_to))

    def history_orders_get(
        self,
        date_from: datetime | int | None = None,
        date_to: datetime | int | None = None,
        group: str | None = None,
        ticket: int | None = None,
        position: int | None = None,
    ) -> tuple[MT5Models.Order, ...] | None:
        """Get historical orders with filters.

        Args:
            date_from: Start date.
            date_to: End date.
            group: Symbol group filter.
            ticket: Specific order ticket.
            position: Position ID filter.

        Returns:
            Tuple of Order objects or None.

        """
        return self._run(
            self._async_client.history_orders_get(
                date_from=date_from,
                date_to=date_to,
                group=group,
                ticket=ticket,
                position=position,
            )
        )

    def history_deals_total(
        self,
        date_from: datetime | int,
        date_to: datetime | int,
    ) -> int:
        """Get total count of historical deals in date range.

        Args:
            date_from: Start date.
            date_to: End date.

        Returns:
            Count of historical deals.

        """
        return self._run(self._async_client.history_deals_total(date_from, date_to))

    def history_deals_get(
        self,
        date_from: datetime | int | None = None,
        date_to: datetime | int | None = None,
        group: str | None = None,
        ticket: int | None = None,
        position: int | None = None,
    ) -> tuple[MT5Models.Deal, ...] | None:
        """Get historical deals with filters.

        Args:
            date_from: Start date.
            date_to: End date.
            group: Symbol group filter.
            ticket: Specific deal ticket.
            position: Position ID filter.

        Returns:
            Tuple of Deal objects or None.

        """
        return self._run(
            self._async_client.history_deals_get(
                date_from=date_from,
                date_to=date_to,
                group=group,
                ticket=ticket,
                position=position,
            )
        )

    # =========================================================================
    # MARKET DEPTH METHODS
    # =========================================================================

    def market_book_add(self, symbol: str) -> bool:
        """Subscribe to market depth (DOM) for a symbol.

        Args:
            symbol: Symbol name to subscribe to.

        Returns:
            True if subscription successful, False otherwise.

        """
        return self._run(self._async_client.market_book_add(symbol))

    def market_book_get(self, symbol: str) -> tuple[MT5Models.BookEntry, ...] | None:
        """Get market depth (DOM) data for a symbol.

        Args:
            symbol: Symbol name to get market depth for.

        Returns:
            Tuple of BookEntry objects or None.

        """
        return self._run(self._async_client.market_book_get(symbol))

    def market_book_release(self, symbol: str) -> bool:
        """Unsubscribe from market depth (DOM) for a symbol.

        Args:
            symbol: Symbol name to unsubscribe from.

        Returns:
            True if unsubscription successful, False otherwise.

        """
        return self._run(self._async_client.market_book_release(symbol))
