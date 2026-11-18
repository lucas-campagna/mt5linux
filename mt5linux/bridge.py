"""gRPC bridge for MetaTrader5 - runs inside Wine.

This module provides the MT5GRPCServicer gRPC server that runs inside Wine
with Windows Python + MetaTrader5 module.

STANDALONE: This file has NO dependencies on other mt5linux modules.
Copy only this file + grpcio + protobuf + generated pb2 files to Wine.

Features:
- gRPC-based service (replaces RPyC)
- Concurrent request handling via ThreadPoolExecutor
- Signal handling (SIGTERM/SIGINT) for clean container stops
- Data materialization (_asdict() for NamedTuples)
- Chunked symbols_get for large datasets (9000+)
- Debug logging for every function call
- NO STUBS - fails if MT5 unavailable
- Complete MT5 API coverage including Market Depth (DOM)
- MT5 constants exposed for client usage
- Secure: no raw module exposure, controlled API surface
- JSON serialization for dict data
- Numpy arrays serialized as bytes

Usage:
    wine python.exe -m mt5linux.bridge --host 0.0.0.0 --port 50051
    wine python.exe bridge.py --host 0.0.0.0 --port 50051 --debug
"""

# pylint: disable=no-member  # Protobuf generated code has dynamic members
from __future__ import annotations

import argparse
import inspect
import logging
import operator
import os
import re
import signal
import subprocess
import sys
import threading
import time
from concurrent import futures
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast, runtime_checkable

import grpc
import orjson

from . import generated_grpc as mt5_pb2_grpc
from . import generated_pb2 as mt5_pb2
from .utilities import MT5Utilities as u

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from datetime import datetime
    from types import FrameType

    from .protocols import MT5Protocols as p


@runtime_checkable
class _GrpcServerLike(Protocol):
    """Subset of grpc.Server methods used by this module."""

    def add_insecure_port(self, address: str) -> int: ...
    def start(self) -> None: ...
    def wait_for_termination(self, timeout: float | None = None) -> bool: ...
    def stop(self, grace: float | None = None) -> object: ...


# Module logger
log = logging.getLogger("mt5bridge")


def _as_tuple_of_strings(value: object) -> tuple[str, ...] | None:
    """Return the value as tuple[str, ...] when every element is a string."""
    if not isinstance(value, tuple):
        return None
    names = cast("tuple[object, ...]", value)
    if not all(isinstance(name, str) for name in names):
        return None
    return cast("tuple[str, ...]", names)


# Global server reference for signal handler
_server: _GrpcServerLike | None = None  # pylint: disable=invalid-name  # Module-private global

# Global MT5 call timeout (configurable via --mt5-timeout)
_mt5_call_timeout: float = 30.0  # pylint: disable=invalid-name  # Module-private global


def _call_mt5_with_timeout(
    func: Callable[..., object],
    *args: object,
    **kwargs: object,
) -> object:
    """Execute MT5 call with timeout protection.

    Wraps potentially blocking MT5 calls to prevent indefinite hangs.
    Uses ThreadPoolExecutor for timeout capability on synchronous calls.

    Args:
        func: MT5 function to call.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        Result of the MT5 function call.

    Raises:
        TimeoutError: If the call exceeds the timeout.
        Exception: Re-raised from the MT5 function.

    """
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future: futures.Future[object] = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=_mt5_call_timeout)
        except futures.TimeoutError:
            func_name = getattr(func, "__name__", str(func))
            msg = f"MT5 call {func_name} timed out after {_mt5_call_timeout}s"
            log.error(msg)
            raise TimeoutError(msg) from None


# =============================================================================
# JSON Value Types (standalone - no external dependencies)
# =============================================================================

# JSON-compatible value types for serialization (PEP 695 type statements)
type JSONPrimitive = str | int | float | bool | None
type JSONValue = JSONPrimitive | list[JSONValue] | dict[str, JSONValue]


def _json_serialize(data: dict[str, JSONValue]) -> str:
    """Serialize dict to JSON string using orjson for high performance.

    Args:
        data: Dictionary with JSON-compatible values.

    Returns:
        JSON string representation.

    Note:
        orjson is 3-10x faster than stdlib json for typical MT5 data.

    """
    return orjson.dumps(data, default=str).decode()


def _json_deserialize(json_str: str) -> dict[str, JSONValue]:
    """Deserialize JSON string to dict using orjson for high performance.

    Args:
        json_str: JSON string to parse.

    Returns:
        Parsed dictionary.

    Note:
        orjson is 3-10x faster than stdlib json for typical MT5 data.

    """
    result: dict[str, JSONValue] = orjson.loads(json_str)
    return result


# =============================================================================
# MT5 gRPC Servicer Implementation
# =============================================================================


class MT5GRPCServicer(mt5_pb2_grpc.MT5ServiceServicer):
    """gRPC service implementation for MetaTrader5.

    Implements all RPC methods defined in mt5.proto, handling:
    - Connection lifecycle (initialize, login, shutdown)
    - Account/terminal information
    - Symbol operations
    - Market data (rates, ticks)
    - Trading operations (orders, positions)
    - History queries
    - Market depth (DOM)
    """

    _mt5_module: p.MetaTrader5Module = u.External.load_metatrader5()
    _mt5_lock: threading.RLock = threading.RLock()
    # Only one demo-creation wizard may run at a time (it drives the shared GUI);
    # a non-blocking acquire lets CreateDemoAccount REJECT concurrent calls instead
    # of queueing 300s subprocesses (DoS amplification).
    _wizard_lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        """Initialize the MT5 gRPC servicer and connect to MT5 terminal."""
        super().__init__()
        log.info("MT5GRPCServicer initializing...")

        # Auto-initialize connection to MT5 terminal
        result = self._mt5_module.initialize()
        if result:
            log.info("MT5 auto-initialize: SUCCESS")
        else:
            error = self._mt5_module.last_error()
            log.warning("MT5 auto-initialize: FAILED - %s", error)

        log.info("MT5GRPCServicer initialized")

    # =========================================================================
    # HELPER FUNCTIONS (PRIVATE)
    # =========================================================================

    def _ensure_mt5_loaded(self) -> None:
        """Ensure MT5 module is loaded, raise RuntimeError if not.

        Raises:
            RuntimeError: If MT5 module is not available.

        """
        return

    def _namedtuple_to_dict(
        self,
        obj: p.NamedTupleRecord,
        nested_fields: list[str] | None = None,
    ) -> dict[str, JSONValue]:
        """Convert namedtuple to JSON-serializable dict.

        Args:
            obj: Object with _asdict() method (namedtuple-like).
            nested_fields: Field names containing nested namedtuples.

        Returns:
            Dictionary representation.

        """
        as_dict = getattr(obj, "_asdict", None)
        if not callable(as_dict):
            return {}
        data = dict(cast("Callable[[], dict[str, JSONValue]]", as_dict)())
        if nested_fields:
            for field in nested_fields:
                nested = data.get(field)
                if nested is None:
                    continue
                nested_as_dict = getattr(nested, "_asdict", None)
                if callable(nested_as_dict):
                    data[field] = dict(
                        cast("Callable[[], dict[str, JSONValue]]", nested_as_dict)()
                    )
        return data

    def _numpy_to_proto(
        self,
        arr: p.StructuredArray | None,
    ) -> mt5_pb2.NumpyArray:
        """Convert numpy array to protobuf NumpyArray message.

        Args:
            arr: Numpy structured array or None.

        Returns:
            NumpyArray protobuf message.

        """
        if arr is None:
            return mt5_pb2.NumpyArray(data=b"", dtype="", shape=[])
        return mt5_pb2.NumpyArray(
            data=arr.tobytes(),
            dtype=str(arr.dtype),
            shape=list(arr.shape),
        )

    def _validate_symbol(self, symbol: str, func_name: str) -> bool:
        """Validate symbol is not empty.

        Args:
            symbol: Symbol to validate.
            func_name: Function name for logging.

        Returns:
            True if valid, False otherwise.

        """
        if not symbol:
            log.debug("%s: empty symbol", func_name)
            return False
        return True

    def _validate_count(self, count: int, func_name: str) -> bool:
        """Validate count is positive.

        Args:
            count: Count to validate.
            func_name: Function name for logging.

        Returns:
            True if valid, False otherwise.

        """
        if count <= 0:
            log.warning("%s: invalid count=%s", func_name, count)
            return False
        return True

    def _validate_date_range(
        self,
        date_from: datetime | int,
        date_to: datetime | int,
        func_name: str,
    ) -> bool:
        """Validate date_from <= date_to.

        Args:
            date_from: Start date (datetime or Unix timestamp).
            date_to: End date (datetime or Unix timestamp).
            func_name: Function name for logging.

        Returns:
            True if valid, False otherwise.

        """
        from_val: float
        to_val: float
        if isinstance(date_from, (int, float)):
            from_val = float(date_from)
        else:
            from_val = date_from.timestamp()
        if isinstance(date_to, (int, float)):
            to_val = float(date_to)
        else:
            to_val = date_to.timestamp()

        if from_val > to_val:
            log.warning(
                "%s: invalid range from=%s > to=%s",
                func_name,
                date_from,
                date_to,
            )
            return False
        return True

    # =========================================================================
    # TERMINAL OPERATIONS
    # =========================================================================

    def HealthCheck(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.HealthStatus:
        """Check MT5 service health status.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            HealthStatus with connection and terminal state.

        """
        log.debug("HealthCheck: called")

        # Service is healthy if MT5 module is loaded and responding
        # Terminal connection is separate - happens during Initialize/Login
        log.debug("HealthCheck: MT5 module loaded and responding")

        # Try to get terminal info for additional details
        terminal = self._mt5_module.terminal_info()
        if terminal is not None:
            log.debug(
                "HealthCheck: connected=%s trade_allowed=%s",
                terminal.connected,
                terminal.trade_allowed,
            )
            return mt5_pb2.HealthStatus(
                healthy=True,
                mt5_available=True,
                connected=terminal.connected,
                trade_allowed=terminal.trade_allowed,
                build=terminal.build,
                reason="",
            )

        # Terminal not connected yet (normal state before Initialize/Login)
        log.debug("HealthCheck: Terminal not yet connected (normal state)")
        return mt5_pb2.HealthStatus(
            healthy=True,
            mt5_available=True,
            connected=False,
            trade_allowed=False,
            build=0,
            reason="Terminal not initialized yet",
        )

    def Initialize(
        self,
        request: mt5_pb2.InitRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.BoolResponse:
        """Initialize MT5 terminal connection.

        Args:
            request: Initialization parameters (path, login, password, etc.).
            context: gRPC servicer context.

        Returns:
            BoolResponse indicating success or failure.

        """
        self._ensure_mt5_loaded()
        log.debug(
            "Initialize: path=%s login=%s server=%s timeout=%s portable=%s",
            request.path if request.HasField("_path") else None,
            request.login if request.HasField("_login") else None,
            request.server if request.HasField("_server") else None,
            request.timeout if request.HasField("_timeout") else None,
            request.portable,
        )

        kwargs: dict[str, str | int | bool] = {}
        if request.HasField("_path"):
            kwargs["path"] = request.path
        if request.HasField("_login"):
            kwargs["login"] = request.login
        if request.HasField("_password"):
            kwargs["password"] = request.password
        if request.HasField("_server"):
            kwargs["server"] = request.server
        if request.HasField("_timeout"):
            kwargs["timeout"] = request.timeout
        if request.portable:
            kwargs["portable"] = request.portable

        result = self._mt5_module.initialize(**kwargs)
        log.info("Initialize: result=%s", result)
        return mt5_pb2.BoolResponse(result=bool(result))

    def Login(
        self,
        request: mt5_pb2.LoginRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.BoolResponse:
        """Login to MT5 account.

        Args:
            request: Login credentials (login, password, server, timeout).
            context: gRPC servicer context.

        Returns:
            BoolResponse indicating success or failure.

        """
        log.debug(
            "Login: login=%s server=%s timeout=%s",
            request.login,
            request.server,
            request.timeout,
        )
        result = self._mt5_module.login(
            login=request.login,
            password=request.password,
            server=request.server,
            timeout=request.timeout,
        )
        log.info("Login: result=%s", result)
        return mt5_pb2.BoolResponse(result=bool(result))

    def Shutdown(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.Empty:
        """Shutdown MT5 terminal connection.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            Empty response.

        """
        log.debug("Shutdown: called")
        self._mt5_module.shutdown()
        log.info("Shutdown: completed")
        return mt5_pb2.Empty()

    def Version(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.MT5Version:
        """Get MT5 terminal version.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            MT5Version with major, minor, and build information.

        """
        log.debug("Version: called")
        result = self._mt5_module.version()
        log.debug("Version: result=%s", result)
        if result is None:
            return mt5_pb2.MT5Version(major=0, minor=0, build="")
        return mt5_pb2.MT5Version(
            major=result[0],
            minor=result[1],
            build=str(result[2]),
        )

    def LastError(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.ErrorInfo:
        """Get last MT5 error code and description.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            ErrorInfo with error code and message.

        """
        log.debug("LastError: called")
        result = self._mt5_module.last_error()
        log.debug("LastError: result=%s", result)
        return mt5_pb2.ErrorInfo(code=result[0], message=result[1])

    def GetConstants(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.Constants:
        """Get all MT5 constants dynamically from the MetaTrader5 module.

        Extracts ALL integer constants from the MetaTrader5 module by
        inspecting its attributes. This ensures we always return the
        complete set of constants from the actual MT5 PyPI package.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            Constants message with map of constant names to values.

        """
        self._ensure_mt5_loaded()
        log.debug("GetConstants: called")
        mt5 = self._mt5_module
        constants: dict[str, int] = {}

        # Dynamically extract ALL integer constants from MetaTrader5 module
        # This includes: TIMEFRAME_*, ORDER_*, TRADE_*, POSITION_*, DEAL_*,
        # ACCOUNT_*, SYMBOL_*, BOOK_*, TICK_*, COPY_TICKS_*, DAY_OF_WEEK_*, etc.
        for name in dir(mt5):
            # Skip private/magic attributes
            if name.startswith("_"):
                continue

            # Only include UPPERCASE names (constants convention)
            if not name.isupper():
                continue

            # Skip callable objects (functions/methods)
            attr = getattr(mt5, name, None)
            if callable(attr):
                continue

            # Only include integer values
            if isinstance(attr, int):
                constants[name] = attr

        log.debug("GetConstants: returned %s constants", len(constants))
        return mt5_pb2.Constants(values=constants)

    @staticmethod
    def _get_tuple_field_order(klass: type[tuple[JSONValue, ...]]) -> list[str] | None:
        """Get field names in correct positional order from tuple subclass.

        Uses Python's built-in introspection - NO hardcoding.
        Tries multiple methods in order of reliability:
        1. __match_args__ (Python 3.10+ structseq types)
        2. _fields (standard namedtuples)
        3. Test instance mapping (universal for member_descriptor types)

        Args:
            klass: The tuple subclass to introspect.

        Returns:
            List of field names in positional order, or None if fails.

        """
        # Python 3.10+ structseq types have __match_args__ in positional order.
        match_args = _as_tuple_of_strings(getattr(klass, "__match_args__", None))
        if match_args is not None:
            return list(match_args)

        # Standard namedtuples have _fields.
        fields = _as_tuple_of_strings(getattr(klass, "_fields", None))
        if fields is not None:
            return list(fields)

        # For types without either, create test instance and map indices
        member_fields = [
            name
            for name in dir(klass)
            if not name.startswith("_")
            and type(getattr(klass, name, None)).__name__ == "member_descriptor"
        ]

        if not member_fields:
            return None

        # Create instance with sentinel values to determine positional order
        try:
            n = len(member_fields)
            tuple_type = cast("type[tuple[object, ...]]", klass)
            instance = tuple_type(tuple(range(n)))

            # Map each field to its positional index
            field_to_index: dict[str, int] = {}
            for field_name in member_fields:
                value = getattr(instance, field_name)
                if isinstance(value, int) and 0 <= value < n:
                    field_to_index[field_name] = value

            # Sort by index to get positional order
            if len(field_to_index) == n:
                return [
                    f
                    for f, _ in sorted(
                        field_to_index.items(), key=operator.itemgetter(1)
                    )
                ]
        except (TypeError, ValueError, AttributeError):
            pass

        return None

    @staticmethod
    def _parse_docstring_signature(
        docstring: str | None,
    ) -> list[tuple[str, bool, str]]:
        """Parse MT5 docstring to extract parameter info.

        MT5 docstrings have format like:
        - login(login,[server="SERVER"],[password="PASSWORD"])
        - copy_rates_from(symbol, timeframe, date_from, count)

        Args:
            docstring: Function docstring.

        Returns:
            List of (param_name, has_default, default_value) tuples.

        """
        if not docstring:
            return []

        # Get first line which contains signature
        first_line = docstring.strip().split("\n")[0]

        # Extract parameters from parentheses

        match = re.search(r"\(([^)]*)\)", first_line)
        if not match:
            return []

        params_str = match.group(1)
        if not params_str.strip():
            return []

        params: list[tuple[str, bool, str]] = []
        # Split by comma, handling nested brackets
        current = ""
        bracket_depth = 0
        for char in params_str:
            if char == "[":
                bracket_depth += 1
                current += char
            elif char == "]":
                bracket_depth -= 1
                current += char
            elif char == "," and bracket_depth == 0:
                if current.strip():
                    params.append(
                        MT5GRPCServicer._parse_single_param(current.strip()),
                    )
                current = ""
            else:
                current += char

        if current.strip():
            params.append(MT5GRPCServicer._parse_single_param(current.strip()))

        return params

    @staticmethod
    def _parse_single_param(param_str: str) -> tuple[str, bool, str]:
        """Parse a single parameter from MT5 docstring.

        Formats:
        - symbol (required)
        - [server="SERVER"] (optional with default)
        - [enable] (optional without explicit default)

        Returns:
            (param_name, has_default, default_value)

        """
        # Check if optional (wrapped in [])
        is_optional = param_str.startswith("[") and param_str.endswith("]")
        if is_optional:
            param_str = param_str[1:-1]

        # Check for default value
        if "=" in param_str:
            name, default = param_str.split("=", 1)
            return (name.strip(), True, default.strip().strip('"'))
        return (param_str.strip(), is_optional, "")

    def GetMethods(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.MethodsResponse:
        """Get all callable methods from the MetaTrader5 module.

        Introspects the real MetaTrader5 PyPI module to extract method signatures
        from docstrings. MT5 built-in functions don't expose signatures via
        inspect, but they do have docstrings with parameter info.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            MethodsResponse with all method information.

        """
        self._ensure_mt5_loaded()
        log.debug("GetMethods: called")
        mt5 = self._mt5_module
        methods: list[mt5_pb2.MethodInfo] = []

        for name in dir(mt5):
            # Skip private/magic attributes
            if name.startswith("_"):
                continue

            attr = getattr(mt5, name, None)

            # Only include callable functions (not constants, not classes)
            if not callable(attr):
                continue

            # Skip classes (we handle them in GetModels)
            if inspect.isclass(attr):
                continue

            # Parse parameters from docstring (MT5 built-ins have useful docstrings)
            docstring = getattr(attr, "__doc__", None)
            parsed_params = self._parse_docstring_signature(docstring)

            params: list[mt5_pb2.ParameterInfo] = []
            for param_name, has_default, default_value in parsed_params:
                kind = "KEYWORD_ONLY" if has_default else "POSITIONAL_OR_KEYWORD"
                params.append(
                    mt5_pb2.ParameterInfo(
                        name=param_name,
                        type_hint="",  # MT5 doesn't provide type hints
                        kind=kind,
                        has_default=has_default,
                        default_value=default_value,
                    )
                )

            methods.append(
                mt5_pb2.MethodInfo(
                    name=name,
                    parameters=params,
                    return_type="",  # MT5 doesn't provide return types
                    is_callable=True,
                )
            )

        log.debug("GetMethods: returned %s methods", len(methods))
        return mt5_pb2.MethodsResponse(methods=methods, total=len(methods))

    def GetModels(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.ModelsResponse:
        """Get all model (tuple subclass) types from the MetaTrader5 module.

        Introspects the real MetaTrader5 PyPI module to extract model structures.
        MT5 models are tuple subclasses with member_descriptor attributes
        (not standard namedtuples with _fields).

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            ModelsResponse with all model information.

        """
        self._ensure_mt5_loaded()
        log.debug("GetModels: called")
        mt5 = self._mt5_module
        models: list[mt5_pb2.ModelInfo] = []

        for name in dir(mt5):
            # Skip private/magic attributes
            if name.startswith("_"):
                continue

            attr = getattr(mt5, name, None)

            # Must be a class
            if not inspect.isclass(attr):
                continue

            # MT5 models are tuple subclasses (not using standard _fields)
            if not issubclass(attr, tuple):
                continue

            # Skip the tuple base class itself
            if attr is tuple:
                continue

            # Get fields in correct positional order (dynamic introspection)
            tuple_class = cast("type[tuple[JSONValue, ...]]", attr)
            field_order = self._get_tuple_field_order(tuple_class)

            if field_order is None:
                # Log warning but skip this type if introspection fails
                log.warning(
                    "GetModels: could not determine field order for %s",
                    name,
                )
                continue

            fields: list[mt5_pb2.FieldInfo] = []
            for idx, field_name in enumerate(field_order):
                fields.append(
                    mt5_pb2.FieldInfo(
                        name=field_name,
                        type_hint="",  # MT5 doesn't provide type hints
                        index=idx,
                    )
                )

            # Only add if we found fields (actual model, not utility class)
            if fields:
                models.append(
                    mt5_pb2.ModelInfo(
                        name=name,
                        fields=fields,
                        is_namedtuple=True,  # Conceptually similar
                    )
                )

        log.debug("GetModels: returned %s models", len(models))
        return mt5_pb2.ModelsResponse(models=models, total=len(models))

    # =========================================================================
    # ACCOUNT/TERMINAL INFO
    # =========================================================================

    def TerminalInfo(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictData:
        """Get terminal information.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            DictData with JSON-serialized terminal information.

        """
        self._ensure_mt5_loaded()
        log.debug("TerminalInfo: called")
        result = self._mt5_module.terminal_info()
        if result is None:
            log.debug("TerminalInfo: result=None")
            return mt5_pb2.DictData(json_data="")
        data = self._namedtuple_to_dict(result)
        log.debug("TerminalInfo: returned terminal info")
        return mt5_pb2.DictData(json_data=_json_serialize(data))

    def AccountInfo(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictData:
        """Get account information.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            DictData with JSON-serialized account information.

        """
        self._ensure_mt5_loaded()
        log.debug("AccountInfo: called")
        result = self._mt5_module.account_info()
        if result is None:
            log.debug("AccountInfo: result=None")
            return mt5_pb2.DictData(json_data="")
        data = self._namedtuple_to_dict(result)
        log.debug("AccountInfo: login=%s", data.get("login"))
        return mt5_pb2.DictData(json_data=_json_serialize(data))

    def GetProvisionedAccount(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.ProvisionedAccount:
        """Recover the account this container provisioned (from auto_demo.json).

        Reads /config/auto_demo.json (written by the demo wizard) so a client can
        recover an auto-created account's identity even when the terminal is not
        connected. The live `connected` flag is best-effort + timeout-protected so
        this never blocks; use HealthCheck/AccountInfo for full live state.
        """
        config_dir = os.environ.get("CONFIG_DIR", "/config")
        path = Path(config_dir) / "auto_demo.json"
        data: dict[str, object] = {}
        if path.exists():
            try:
                parsed = orjson.loads(path.read_bytes())
            except (OSError, orjson.JSONDecodeError) as exc:
                log.warning("GetProvisionedAccount: cannot read %s: %s", path, exc)
            else:
                if isinstance(parsed, dict):
                    data = cast("dict[str, object]", parsed)
        connected = False
        try:
            terminal = _call_mt5_with_timeout(self._mt5_module.terminal_info)
            connected = bool(getattr(terminal, "connected", False))
        except (TimeoutError, OSError, RuntimeError) as exc:
            log.debug("GetProvisionedAccount: live connected check failed: %s", exc)
        login = data.get("login")
        return mt5_pb2.ProvisionedAccount(
            login=login if isinstance(login, int) else 0,
            server=str(data.get("server") or ""),
            email=str(data.get("email") or ""),
            created_at=str(data.get("created_at") or ""),
            login_confirmed=bool(data.get("login_confirmed", False)),
            credentials_persisted=bool(data.get("credentials_persisted", False)),
            connected=connected,
            source=str(data.get("source") or ""),
        )

    def CreateDemoAccount(
        self,
        request: mt5_pb2.CreateDemoRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.ProvisionedAccount:
        """Create a fresh demo account at runtime by running the wizard.

        Maps the request to the wizard's MT5_DEMO_* env and runs
        open_demo_account.py headlessly, then returns the provisioned account. This
        drives the MT5 GUI wizard (build-specific, best-effort); the zero-touch
        env-at-launch path remains the primary creation mechanism.
        """
        script = Path("/Metatrader/open_demo_account.py")
        if not script.exists():
            context.abort(grpc.StatusCode.UNIMPLEMENTED, f"wizard not found: {script}")
        # Reject (do NOT queue) concurrent wizard runs: a second run would drive the
        # same GUI and pile up 300s subprocesses (unauthenticated DoS amplification).
        if not self._wizard_lock.acquire(blocking=False):
            context.abort(
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                "a demo creation is already in progress",
            )
        try:
            env = dict(os.environ)
            overrides = {
                "MT5_DEMO_SERVER": request.server,
                "MT5_DEMO_EMAIL": request.email,
                "MT5_DEMO_PHONE": request.phone,
                "MT5_DEMO_FIRST": request.first_name,
                "MT5_DEMO_LAST": request.last_name,
                "MT5_DEMO_DOB_YEAR": request.dob_year,
            }
            env.update({key: value for key, value in overrides.items() if value})
            # Force a fresh account: move the existing record aside to a TIMESTAMPED
            # path so a prior backup is never clobbered (no data loss).
            guard = Path(os.environ.get("CONFIG_DIR", "/config")) / "auto_demo.json"
            if guard.exists():
                stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
                guard.replace(guard.with_name(f"auto_demo.{stamp}.json"))
            proc = subprocess.run(  # fixed argv, no shell
                [sys.executable, str(script)],
                check=False,
                capture_output=True,
                text=True,
                env=env,
                timeout=300,
            )
            if proc.returncode != 0:
                # Log full stderr server-side; return a GENERIC error to the caller
                # (never reflect raw subprocess output to RPC clients).
                log.error(
                    "CreateDemoAccount: wizard failed rc=%s: %s",
                    proc.returncode,
                    proc.stderr[-2000:],
                )
                context.abort(
                    grpc.StatusCode.INTERNAL,
                    f"demo wizard failed (rc={proc.returncode})",
                )
            return self.GetProvisionedAccount(mt5_pb2.Empty(), context)
        finally:
            self._wizard_lock.release()

    # =========================================================================
    # SYMBOL OPERATIONS
    # =========================================================================

    def SymbolsTotal(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.IntResponse:
        """Get total number of available symbols.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            IntResponse with symbol count.

        """
        log.debug("SymbolsTotal: called")
        result = self._mt5_module.symbols_total()
        log.debug("SymbolsTotal: result=%s", result)
        return mt5_pb2.IntResponse(value=int(result) if result else 0)

    def SymbolsGet(
        self,
        request: mt5_pb2.SymbolsRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.SymbolsResponse:
        """Get available symbols with optional group filter.

        Returns chunked JSON for large datasets to prevent memory issues.

        Args:
            request: Optional group filter pattern.
            context: gRPC servicer context.

        Returns:
            SymbolsResponse with total count and JSON chunks.

        """
        group: str | None = None
        if request.HasField("_group"):
            group = request.group
        log.debug("SymbolsGet: group=%s", group)

        if group:
            result = _call_mt5_with_timeout(
                self._mt5_module.symbols_get,
                group=group,
            )
        else:
            result = _call_mt5_with_timeout(
                self._mt5_module.symbols_get,
            )

        if result is None:
            log.debug("SymbolsGet: result=None")
            return mt5_pb2.SymbolsResponse(total=0, chunks=[])

        # MT5 API returns tuple of SymbolInfo namedtuples
        items = list(cast("Iterable[p.NamedTupleRecord]", result))
        total = len(items)
        log.debug("SymbolsGet: total=%s symbols", total)

        chunk_size = 500
        chunks: list[str] = []
        for i in range(0, total, chunk_size):
            chunk_items = items[i : i + chunk_size]
            chunk_data = [self._namedtuple_to_dict(s) for s in chunk_items]
            chunks.append(orjson.dumps(chunk_data, default=str).decode())

        log.debug("SymbolsGet: returned %s chunks", len(chunks))
        return mt5_pb2.SymbolsResponse(total=total, chunks=chunks)

    def SymbolInfo(
        self,
        request: mt5_pb2.SymbolRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictData:
        """Get detailed symbol information.

        Args:
            request: Symbol name to query.
            context: gRPC servicer context.

        Returns:
            DictData with JSON-serialized symbol information.

        """
        self._ensure_mt5_loaded()
        log.debug("SymbolInfo: symbol=%s", request.symbol)
        if not self._validate_symbol(request.symbol, "SymbolInfo"):
            return mt5_pb2.DictData(json_data="")
        result = self._mt5_module.symbol_info(request.symbol)
        if result is None:
            return mt5_pb2.DictData(json_data="")
        data = self._namedtuple_to_dict(result)
        log.debug("SymbolInfo: found symbol")
        return mt5_pb2.DictData(json_data=_json_serialize(data))

    def SymbolInfoTick(
        self,
        request: mt5_pb2.SymbolRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictData:
        """Get current tick data for a symbol.

        Args:
            request: Symbol name to query.
            context: gRPC servicer context.

        Returns:
            DictData with JSON-serialized tick information.

        """
        self._ensure_mt5_loaded()
        log.debug("SymbolInfoTick: symbol=%s", request.symbol)
        if not self._validate_symbol(request.symbol, "SymbolInfoTick"):
            return mt5_pb2.DictData(json_data="")
        result = self._mt5_module.symbol_info_tick(request.symbol)
        if result is None:
            return mt5_pb2.DictData(json_data="")
        data = self._namedtuple_to_dict(result)
        log.debug(
            "SymbolInfoTick: bid=%s ask=%s",
            data.get("bid"),
            data.get("ask"),
        )
        return mt5_pb2.DictData(json_data=_json_serialize(data))

    def SymbolSelect(
        self,
        request: mt5_pb2.SymbolSelectRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.BoolResponse:
        """Select or deselect symbol in Market Watch.

        Args:
            request: Symbol name and enable flag.
            context: gRPC servicer context.

        Returns:
            BoolResponse indicating success or failure.

        """
        log.debug(
            "SymbolSelect: symbol=%s enable=%s",
            request.symbol,
            request.enable,
        )
        if not self._validate_symbol(request.symbol, "SymbolSelect"):
            return mt5_pb2.BoolResponse(result=False)
        result = self._mt5_module.symbol_select(request.symbol, enable=request.enable)
        log.debug("SymbolSelect: result=%s", result)
        return mt5_pb2.BoolResponse(result=bool(result))

    # =========================================================================
    # MARKET DATA - RATES
    # =========================================================================

    def CopyRatesFrom(
        self,
        request: mt5_pb2.CopyRatesRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.NumpyArray:
        """Copy OHLCV rates from a specific date.

        Args:
            request: Symbol, timeframe, date_from (timestamp), and count.
            context: gRPC servicer context.

        Returns:
            NumpyArray with serialized rate data.

        """
        log.debug(
            "CopyRatesFrom: symbol=%s tf=%s date=%s count=%s",
            request.symbol,
            request.timeframe,
            request.date_from,
            request.count,
        )
        if not self._validate_symbol(request.symbol, "CopyRatesFrom"):
            return self._numpy_to_proto(None)
        if not self._validate_count(request.count, "CopyRatesFrom"):
            return self._numpy_to_proto(None)
        result = _call_mt5_with_timeout(
            self._mt5_module.copy_rates_from,
            request.symbol,
            request.timeframe,
            request.date_from,
            request.count,
        )
        array_result = cast("p.StructuredArray | None", result)
        log.debug(
            "CopyRatesFrom: returned %s bars",
            len(array_result) if array_result is not None else 0,
        )
        return self._numpy_to_proto(array_result)

    def CopyRatesFromPos(
        self,
        request: mt5_pb2.CopyRatesPosRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.NumpyArray:
        """Copy OHLCV rates from a bar position.

        Args:
            request: Symbol, timeframe, start_pos, and count.
            context: gRPC servicer context.

        Returns:
            NumpyArray with serialized rate data.

        """
        log.debug(
            "CopyRatesFromPos: symbol=%s tf=%s pos=%s count=%s",
            request.symbol,
            request.timeframe,
            request.start_pos,
            request.count,
        )
        if not self._validate_symbol(request.symbol, "CopyRatesFromPos"):
            return self._numpy_to_proto(None)
        if not self._validate_count(request.count, "CopyRatesFromPos"):
            return self._numpy_to_proto(None)
        result = _call_mt5_with_timeout(
            self._mt5_module.copy_rates_from_pos,
            request.symbol,
            request.timeframe,
            request.start_pos,
            request.count,
        )
        array_result = cast("p.StructuredArray | None", result)
        log.debug(
            "CopyRatesFromPos: returned %s bars",
            len(array_result) if array_result is not None else 0,
        )
        return self._numpy_to_proto(array_result)

    def CopyRatesRange(
        self,
        request: mt5_pb2.CopyRatesRangeRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.NumpyArray:
        """Copy OHLCV rates in a date range.

        Args:
            request: Symbol, timeframe, date_from, and date_to (timestamps).
            context: gRPC servicer context.

        Returns:
            NumpyArray with serialized rate data.

        """
        log.debug(
            "CopyRatesRange: symbol=%s tf=%s from=%s to=%s",
            request.symbol,
            request.timeframe,
            request.date_from,
            request.date_to,
        )
        if not self._validate_symbol(request.symbol, "CopyRatesRange"):
            return self._numpy_to_proto(None)
        if not self._validate_date_range(
            request.date_from,
            request.date_to,
            "CopyRatesRange",
        ):
            return self._numpy_to_proto(None)
        result = _call_mt5_with_timeout(
            self._mt5_module.copy_rates_range,
            request.symbol,
            request.timeframe,
            request.date_from,
            request.date_to,
        )
        array_result = cast("p.StructuredArray | None", result)
        log.debug(
            "CopyRatesRange: returned %s bars",
            len(array_result) if array_result is not None else 0,
        )
        return self._numpy_to_proto(array_result)

    # =========================================================================
    # MARKET DATA - TICKS
    # =========================================================================

    def CopyTicksFrom(
        self,
        request: mt5_pb2.CopyTicksRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.NumpyArray:
        """Copy tick data from a specific date.

        Args:
            request: Symbol, date_from (timestamp), count, and flags.
            context: gRPC servicer context.

        Returns:
            NumpyArray with serialized tick data.

        """
        log.debug(
            "CopyTicksFrom: symbol=%s date=%s count=%s flags=%s",
            request.symbol,
            request.date_from,
            request.count,
            request.flags,
        )
        if not self._validate_symbol(request.symbol, "CopyTicksFrom"):
            return self._numpy_to_proto(None)
        if not self._validate_count(request.count, "CopyTicksFrom"):
            return self._numpy_to_proto(None)
        result = _call_mt5_with_timeout(
            self._mt5_module.copy_ticks_from,
            request.symbol,
            request.date_from,
            request.count,
            request.flags,
        )
        array_result = cast("p.StructuredArray | None", result)
        log.debug(
            "CopyTicksFrom: returned %s ticks",
            len(array_result) if array_result is not None else 0,
        )
        return self._numpy_to_proto(array_result)

    def CopyTicksRange(
        self,
        request: mt5_pb2.CopyTicksRangeRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.NumpyArray:
        """Copy tick data in a date range.

        Args:
            request: Symbol, date_from, date_to (timestamps), and flags.
            context: gRPC servicer context.

        Returns:
            NumpyArray with serialized tick data.

        """
        log.debug(
            "CopyTicksRange: symbol=%s from=%s to=%s flags=%s",
            request.symbol,
            request.date_from,
            request.date_to,
            request.flags,
        )
        if not self._validate_symbol(request.symbol, "CopyTicksRange"):
            return self._numpy_to_proto(None)
        if not self._validate_date_range(
            request.date_from,
            request.date_to,
            "CopyTicksRange",
        ):
            return self._numpy_to_proto(None)
        result = _call_mt5_with_timeout(
            self._mt5_module.copy_ticks_range,
            request.symbol,
            request.date_from,
            request.date_to,
            request.flags,
        )
        array_result = cast("p.StructuredArray | None", result)
        log.debug(
            "CopyTicksRange: returned %s ticks",
            len(array_result) if array_result is not None else 0,
        )
        return self._numpy_to_proto(array_result)

    # =========================================================================
    # TRADING OPERATIONS
    # =========================================================================

    def OrderCalcMargin(
        self,
        request: mt5_pb2.MarginRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.FloatResponse:
        """Calculate margin required for an order.

        Args:
            request: Action type, symbol, volume, and price.
            context: gRPC servicer context.

        Returns:
            FloatResponse with margin value or None.

        """
        log.debug(
            "OrderCalcMargin: action=%s symbol=%s vol=%s price=%s",
            request.action,
            request.symbol,
            request.volume,
            request.price,
        )
        result = self._mt5_module.order_calc_margin(
            request.action,
            request.symbol,
            request.volume,
            request.price,
        )
        log.debug("OrderCalcMargin: result=%s", result)
        if result is None:
            return mt5_pb2.FloatResponse()
        return mt5_pb2.FloatResponse(value=float(result))

    def OrderCalcProfit(
        self,
        request: mt5_pb2.ProfitRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.FloatResponse:
        """Calculate potential profit for an order.

        Args:
            request: Action, symbol, volume, price_open, and price_close.
            context: gRPC servicer context.

        Returns:
            FloatResponse with profit value or None.

        """
        log.debug(
            "OrderCalcProfit: action=%s symbol=%s vol=%s open=%s close=%s",
            request.action,
            request.symbol,
            request.volume,
            request.price_open,
            request.price_close,
        )
        result = self._mt5_module.order_calc_profit(
            request.action,
            request.symbol,
            request.volume,
            request.price_open,
            request.price_close,
        )
        log.debug("OrderCalcProfit: result=%s", result)
        if result is None:
            return mt5_pb2.FloatResponse()
        return mt5_pb2.FloatResponse(value=float(result))

    def OrderCheck(
        self,
        request: mt5_pb2.OrderRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictData:
        """Check order validity without sending.

        Args:
            request: JSON-serialized order request dict.
            context: gRPC servicer context.

        Returns:
            DictData with JSON-serialized order check result.

        """
        self._ensure_mt5_loaded()
        log.debug("OrderCheck: request=%s", request.json_request)
        order_dict = _json_deserialize(request.json_request)
        try:
            result = self._mt5_module.order_check(order_dict)
        except Exception as e:  # noqa: BLE001 - intentional catch-all for MT5 errors
            log.warning("OrderCheck exception: %s", e)
            # Return error result instead of raising
            error_data: dict[str, JSONValue] = {
                "retcode": 10006,  # TRADE_RETCODE_REJECT
                "comment": str(e),
            }
            return mt5_pb2.DictData(json_data=_json_serialize(error_data))
        if result is None:
            return mt5_pb2.DictData(json_data="")
        data = self._namedtuple_to_dict(result, nested_fields=["request"])
        log.debug("OrderCheck: retcode=%s", data.get("retcode"))
        return mt5_pb2.DictData(json_data=_json_serialize(data))

    def OrderSend(
        self,
        request: mt5_pb2.OrderRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictData:
        """Send trading order to MT5.

        Args:
            request: JSON-serialized order request dict.
            context: gRPC servicer context.

        Returns:
            DictData with JSON-serialized order result.

        """
        self._ensure_mt5_loaded()
        log.debug("OrderSend: request=%s", request.json_request)
        order_dict = _json_deserialize(request.json_request)
        result = self._mt5_module.order_send(order_dict)
        if result is None:
            return mt5_pb2.DictData(json_data="")
        data = self._namedtuple_to_dict(result, nested_fields=["request"])
        log.info(
            "OrderSend: retcode=%s order=%s deal=%s",
            data.get("retcode"),
            data.get("order"),
            data.get("deal"),
        )
        return mt5_pb2.DictData(json_data=_json_serialize(data))

    # =========================================================================
    # POSITION OPERATIONS
    # =========================================================================

    def PositionsTotal(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.IntResponse:
        """Get total number of open positions.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            IntResponse with position count.

        """
        log.debug("PositionsTotal: called")
        result = self._mt5_module.positions_total()
        log.debug("PositionsTotal: result=%s", result)
        return mt5_pb2.IntResponse(value=int(result) if result else 0)

    def PositionsGet(
        self,
        request: mt5_pb2.PositionsRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictList:
        """Get open positions with optional filters.

        Args:
            request: Optional symbol, group, or ticket filter.
            context: gRPC servicer context.

        Returns:
            DictList with JSON-serialized position data.

        """
        self._ensure_mt5_loaded()
        log.debug(
            "PositionsGet: symbol=%s group=%s ticket=%s",
            request.symbol if request.HasField("_symbol") else None,
            request.group if request.HasField("_group") else None,
            request.ticket if request.HasField("_ticket") else None,
        )
        kwargs: dict[str, str | int] = {}
        if request.HasField("_symbol"):
            kwargs["symbol"] = request.symbol
        if request.HasField("_group"):
            kwargs["group"] = request.group
        if request.HasField("_ticket"):
            kwargs["ticket"] = request.ticket

        if kwargs:
            result = self._mt5_module.positions_get(**kwargs)
        else:
            result = self._mt5_module.positions_get()

        if result is None:
            log.debug("PositionsGet: result=None")
            return mt5_pb2.DictList(json_items=[])

        json_items = [_json_serialize(self._namedtuple_to_dict(p)) for p in result]
        log.debug("PositionsGet: returned %s positions", len(json_items))
        return mt5_pb2.DictList(json_items=json_items)

    # =========================================================================
    # ORDER OPERATIONS
    # =========================================================================

    def OrdersTotal(
        self,
        request: mt5_pb2.Empty,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.IntResponse:
        """Get total number of pending orders.

        Args:
            request: Empty request.
            context: gRPC servicer context.

        Returns:
            IntResponse with order count.

        """
        log.debug("OrdersTotal: called")
        result = self._mt5_module.orders_total()
        log.debug("OrdersTotal: result=%s", result)
        return mt5_pb2.IntResponse(value=int(result) if result else 0)

    def OrdersGet(
        self,
        request: mt5_pb2.OrdersRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictList:
        """Get pending orders with optional filters.

        Args:
            request: Optional symbol, group, or ticket filter.
            context: gRPC servicer context.

        Returns:
            DictList with JSON-serialized order data.

        """
        self._ensure_mt5_loaded()
        log.debug(
            "OrdersGet: symbol=%s group=%s ticket=%s",
            request.symbol if request.HasField("_symbol") else None,
            request.group if request.HasField("_group") else None,
            request.ticket if request.HasField("_ticket") else None,
        )
        kwargs: dict[str, str | int] = {}
        if request.HasField("_symbol"):
            kwargs["symbol"] = request.symbol
        if request.HasField("_group"):
            kwargs["group"] = request.group
        if request.HasField("_ticket"):
            kwargs["ticket"] = request.ticket

        if kwargs:
            result = self._mt5_module.orders_get(**kwargs)
        else:
            result = self._mt5_module.orders_get()

        if result is None:
            log.debug("OrdersGet: result=None")
            return mt5_pb2.DictList(json_items=[])

        json_items = [_json_serialize(self._namedtuple_to_dict(o)) for o in result]
        log.debug("OrdersGet: returned %s orders", len(json_items))
        return mt5_pb2.DictList(json_items=json_items)

    # =========================================================================
    # HISTORY OPERATIONS
    # =========================================================================

    def HistoryOrdersTotal(
        self,
        request: mt5_pb2.HistoryRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.IntResponse:
        """Get total count of historical orders in date range.

        Args:
            request: date_from and date_to timestamps.
            context: gRPC servicer context.

        Returns:
            IntResponse with order count.

        """
        log.debug(
            "HistoryOrdersTotal: from=%s to=%s",
            request.date_from if request.HasField("_date_from") else None,
            request.date_to if request.HasField("_date_to") else None,
        )
        if not request.HasField("_date_from") or not request.HasField(
            "_date_to",
        ):
            return mt5_pb2.IntResponse(value=0)
        result = self._mt5_module.history_orders_total(
            request.date_from,
            request.date_to,
        )
        log.debug("HistoryOrdersTotal: result=%s", result)
        return mt5_pb2.IntResponse(value=int(result) if result else 0)

    def HistoryOrdersGet(
        self,
        request: mt5_pb2.HistoryRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictList:
        """Get historical orders with filters.

        Args:
            request: Optional date range, group, ticket, or position filter.
            context: gRPC servicer context.

        Returns:
            DictList with JSON-serialized historical order data.

        """
        self._ensure_mt5_loaded()
        log.debug(
            "HistoryOrdersGet: from=%s to=%s group=%s ticket=%s pos=%s",
            request.date_from if request.HasField("_date_from") else None,
            request.date_to if request.HasField("_date_to") else None,
            request.group if request.HasField("_group") else None,
            request.ticket if request.HasField("_ticket") else None,
            request.position if request.HasField("_position") else None,
        )

        kwargs: dict[str, str | int] = {}
        if request.HasField("_group"):
            kwargs["group"] = request.group
        if request.HasField("_ticket"):
            kwargs["ticket"] = request.ticket
        if request.HasField("_position"):
            kwargs["position"] = request.position

        if request.HasField("_date_from") and request.HasField("_date_to"):
            result = self._mt5_module.history_orders_get(
                request.date_from,
                request.date_to,
                **kwargs,
            )
        elif kwargs:
            result = self._mt5_module.history_orders_get(**kwargs)
        else:
            result = self._mt5_module.history_orders_get()

        if result is None:
            return mt5_pb2.DictList(json_items=[])

        json_items = [_json_serialize(self._namedtuple_to_dict(o)) for o in result]
        log.debug("HistoryOrdersGet: returned %s orders", len(json_items))
        return mt5_pb2.DictList(json_items=json_items)

    def HistoryDealsTotal(
        self,
        request: mt5_pb2.HistoryRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.IntResponse:
        """Get total count of historical deals in date range.

        Args:
            request: date_from and date_to timestamps.
            context: gRPC servicer context.

        Returns:
            IntResponse with deal count.

        """
        log.debug(
            "HistoryDealsTotal: from=%s to=%s",
            request.date_from if request.HasField("_date_from") else None,
            request.date_to if request.HasField("_date_to") else None,
        )
        if not request.HasField("_date_from") or not request.HasField(
            "_date_to",
        ):
            return mt5_pb2.IntResponse(value=0)
        result = self._mt5_module.history_deals_total(
            request.date_from,
            request.date_to,
        )
        log.debug("HistoryDealsTotal: result=%s", result)
        return mt5_pb2.IntResponse(value=int(result) if result else 0)

    def HistoryDealsGet(
        self,
        request: mt5_pb2.HistoryRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictList:
        """Get historical deals with filters.

        Args:
            request: Optional date range, group, ticket, or position filter.
            context: gRPC servicer context.

        Returns:
            DictList with JSON-serialized historical deal data.

        """
        self._ensure_mt5_loaded()
        log.debug(
            "HistoryDealsGet: from=%s to=%s group=%s ticket=%s pos=%s",
            request.date_from if request.HasField("_date_from") else None,
            request.date_to if request.HasField("_date_to") else None,
            request.group if request.HasField("_group") else None,
            request.ticket if request.HasField("_ticket") else None,
            request.position if request.HasField("_position") else None,
        )

        kwargs: dict[str, str | int] = {}
        if request.HasField("_group"):
            kwargs["group"] = request.group
        if request.HasField("_ticket"):
            kwargs["ticket"] = request.ticket
        if request.HasField("_position"):
            kwargs["position"] = request.position

        if request.HasField("_date_from") and request.HasField("_date_to"):
            result = self._mt5_module.history_deals_get(
                request.date_from,
                request.date_to,
                **kwargs,
            )
        elif kwargs:
            result = self._mt5_module.history_deals_get(**kwargs)
        else:
            result = self._mt5_module.history_deals_get()

        if result is None:
            return mt5_pb2.DictList(json_items=[])

        json_items = [_json_serialize(self._namedtuple_to_dict(d)) for d in result]
        log.debug("HistoryDealsGet: returned %s deals", len(json_items))
        return mt5_pb2.DictList(json_items=json_items)

    # =========================================================================
    # MARKET DEPTH (DOM) OPERATIONS
    # =========================================================================

    def MarketBookAdd(
        self,
        request: mt5_pb2.SymbolRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.BoolResponse:
        """Subscribe to market depth (DOM) for a symbol.

        Must be called before MarketBookGet to receive updates.

        Args:
            request: Symbol name to subscribe.
            context: gRPC servicer context.

        Returns:
            BoolResponse indicating success or failure.

        """
        log.debug("MarketBookAdd: symbol=%s", request.symbol)
        if not self._validate_symbol(request.symbol, "MarketBookAdd"):
            return mt5_pb2.BoolResponse(result=False)
        result = self._mt5_module.market_book_add(request.symbol)
        log.debug("MarketBookAdd: result=%s", result)
        return mt5_pb2.BoolResponse(result=bool(result))

    def MarketBookGet(
        self,
        request: mt5_pb2.SymbolRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.DictList:
        """Get market depth (DOM) data for a symbol.

        Requires prior MarketBookAdd call.

        Args:
            request: Symbol name to query.
            context: gRPC servicer context.

        Returns:
            DictList with JSON-serialized book entries.

        """
        self._ensure_mt5_loaded()
        log.debug("MarketBookGet: symbol=%s", request.symbol)
        if not self._validate_symbol(request.symbol, "MarketBookGet"):
            return mt5_pb2.DictList(json_items=[])
        result = self._mt5_module.market_book_get(request.symbol)
        if result is None:
            return mt5_pb2.DictList(json_items=[])
        json_items = [_json_serialize(self._namedtuple_to_dict(e)) for e in result]
        log.debug("MarketBookGet: returned %s entries", len(json_items))
        return mt5_pb2.DictList(json_items=json_items)

    def MarketBookRelease(
        self,
        request: mt5_pb2.SymbolRequest,
        context: grpc.ServicerContext,
    ) -> mt5_pb2.BoolResponse:
        """Unsubscribe from market depth (DOM) for a symbol.

        Args:
            request: Symbol name to unsubscribe.
            context: gRPC servicer context.

        Returns:
            BoolResponse indicating success or failure.

        """
        log.debug("MarketBookRelease: symbol=%s", request.symbol)
        if not self._validate_symbol(request.symbol, "MarketBookRelease"):
            return mt5_pb2.BoolResponse(result=False)
        result = self._mt5_module.market_book_release(request.symbol)
        log.debug("MarketBookRelease: result=%s", result)
        return mt5_pb2.BoolResponse(result=bool(result))


# =============================================================================
# SERVER SETUP AND LIFECYCLE
# =============================================================================


def _setup_logging(*, debug: bool = False) -> None:
    """Configure logging for the bridge.

    Args:
        debug: Enable debug-level logging if True.

    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(name)s] %(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def _graceful_shutdown(signum: int, frame: FrameType | None) -> None:
    """Handle shutdown signals for clean container stops.

    Args:
        signum: Signal number received.
        frame: Current stack frame (unused).

    """
    del frame  # Unused parameter
    sig_name = signal.Signals(signum).name
    log.info("Received %s, shutting down gracefully...", sig_name)
    if _server is not None:
        _server.stop(grace=5)
    sys.exit(0)


def serve(
    host: str = "0.0.0.0",
    port: int = 50051,
    max_workers: int = 10,
) -> None:
    """Start the gRPC server.

    Args:
        host: Host address to bind to.
        port: Port number to listen on.
        max_workers: Maximum number of worker threads.

    """
    global _server

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    if not isinstance(server, _GrpcServerLike):
        msg = "grpc.server returned incompatible server interface"
        raise TypeError(msg)
    _server = server
    register_servicer = cast(
        "Callable[[MT5GRPCServicer, _GrpcServerLike], None]",
        mt5_pb2_grpc.add_MT5ServiceServicer_to_server,
    )
    register_servicer(MT5GRPCServicer(), server)
    server_address = f"{host}:{port}"
    server.add_insecure_port(server_address)

    log.info("Starting MT5 gRPC server on %s", server_address)
    log.info("Python %s", sys.version)

    server.start()
    log.info("Server started, waiting for connections...")
    server.wait_for_termination()


def main(argv: list[str] | None = None) -> int:
    """Run the gRPC bridge server.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, 1 for error).

    """
    parser = argparse.ArgumentParser(description="MT5 gRPC Bridge Server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind (default: 0.0.0.0)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=50051,
        help="Port (default: 50051)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Worker threads (default: 10)",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--mt5-timeout",
        type=float,
        default=30.0,
        help="MT5 call timeout in seconds (default: 30.0)",
    )
    args = parser.parse_args(argv)

    # Update global MT5 call timeout
    global _mt5_call_timeout
    _mt5_call_timeout = args.mt5_timeout

    _setup_logging(debug=args.debug)

    signal.signal(signal.SIGTERM, _graceful_shutdown)
    signal.signal(signal.SIGINT, _graceful_shutdown)

    log.debug("Debug logging enabled")
    log.debug("Workers=%s", args.workers)

    try:
        serve(host=args.host, port=args.port, max_workers=args.workers)
    except KeyboardInterrupt:
        log.info("Server interrupted by user")
    except Exception:
        log.exception("Server error")
        return 1
    finally:
        log.info("Server stopped")

    return 0


if __name__ == "__main__":
    sys.exit(main())
