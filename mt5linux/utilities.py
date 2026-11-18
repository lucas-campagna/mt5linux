"""Centralized utilities for mt5linux.

Minimal structure with maximum integration:
- Uses MT5Settings for all configuration (no separate config classes)
- Uses MT5Constants for enums (CircuitBreakerState)
- All data utilities consolidated in Data class
- All exceptions consolidated in Exceptions class

Hierarchy Level: 2
- Imports: MT5Settings, MT5Constants
- Used by: client.py, async_client.py, server.py

Usage:

    # Exceptions
    raise MT5Utilities.Exceptions.RetryableError(code, description)
    raise MT5Utilities.Exceptions.CircuitBreakerOpenError()

    # Data utilities
    MT5Utilities.Data.validate_version(value)
    MT5Utilities.Data.wrap(d)
    MT5Utilities.Data.to_timestamp(dt)

    # Circuit Breaker (uses MT5Settings directly)
    cb = MT5Utilities.CircuitBreaker(config=mt5_settings, name="mt5")
    if cb.can_execute():
        try:
            result = do_operation()
            cb.record_success()
        except Exception:
            cb.record_failure()
"""

from __future__ import annotations

# pylint: disable=no-member  # Protobuf generated code has dynamic members
import ast
import asyncio
import logging
import operator
import random
import threading
import uuid
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import IntEnum
from importlib import import_module
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    NoReturn,
    Protocol,
    cast,
    overload,
    runtime_checkable,
)

import aiosqlite
import orjson

from mt5linux.grpc_constants import MT5Constants as c

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Coroutine, Mapping, Sequence

    from mt5linux.grpc_types import MT5Types as t
    from mt5linux.grpc_types import T
    from mt5linux.protocols import MT5Protocols as p
    from mt5linux.settings import MT5Settings


def _string_tuple(value: object) -> tuple[str, ...] | None:
    """Return value as a string tuple when every item is a string."""
    if not isinstance(value, tuple):
        return None
    items = cast("tuple[object, ...]", value)
    result: list[str] = []
    for item in items:
        if not isinstance(item, str):
            return None
        result.append(item)
    return tuple(result)


def _tuple_of_objects(
    value: object,
    expected_len: int,
    expected: str,
) -> tuple[object, ...]:
    """Validate tuple shape and return explicitly typed items."""
    if not isinstance(value, tuple):
        msg = f"Expected {expected}, got object that is not a tuple"
        raise TypeError(msg)
    tuple_value = cast("tuple[object, ...]", value)
    if len(tuple_value) != expected_len:
        msg = f"Expected {expected}, got tuple with {len(tuple_value)} items"
        raise TypeError(msg)
    return tuple_value


# Protocols for gRPC protobuf types
@runtime_checkable
class _NumpyArrayProto(Protocol):
    """Protocol for NumpyArray protobuf message."""

    data: bytes
    dtype: str
    shape: Sequence[int]


@runtime_checkable
class _SymbolsResponseProto(Protocol):
    """Protocol for SymbolsResponse protobuf message."""

    total: int
    chunks: Sequence[str]


class _NumpyModule(Protocol):
    """Small NumPy surface needed by mt5linux serialization."""

    def dtype(self, value: str | list[tuple[str, str]]) -> t.ArrayDType: ...
    def frombuffer(
        self, buffer: bytes, *, dtype: t.ArrayDType
    ) -> t.StructuredArray: ...


@runtime_checkable
class _GrpcStatusCodeProto(Protocol):
    """gRPC status-code value surface used by retry classification."""

    value: tuple[int, str]


@runtime_checkable
class _GrpcErrorProto(Protocol):
    """Exception surface provided by grpc.RpcError implementations."""

    def code(self) -> _GrpcStatusCodeProto | int: ...


@runtime_checkable
class _RetcodeResultProto(Protocol):
    """Result surface for MT5 trade return-code handling."""

    retcode: int


class _CircuitBreakerRecorder(Protocol):
    """Circuit-breaker behavior needed by transaction helpers."""

    def record_success(self) -> None:
        """Record a successful operation."""


log = logging.getLogger(__name__)


class MT5Utilities:
    """Centralized utilities for mt5linux.

    Minimal structure:
    - Exceptions: All exception classes
    - Data: All data utilities (validation, wrapping, datetime)
    - CircuitBreaker: Fault tolerance pattern

    Note: All constants moved to MT5Constants.Validation:
    VERSION_TUPLE_LEN, ERROR_TUPLE_LEN, REQUEST_ID_*
    """

    class External:
        """External runtime module loaders."""

        @staticmethod
        def load_metatrader5() -> p.MetaTrader5Module:
            """Load the real MetaTrader5 module through a typed protocol."""
            return cast("p.MetaTrader5Module", import_module("MetaTrader5"))

        @staticmethod
        def load_numpy() -> _NumpyModule:
            """Load NumPy through the typed serialization protocol."""
            return cast("_NumpyModule", import_module("numpy"))

    # =========================================================================
    # EXCEPTIONS
    # =========================================================================

    class Exceptions:
        """All MT5 exceptions in one container."""

        class Error(Exception):
            """Base exception for all MT5 client errors."""

        class RetryableError(Error):
            """Error that can be retried (transient failure)."""

            def __init__(self, code: int, description: str) -> None:
                """Initialize retryable error.

                Args:
                    code: MT5 error code.
                    description: Error description.

                """
                super().__init__(f"MT5 error {code}: {description}")
                self.code = code
                self.description = description

        class PermanentError(Error):
            """Error that should not be retried."""

            def __init__(self, code: int, description: str) -> None:
                """Initialize permanent error.

                Args:
                    code: MT5 error code.
                    description: Error description.

                """
                super().__init__(f"MT5 permanent error {code}: {description}")
                self.code = code
                self.description = description

        class MaxRetriesError(Error):
            """Maximum retry attempts exceeded."""

            def __init__(
                self,
                operation: str,
                attempts: int,
                last_error: Exception | None = None,
            ) -> None:
                """Initialize max retries error.

                Args:
                    operation: Name of the failed operation.
                    attempts: Number of attempts made.
                    last_error: The last exception that occurred.

                """
                msg = f"Operation '{operation}' failed after {attempts} attempts"
                if last_error:
                    msg += f": {last_error}"
                super().__init__(msg)
                self.operation = operation
                self.attempts = attempts
                self.last_error = last_error

        class NotAvailableError(Error):
            """MT5 module not available."""

        class CircuitBreakerOpenError(Error):
            """Raised when circuit breaker is open."""

            def __init__(
                self,
                message: str = "Circuit breaker is open - too many failures",
                recovery_time: datetime | None = None,
            ) -> None:
                """Initialize circuit breaker open error.

                Args:
                    message: Error message.
                    recovery_time: When the circuit breaker will attempt reset.

                """
                super().__init__(message)
                self.recovery_time = recovery_time

        class EmptyResponseError(RetryableError):
            """Raised when MT5 returns empty response that should have data.

            This is a transient condition that should trigger retry.
            Used to distinguish between:
            - Valid None (e.g., symbol doesn't exist)
            - Transient failure (e.g., MT5 not ready, connection hiccup)

            """

            def __init__(self, operation: str, detail: str = "") -> None:
                """Initialize empty response error.

                Args:
                    operation: Name of the operation that returned empty.
                    detail: Additional context about the empty response.

                """
                msg = f"Empty response from {operation}"
                if detail:
                    msg += f": {detail}"
                # Use code -1 to indicate empty response (not a real MT5 error)
                super().__init__(code=-1, description=msg)
                self.operation = operation
                self.detail = detail

        class QueueFullError(Error):
            """Raised when request queue is at capacity (backpressure).

            This is NOT a transient error - caller should handle backpressure
            by waiting, reducing request rate, or dropping low-priority requests.

            """

            def __init__(self, message: str = "Request queue full") -> None:
                """Initialize queue full error.

                Args:
                    message: Error message with queue capacity.

                """
                super().__init__(message)

    # =========================================================================
    # DATA UTILITIES
    # =========================================================================

    class Data:
        """Unified data utilities - validation, wrapping, transformation, datetime."""

        class Wrapper:
            """Wrapper for MT5 data dict with attribute access."""

            __slots__ = ("_data",)
            _data: dict[str, object]

            def __init__(self, data: dict[str, object]) -> None:
                """Initialize wrapper with data dict.

                Args:
                    data: Dictionary to wrap for attribute access.

                """
                object.__setattr__(self, "_data", data)

            def __getattr__(self, name: str) -> object:
                """Get attribute from underlying dict.

                Args:
                    name: Attribute name to retrieve.

                Returns:
                    Value from the underlying dictionary.

                Raises:
                    AttributeError: If key not found in dict.

                """
                try:
                    return self._data[name]
                except KeyError:
                    msg = f"'{type(self).__name__}' has no attribute '{name}'"
                    raise AttributeError(msg) from None

            def __repr__(self) -> str:
                """Return string representation.

                Returns:
                    String representation of the wrapper.

                """
                return f"{type(self).__name__}({self._data})"

            def _asdict(self) -> dict[str, object]:
                """Return underlying dict (compatibility with named tuples)."""
                return self._data

        # --- Validators ---

        @staticmethod
        def validate_version(value: object) -> tuple[int, int, str] | None:
            """Validate and convert Any to version tuple."""
            if value is None:
                return None
            expected_len = c.Validation.VERSION_TUPLE_LEN
            items = cast(
                "tuple[int, int, str]",
                _tuple_of_objects(
                    value,
                    expected_len,
                    "version tuple | None",
                ),
            )
            try:
                return (int(items[0]), int(items[1]), str(items[2]))
            except (ValueError, IndexError, TypeError) as e:
                msg = f"Invalid version tuple: {e}"
                raise TypeError(msg) from e

        @staticmethod
        def validate_last_error(value: object) -> tuple[int, str]:
            """Validate and convert Any to last_error tuple."""
            expected_len = c.Validation.ERROR_TUPLE_LEN
            items = cast(
                "tuple[int, str]",
                _tuple_of_objects(
                    value,
                    expected_len,
                    "tuple[int, str]",
                ),
            )
            try:
                return (int(items[0]), str(items[1]))
            except (ValueError, IndexError, TypeError) as e:
                msg = f"Invalid error tuple: {e}"
                raise TypeError(msg) from e

        @staticmethod
        def validate_bool(value: object) -> bool:
            """Validate and convert Any to bool."""
            if isinstance(value, bool):
                return value
            if isinstance(value, int):
                return bool(value)
            msg = f"Expected bool, got {type(value).__name__}"
            raise TypeError(msg)

        @staticmethod
        def validate_int(value: object) -> int:
            """Validate and convert Any to int."""
            if isinstance(value, int) and not isinstance(value, bool):
                return value
            msg = f"Expected int, got {type(value).__name__}"
            raise TypeError(msg)

        @staticmethod
        def validate_int_optional(value: object) -> int | None:
            """Validate and convert Any to int | None."""
            if value is None:
                return None
            if isinstance(value, int) and not isinstance(value, bool):
                return value
            msg = f"Expected int | None, got {type(value).__name__}"
            raise TypeError(msg)

        @staticmethod
        def validate_float_optional(value: object) -> float | None:
            """Validate and convert Any to float | None."""
            if value is None:
                return None
            if isinstance(value, int | float) and not isinstance(value, bool):
                return float(value)
            msg = f"Expected float | None, got {type(value).__name__}"
            raise TypeError(msg)

        # --- Transformations ---

        @staticmethod
        def wrap(
            d: dict[str, object] | object,
        ) -> MT5Utilities.Data.Wrapper | object:
            """Convert dict to object with attribute access.

            Args:
                d: Dictionary or other object.

            Returns:
                Wrapper if dict, otherwise original object.

            """
            if isinstance(d, dict):
                return MT5Utilities.Data.Wrapper(cast("dict[str, object]", d))
            return d

        @staticmethod
        def wrap_many(
            items: tuple[object, ...] | list[object] | None,
        ) -> tuple[object, ...] | None:
            """Convert tuple/list of dicts to tuple of objects.

            Args:
                items: Tuple or list of dictionaries.

            Returns:
                Tuple of wrapped objects or None.

            """
            if items is None:
                return None
            return tuple(MT5Utilities.Data.wrap(d) for d in items)

        @staticmethod
        def unwrap_chunks(
            result: dict[str, object] | tuple[object, ...] | list[object] | None,
        ) -> tuple[object, ...] | None:
            """Reassemble chunked response from server into tuple of objects.

            Args:
                result: Chunked response dict or None.

            Returns:
                Tuple of wrapped objects or None.

            """
            unwrapped: tuple[object, ...] | None
            if result is None:
                return None
            if isinstance(result, dict):
                if "chunks" not in result:
                    return None
                chunks = result.get("chunks")
                if not isinstance(chunks, list):
                    return ()
                all_items: list[MT5Utilities.Data.Wrapper] = []
                chunks_list = cast("list[object]", chunks)
                for chunk in chunks_list:
                    if not isinstance(chunk, list):
                        return None
                    all_items.extend(
                        MT5Utilities.Data.Wrapper(cast("dict[str, object]", item))
                        for item in cast("list[object]", chunk)
                        if isinstance(item, dict)
                    )
                unwrapped = tuple(all_items)
            elif isinstance(result, tuple):
                unwrapped = MT5Utilities.Data.wrap_many(result)
            else:
                unwrapped = MT5Utilities.Data.wrap_many(tuple(result))
            return unwrapped

        # --- DateTime ---

        @staticmethod
        @overload
        def to_timestamp(dt: datetime | int) -> int: ...

        @staticmethod
        @overload
        def to_timestamp(dt: None) -> None: ...

        @staticmethod
        def to_timestamp(dt: datetime | int | None) -> int | None:
            """Convert datetime to Unix timestamp for MT5 API."""
            if dt is None:
                return None
            if isinstance(dt, datetime):
                return int(dt.timestamp())
            return dt

        @staticmethod
        def json_to_dict(json_data: str) -> dict[str, object] | None:
            """Convert JSON string from gRPC to dict.

            Used by both sync and async clients for gRPC responses.

            Args:
                json_data: JSON string to parse.

            Returns:
                Parsed dictionary or None if empty.

            """
            if not json_data:
                return None
            parsed = orjson.loads(json_data)
            if not isinstance(parsed, dict):
                return None
            return cast("dict[str, object]", parsed)

        @staticmethod
        def unwrap_proto_list_to_dicts(
            json_items: list[str],
        ) -> list[dict[str, object]] | None:
            """Convert list of JSON strings from gRPC to list of dicts.

            Used by both sync and async clients for gRPC responses containing
            lists of JSON-serialized objects (positions, orders, history, etc).

            Args:
                json_items: List of JSON strings to parse.

            Returns:
                List of dictionaries or None if empty.

            """
            if not json_items:
                return None
            return [orjson.loads(item) for item in json_items if item]

        @staticmethod
        def unwrap_proto_list_to_tuple(
            json_items: list[str],
        ) -> tuple[dict[str, object], ...] | None:
            """Convert list of JSON strings from gRPC to tuple of dicts.

            Maintains compatibility with original MetaTrader5 API which
            returns tuples from methods like positions_get(), orders_get().

            Args:
                json_items: List of JSON strings to parse.

            Returns:
                Tuple of dictionaries or None if empty.

            """
            result = MT5Utilities.Data.unwrap_proto_list_to_dicts(json_items)
            if result is None:
                return None
            return tuple(result)

        @staticmethod
        def numpy_from_proto(
            proto: _NumpyArrayProto | None,
        ) -> t.StructuredArray | None:
            """Convert NumpyArray proto to numpy array.

            Used by both sync and async clients to deserialize OHLCV and tick data
            from gRPC NumpyArray protobuf messages.

            Handles both simple dtypes ('float64') and structured array dtypes
            ("[('time', '<i8'), ('open', '<f8'), ...]").

            Args:
                proto: NumpyArray protobuf message with .data, .dtype, .shape
                 attributes.

            Returns:
                NumPy structured array or None if empty.

            """
            if proto is None or not proto.data or not proto.dtype:
                return None

            # Parse dtype string to numpy dtype
            dtype_str = proto.dtype
            numpy = MT5Utilities.External.load_numpy()
            if dtype_str.startswith("["):
                # Structured array dtype - parse the list of tuples
                dtype_spec = cast("list[tuple[str, str]]", ast.literal_eval(dtype_str))
                dtype = numpy.dtype(dtype_spec)
            else:
                # Simple dtype like 'float64', '<f8'
                dtype = numpy.dtype(dtype_str)

            arr = numpy.frombuffer(proto.data, dtype=dtype)
            if proto.shape:
                arr = arr.reshape(tuple(proto.shape))
            return arr

        @staticmethod
        def unwrap_symbols_chunks(
            response: _SymbolsResponseProto | None,
        ) -> list[dict[str, object]] | None:
            """Unwrap chunked symbols response from gRPC.

            Used by both sync and async clients to reassemble large symbol lists
            that are sent in chunks to avoid gRPC message size limits.

            Args:
                response: SymbolsResponse protobuf with .total and .chunks attributes.

            Returns:
                List of symbol dictionaries or None if empty.

            """
            if response is None or response.total == 0:
                return None
            result: list[dict[str, object]] = []
            for chunk in response.chunks:
                chunk_data: list[dict[str, object]] = orjson.loads(chunk)
                result.extend(chunk_data)
            return result

    # =========================================================================
    # INTROSPECTION UTILITIES
    # =========================================================================

    class Introspection:
        """Python introspection utilities for tuple subclasses."""

        @staticmethod
        def get_tuple_field_order(tuple_cls: type) -> list[str] | None:
            """Get field names in correct positional order from tuple subclass.

            Uses Python's built-in introspection - NO hardcoding.
            Tries multiple methods in order of reliability:
            1. __match_args__ (Python 3.10+ structseq types)
            2. _fields (standard namedtuples)
            3. Test instance mapping (universal for member_descriptor types)

            Args:
                tuple_cls: The tuple subclass to introspect.

            Returns:
                List of field names in positional order, or None if fails.

            """
            # Python 3.10+ structseq types have __match_args__.
            match_args = _string_tuple(getattr(tuple_cls, "__match_args__", None))
            if match_args is not None:
                return list(match_args)

            # Standard namedtuples have _fields.
            fields = _string_tuple(getattr(tuple_cls, "_fields", None))
            if fields is not None:
                return list(fields)

            # For types without either, create test instance and map indices
            member_fields = [
                name
                for name in dir(tuple_cls)
                if not name.startswith("_")
                and type(getattr(tuple_cls, name, None)).__name__
                in (
                    "member_descriptor",
                    "MemberDescriptor",
                )
            ]

            if not member_fields:
                return None

            # Create instance with sentinel values to determine positional order
            try:
                n = len(member_fields)
                instance = tuple_cls.__new__(tuple_cls, tuple(range(n)))

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

    # =========================================================================
    # ERROR CLASSIFIER
    # =========================================================================

    class ErrorClassifier:
        """Error classification for gRPC and MT5 operations.

        Centralized error classification logic extracted from CircuitBreaker.
        All methods are static - no state stored.

        Used by:
        - RetryStrategy: to determine if exception is retryable
        - TransactionHandler: to classify MT5 retcodes
        - CircuitBreaker: via aliases for backward compatibility

        Categories:
        - gRPC errors: network-level, transient vs permanent
        - MT5 retcodes: operation result codes, 7 classifications
        - Operation criticality: determines retry behavior

        Usage:
            if ErrorClassifier.is_retryable_exception(error):
                retry()

            classification = ErrorClassifier.classify_mt5_retcode(10012)
            if classification == ErrorClassification.VERIFY_REQUIRED:
                verify_state()
        """

        @staticmethod
        def is_retryable_grpc_code(code: int) -> bool:
            """Check if gRPC status code is retryable.

            Args:
                code: gRPC status code (integer value).

            Returns:
                True if the code indicates a transient error.

            """
            retryable_codes = {
                c.Resilience.GrpcRetryableCode.UNAVAILABLE,
                c.Resilience.GrpcRetryableCode.DEADLINE_EXCEEDED,
                c.Resilience.GrpcRetryableCode.ABORTED,
                c.Resilience.GrpcRetryableCode.RESOURCE_EXHAUSTED,
            }
            return code in retryable_codes

        @staticmethod
        def is_retryable_exception(error: Exception) -> bool:
            """Check if exception should trigger retry.

            Args:
                error: Exception to check.

            Returns:
                True if exception is retryable.

            """
            # MT5 client errors. Checked before gRPC protocol detection because
            # both RetryableError and PermanentError expose a `code` attribute
            # that would satisfy _GrpcErrorProto.
            if isinstance(error, MT5Utilities.Exceptions.Error):
                return isinstance(error, MT5Utilities.Exceptions.RetryableError)

            # Check for gRPC errors (duck typing to avoid import)
            if isinstance(error, _GrpcErrorProto):
                code = error.code()
                # grpc.StatusCode is an enum, get its value
                code_value = code if isinstance(code, int) else code.value[0]
                return MT5Utilities.ErrorClassifier.is_retryable_grpc_code(code_value)

            # Connection/timeout errors are retryable, EXCEPT "not established"
            # which means client was never connected (programming error, not transient)
            if isinstance(error, ConnectionError):
                msg = str(error).lower()
                # Client never connected is not retryable; connection lost is retryable
                return "not established" not in msg and "call connect" not in msg

            return isinstance(error, (TimeoutError, OSError))

        @staticmethod
        def classify_mt5_retcode(
            retcode: int,
        ) -> c.Resilience.ErrorClassification:
            """Classify MT5 retcode into error category.

            Used to determine how each error should be handled:
            - SUCCESS: Operation completed successfully
            - PARTIAL: Partially completed (may need follow-up)
            - RETRYABLE: Transient error, safe to retry (order NOT executed)
            - VERIFY_REQUIRED: MUST verify state before retry (order MAY executed)
            - CONDITIONAL: May be retryable depending on context
            - PERMANENT: Permanent error, do not retry
            - UNKNOWN: Unknown error code

            Args:
                retcode: MT5 TradeRetcode value.

            Returns:
                ErrorClassification indicating how to handle this code.

            """
            if retcode in c.Resilience.MT5_SUCCESS_CODES:
                return c.Resilience.ErrorClassification.SUCCESS
            if retcode in c.Resilience.MT5_PARTIAL_CODES:
                return c.Resilience.ErrorClassification.PARTIAL
            if retcode in c.Resilience.MT5_VERIFY_REQUIRED_CODES:
                return c.Resilience.ErrorClassification.VERIFY_REQUIRED
            if retcode in c.Resilience.MT5_RETRYABLE_CODES:
                return c.Resilience.ErrorClassification.RETRYABLE
            if retcode in c.Resilience.MT5_CONDITIONAL_CODES:
                return c.Resilience.ErrorClassification.CONDITIONAL
            if retcode in c.Resilience.MT5_PERMANENT_CODES:
                return c.Resilience.ErrorClassification.PERMANENT
            return c.Resilience.ErrorClassification.UNKNOWN

        @staticmethod
        def is_retryable_mt5_code(retcode: int) -> bool:
            """Check if MT5 TradeRetcode is retryable.

            Args:
                retcode: MT5 TradeRetcode value.

            Returns:
                True if the code indicates a transient error.

            """
            classification = MT5Utilities.ErrorClassifier.classify_mt5_retcode(retcode)
            return classification == c.Resilience.ErrorClassification.RETRYABLE

        @staticmethod
        def is_permanent_mt5_code(retcode: int) -> bool:
            """Check if MT5 TradeRetcode is permanent.

            Args:
                retcode: MT5 TradeRetcode value.

            Returns:
                True if the code indicates a permanent error.

            """
            classification = MT5Utilities.ErrorClassifier.classify_mt5_retcode(retcode)
            return classification == c.Resilience.ErrorClassification.PERMANENT

        @staticmethod
        def get_operation_criticality(
            operation: str,
        ) -> c.Resilience.OperationCriticality:
            """Get criticality level for an operation.

            Used to determine retry strategy and state verification:
            - CRITICAL: More retries, state verification on ambiguous errors
            - HIGH/NORMAL/LOW: Standard retry behavior

            Args:
                operation: Operation name (e.g., "order_send").

            Returns:
                OperationCriticality level (defaults to NORMAL if unknown).

            """
            criticality_value = c.Resilience.OPERATION_CRITICALITY.get(
                operation,
                c.Resilience.OperationCriticality.NORMAL,
            )
            return c.Resilience.OperationCriticality(criticality_value)

        @staticmethod
        def should_verify_state(
            operation: str,
            classification: c.Resilience.ErrorClassification,
        ) -> bool:
            """Determine if state verification is needed after error.

            For CRITICAL operations with ambiguous errors (CONDITIONAL, UNKNOWN),
            we need to verify the actual state before reporting to caller.

            Args:
                operation: Operation name.
                classification: Error classification from classify_mt5_retcode().

            Returns:
                True if state verification is recommended.

            """
            criticality = MT5Utilities.ErrorClassifier.get_operation_criticality(
                operation
            )
            if criticality != c.Resilience.OperationCriticality.CRITICAL:
                return False

            # For critical ops, verify state on ambiguous errors
            return classification in {
                c.Resilience.ErrorClassification.CONDITIONAL,
                c.Resilience.ErrorClassification.UNKNOWN,
                c.Resilience.ErrorClassification.VERIFY_REQUIRED,
            }

    # =========================================================================
    # RETRY STRATEGY
    # =========================================================================

    class RetryStrategy:
        """Retry strategies for async operations.

        Centralized retry logic extracted from CircuitBreaker.
        All methods are static - no state stored.

        Used by:
        - AsyncMetaTrader5._resilient_call(): generic retry for all gRPC calls
        - AsyncMetaTrader5._reconnect_with_backoff(): reconnection attempts
        - CircuitBreaker: via aliases for backward compatibility

        Features:
        - Exponential backoff with configurable parameters
        - Jitter support to prevent thundering herd
        - Callbacks for circuit breaker integration
        - Before-retry hooks for reconnection

        Usage:
            result = await RetryStrategy.async_retry_with_backoff(
                lambda: client.send_order(),
                config,
                "order_send",
                should_retry=ErrorClassifier.is_retryable_exception,
                on_success=cb.record_success,
                on_failure=cb.record_failure,
            )
        """

        @staticmethod
        async def async_retry_with_backoff(
            coro_factory: Callable[[], Awaitable[T]],
            config: MT5Settings,
            operation_name: str = "operation",
            *,
            should_retry: Callable[[Exception], bool] | None = None,
            on_success: Callable[[], None] | None = None,
            on_failure: Callable[[Exception], None] | None = None,
            before_retry: Callable[[], Awaitable[None]] | None = None,
            max_attempts_override: int | None = None,
        ) -> T:
            """Execute async operation with exponential backoff retry.

            This is the SINGLE implementation of retry logic used by both
            generic operations and MT5-specific operations (via hooks).

            Args:
                coro_factory: Callable that returns an awaitable (not a coroutine).
                config: MT5Settings with retry_* settings.
                operation_name: Name for logging purposes.
                should_retry: Optional predicate to decide if exception is retryable.
                    If None, all exceptions are retryable. If returns False,
                    exception is raised immediately without retry.
                on_success: Optional callback invoked on successful execution.
                    Used by circuit breaker to record success.
                on_failure: Optional callback invoked when non-retryable exception
                    occurs or all retries exhausted. Used by circuit breaker.
                before_retry: Optional async callback invoked before each retry.
                    Used for reconnection attempts.
                max_attempts_override: Override config.retry_max_attempts.
                    Used by _resilient_call for different attempt counts.

            Returns:
                Result of successful operation.

            Raises:
                MT5Utilities.Exceptions.MaxRetriesError: If all retries fail.
                Exception: Non-retryable exceptions propagate immediately.

            Example:
                >>> # Simple retry (all exceptions retryable)
                >>> async def fetch():
                ...     return await client.get_data()
                >>> result = await MT5Utilities.RetryStrategy.async_retry_with_backoff(
                ...     fetch, config, "get_data"
                ... )

                >>> # With circuit breaker hooks
                >>> result = await MT5Utilities.RetryStrategy.async_retry_with_backoff(
                ...     fetch, config, "get_data",
                ...     should_retry=ErrorClassifier.is_retryable_exception,
                ...     on_success=cb.record_success,
                ...     on_failure=cb.record_failure,
                ... )

            """
            last_exception: Exception | None = None
            # CRITICAL FIX v4: Use explicit None check, not "or"
            # "0 or default" returns default because 0 is falsy!
            max_attempts = (
                max_attempts_override
                if max_attempts_override is not None
                else config.retry_max_attempts
            )

            # CRITICAL FIX v4: Validate max_attempts >= 1
            # If max_attempts is 0 or negative, the loop never executes
            if max_attempts < 1:
                msg = f"max_attempts must be >= 1, got {max_attempts}"
                raise ValueError(msg)

            for attempt in range(max_attempts):
                try:
                    result = await coro_factory()
                except Exception as e:
                    last_exception = e

                    # Check if retryable (default: all exceptions are retryable)
                    if should_retry is not None and not should_retry(e):
                        # Non-retryable: record failure and propagate
                        if on_failure:
                            on_failure(e)
                        raise

                    # Check if more attempts available
                    if attempt < max_attempts - 1:
                        # Calculate backoff delay using config
                        delay = config.calculate_retry_delay(attempt)

                        log.warning(
                            "'%s' attempt %d/%d failed: %s. Retry in %.2fs",
                            operation_name,
                            attempt + 1,
                            max_attempts,
                            e,
                            delay,
                        )

                        await asyncio.sleep(delay)

                        # Before retry callback (e.g., reconnection)
                        # CRITICAL FIX: Handle exceptions in before_retry gracefully
                        # to prevent infinite hangs when reconnection fails
                        if before_retry:
                            try:
                                await before_retry()
                            except Exception as before_retry_error:  # noqa: BLE001
                                # Log but don't raise - let the main retry continue
                                log.warning(
                                    "before_retry callback failed: %s",
                                    before_retry_error,
                                )
                    else:
                        # Last attempt failed
                        if on_failure:
                            on_failure(e)
                        log.exception(
                            "Operation '%s' failed after %d attempts",
                            operation_name,
                            max_attempts,
                        )
                        raise MT5Utilities.Exceptions.MaxRetriesError(
                            operation_name,
                            max_attempts,
                            last_exception,
                        ) from e
                else:
                    # Success - invoke callback and return
                    # CRITICAL FIX v4: Wrap callback in try-except to prevent
                    # callback errors from losing successful result
                    if on_success:
                        try:
                            on_success()
                        except Exception:
                            log.exception(
                                "on_success callback failed for '%s'",
                                operation_name,
                            )
                    return result

            # Should not reach here, but satisfy type checker
            if last_exception:
                raise MT5Utilities.Exceptions.MaxRetriesError(
                    operation_name,
                    max_attempts,
                    last_exception,
                )
            msg = f"Retry failed for '{operation_name}' with no exception recorded"
            raise RuntimeError(msg)

        @staticmethod
        async def async_reconnect_with_backoff(
            connect_factory: Callable[[], Awaitable[bool]],
            config: MT5Settings,
            name: str = "reconnect",
        ) -> bool:
            """Attempt reconnection with exponential backoff and jitter.

            Uses MT5Settings values for retry parameters.

            Args:
                connect_factory: Callable that returns awaitable bool (True=success).
                config: MT5Settings with retry_* settings.
                name: Name for logging purposes.

            Returns:
                True if reconnection successful, False otherwise.

            """
            delay = config.retry_initial_delay

            for attempt in range(config.retry_max_attempts):
                try:
                    log.info(
                        "Reconnection '%s' attempt %d/%d",
                        name,
                        attempt + 1,
                        config.retry_max_attempts,
                    )

                    success = await connect_factory()
                    if success:
                        log.info(
                            "Reconnection '%s' successful after %d attempts",
                            name,
                            attempt + 1,
                        )
                        return True

                except Exception as e:  # noqa: BLE001
                    log.warning(
                        "Reconnection '%s' attempt %d/%d failed: %s",
                        name,
                        attempt + 1,
                        config.retry_max_attempts,
                        e,
                    )

                # Exponential backoff with jitter
                if config.retry_jitter:
                    # S311: random is fine for jitter - not cryptographic
                    jitter = random.uniform(0, delay * 0.1)
                    wait_time = delay + jitter
                else:
                    wait_time = delay

                await asyncio.sleep(wait_time)
                delay = min(
                    delay * config.retry_exponential_base,
                    config.retry_max_delay,
                )

            log.error(
                "Reconnection '%s' failed after %d attempts",
                name,
                config.retry_max_attempts,
            )
            return False

        @staticmethod
        async def execute_with_timeout_and_cancel(
            coro: Coroutine[object, object, T],
            timeout: float,
            operation_name: str,
        ) -> tuple[T | None, bool]:
            """Execute coroutine with timeout and proper task cancellation.

            CRITICAL: asyncio.wait_for() doesn't guarantee cleanup of child tasks.
            This helper ensures:
            1. Task is explicitly created for tracking
            2. On timeout, task is explicitly cancelled
            3. We wait for cancellation to complete (no orphan tasks)

            Args:
                coro: Coroutine to execute.
                timeout: Timeout in seconds.
                operation_name: Name for logging.

            Returns:
                Tuple of (result, timed_out) where:
                - result: Result of coroutine, or None on timeout/cancel
                - timed_out: True if operation timed out, False otherwise

            Raises:
                ValueError: If timeout <= 0.
                Exception: Any non-timeout exception from the coroutine.

            """
            if timeout <= 0:
                msg = f"timeout must be > 0, got {timeout}"
                raise ValueError(msg)

            task: asyncio.Task[T] = asyncio.create_task(coro)
            try:
                result = await asyncio.wait_for(task, timeout=timeout)
            except TimeoutError:
                # Check if result arrived just before timeout (race condition)
                if task.done() and not task.cancelled():
                    try:
                        result = task.result()
                        log.debug(
                            "%s completed at timeout boundary (%.1fs)",
                            operation_name,
                            timeout,
                        )
                    except Exception:  # noqa: BLE001, S110
                        pass
                    else:
                        return result, False

                # Task didn't complete - cancel it
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
                log.debug(
                    "%s cancelled after %.1fs timeout",
                    operation_name,
                    timeout,
                )
                return None, True
            else:
                return result, False

    # =========================================================================
    # CIRCUIT BREAKER
    # =========================================================================

    class CircuitBreaker:
        """Circuit breaker for fault tolerance.

        Implements the circuit breaker pattern to prevent cascading failures.
        Uses MT5Settings directly for configuration (no separate config class).

        States (from c.Resilience.CircuitBreakerState):
            CLOSED: Normal operation, requests pass through
            OPEN: Too many failures, requests blocked
            HALF_OPEN: Testing recovery, limited requests allowed

        Usage:
            cb = MT5Utilities.CircuitBreaker(config=mt5_settings, name="mt5-client")
            if cb.can_execute():
                try:
                    result = risky_operation()
                    cb.record_success()
                except Exception:
                    cb.record_failure()
                    raise
            else:
                raise MT5Utilities.Exceptions.CircuitBreakerOpenError()
        """

        def __init__(
            self,
            config: MT5Settings,
            name: str = "default",
        ) -> None:
            """Initialize circuit breaker.

            Args:
                config: MT5Settings with cb_threshold, cb_recovery, cb_half_open_max.
                name: Name for logging purposes.

            """
            self._settings = config
            self.name = name
            self._state = c.Resilience.CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time: datetime | None = None
            self._half_open_calls = 0
            self._lock = threading.RLock()

        @property
        def config(self) -> MT5Settings:
            """Get configuration."""
            return self._settings

        @property
        def state(self) -> c.Resilience.CircuitBreakerState:
            """Get current circuit state, transitioning if needed."""
            with self._lock:
                if (
                    self._state == c.Resilience.CircuitBreakerState.OPEN
                    and self._should_attempt_reset()
                ):
                    log.info(
                        "Circuit breaker '%s' transitioning OPEN -> HALF_OPEN",
                        self.name,
                    )
                    self._state = c.Resilience.CircuitBreakerState.HALF_OPEN
                    self._half_open_calls = 0
                return self._state

        @property
        def failure_count(self) -> int:
            """Get current failure count."""
            with self._lock:
                return self._failure_count

        @property
        def is_closed(self) -> bool:
            """Check if circuit is closed (normal operation)."""
            return self.state == c.Resilience.CircuitBreakerState.CLOSED

        @property
        def is_open(self) -> bool:
            """Check if circuit is open (blocking requests)."""
            return self.state == c.Resilience.CircuitBreakerState.OPEN

        def _should_attempt_reset(self) -> bool:
            """Check if enough time passed to attempt recovery."""
            if self._last_failure_time is None:
                return False
            elapsed = datetime.now(UTC) - self._last_failure_time
            return elapsed >= timedelta(seconds=self._settings.cb_recovery)

        def record_success(self) -> None:
            """Record a successful operation."""
            with self._lock:
                self._failure_count = 0
                self._success_count += 1
                if self._state == c.Resilience.CircuitBreakerState.HALF_OPEN:
                    log.info(
                        "Circuit breaker '%s' recovered: HALF_OPEN -> CLOSED",
                        self.name,
                    )
                    self._state = c.Resilience.CircuitBreakerState.CLOSED

        def record_failure(self) -> None:
            """Record a failed operation."""
            with self._lock:
                self._failure_count += 1
                self._last_failure_time = datetime.now(UTC)

                if self._state == c.Resilience.CircuitBreakerState.HALF_OPEN:
                    log.warning(
                        "Circuit breaker '%s' failed during recovery",
                        self.name,
                    )
                    self._state = c.Resilience.CircuitBreakerState.OPEN
                elif self._failure_count >= self._settings.cb_threshold:
                    log.warning(
                        "Circuit breaker '%s' opened after %d failures",
                        self.name,
                        self._failure_count,
                    )
                    self._state = c.Resilience.CircuitBreakerState.OPEN

        def can_execute(self) -> bool:
            """Check if a request is allowed through the circuit.

            CRITICAL FIX: Entire operation is now under lock to prevent race
            conditions where state could change between read and decision.
            Previously, reset() could be called between state read and action.
            """
            with self._lock:
                # Inline state check (don't call property which also locks)
                if (
                    self._state == c.Resilience.CircuitBreakerState.OPEN
                    and self._should_attempt_reset()
                ):
                    log.info(
                        "Circuit breaker '%s' transitioning OPEN -> HALF_OPEN",
                        self.name,
                    )
                    self._state = c.Resilience.CircuitBreakerState.HALF_OPEN
                    self._half_open_calls = 0

                current_state = self._state

                if current_state == c.Resilience.CircuitBreakerState.CLOSED:
                    return True

                if current_state == c.Resilience.CircuitBreakerState.HALF_OPEN:
                    if self._half_open_calls < self._settings.cb_half_open_max:
                        self._half_open_calls += 1
                        return True
                    return False

                return False  # OPEN state

        def reset(self) -> None:
            """Manually reset the circuit breaker to closed state."""
            with self._lock:
                log.info("Circuit breaker '%s' manually reset", self.name)
                self._state = c.Resilience.CircuitBreakerState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                self._last_failure_time = None
                self._half_open_calls = 0

        def get_status(self) -> dict[str, str | int]:
            """Get circuit breaker status for monitoring.

            Returns:
                Dictionary with circuit breaker state information.

            """
            with self._lock:
                status: dict[str, str | int] = {
                    "name": self.name,
                    "state": self._state.name,
                    "failure_count": self._failure_count,
                    "success_count": self._success_count,
                    "failure_threshold": self._settings.cb_threshold,
                }

                if self._last_failure_time:
                    status["last_failure"] = self._last_failure_time.isoformat()
                    if self._state == c.Resilience.CircuitBreakerState.OPEN:
                        recovery_at = self._last_failure_time + timedelta(
                            seconds=self._settings.cb_recovery
                        )
                        status["recovery_at"] = recovery_at.isoformat()

                return status

    # =========================================================================
    # TRANSACTION HANDLER (order_send orchestration)
    # =========================================================================

    class TransactionHandler:
        """Handler for critical transaction orchestration.

        Centralizes transaction logic used by _safe_order_send:
        - Request preparation with idempotency markers
        - Result classification and outcome determination
        - Retry decision logic

        All methods are static - no state stored.

        Contains RequestTracker as nested class for idempotency tracking.
        """

        class RequestTracker:
            """Track order requests to prevent double execution.

            Uses comment field as idempotency marker since MT5 doesn't have
            native support for request deduplication. Each order_send gets
            a unique request_id embedded in the comment field.

            MT5 Limitations:
            - No native idempotency (each request creates new order)
            - Comment field is 31 chars max
            - No "order already exists" detection

            Format: RQ<16chars>|<original_comment>
            Example: RQ1a2b3c4d5e6f7g8h|my_order

            CRITICAL FIX v4: Increased from 10 hex chars (40 bits) to 16 hex
            chars (64 bits) to reduce collision probability:
            - 10 chars: collision after ~1M requests (Birthday paradox)
            - 16 chars: collision after ~4B requests (~12 years at 10/sec)

            Nested inside TransactionHandler since it's only used
            for transaction idempotency tracking.
            """

            @staticmethod
            def generate_request_id() -> str:
                """Generate unique request ID for idempotency.

                Format: RQ + 16 hex chars = 18 chars total.
                Uses 64 bits of entropy (16 hex chars) to reduce collision risk.
                Birthday paradox: collision expected after ~4 billion requests.
                Fits in MT5 comment field (31 chars max, leaves 12 for original).

                CRITICAL FIX v4: Increased from 10 hex chars (40 bits) to 16 hex
                chars (64 bits). With 10 chars, collision expected after ~1M requests
                (in ~1 day at 10 orders/sec). With 16 chars, collision expected
                after ~4B requests (in ~12 years at 10 orders/sec).

                Returns:
                    18-character request ID starting with 'RQ'.

                """
                prefix = c.Validation.REQUEST_ID_PREFIX
                hex_len = c.Validation.REQUEST_ID_HEX_LENGTH
                return f"{prefix}{uuid.uuid4().hex[:hex_len]}"

            @staticmethod
            def mark_comment(comment: str | None, request_id: str) -> str:
                """Add request_id marker to comment field.

                Embeds request_id at the start of comment for later extraction.
                Preserves as much of original comment as possible.

                Args:
                    comment: Original comment (may be None or empty).
                    request_id: Request ID to embed (18 chars).

                Returns:
                    Marked comment: 'RQ<16chars>|<original>' or just 'RQ<16chars>'.

                """
                if comment:
                    # Leave room for request_id + separator + some original
                    max_original = 31 - len(request_id) - 1
                    return f"{request_id}|{comment[:max_original]}"
                return request_id

            @staticmethod
            def extract_request_id(comment: str | None) -> str | None:
                """Extract request_id from marked comment field.

                CRITICAL FIX: Added validation to prevent false matches:
                - Length must be exactly 18 chars (RQ + 16 hex)
                - Must start with "RQ"
                - Remaining 16 chars must be valid hex
                This prevents matching corrupted/concatenated comments.

                Args:
                    comment: Comment field from order/deal.

                Returns:
                    Request ID if found and valid, None otherwise.

                """
                prefix = c.Validation.REQUEST_ID_PREFIX
                if not comment or not comment.startswith(prefix):
                    return None

                # Extract candidate (before separator if present)
                candidate = comment.split("|")[0]

                # Validate length
                if len(candidate) != c.Validation.REQUEST_ID_LENGTH:
                    log.debug(
                        "Invalid request_id length: %d (expected %d)",
                        len(candidate),
                        c.Validation.REQUEST_ID_LENGTH,
                    )
                    return None

                # Validate hex portion (chars 2-18 should be hex)
                hex_part = candidate[len(c.Validation.REQUEST_ID_PREFIX) :]
                try:
                    int(hex_part, 16)  # Validate hex
                except ValueError:
                    log.debug(
                        "Invalid request_id hex portion: %s",
                        hex_part,
                    )
                    return None

                return candidate

        @staticmethod
        def prepare_request(
            request: dict[str, object],
            operation: str,
        ) -> tuple[dict[str, object], str]:
            """Prepare request with idempotency marker.

            Adds request_id to comment field for tracking and verification.

            Args:
                request: Order request dictionary.
                operation: Operation name for logging.

            Returns:
                Tuple of (modified_request, request_id).

            """
            tracker = MT5Utilities.TransactionHandler.RequestTracker
            request_id = tracker.generate_request_id()
            original_comment = request.get("comment", "") or ""
            request["comment"] = tracker.mark_comment(str(original_comment), request_id)
            log.debug(
                "TX_PREPARE: %s request_id=%s",
                operation,
                request_id,
            )
            return request, request_id

        @staticmethod
        def classify_result(
            retcode: int,
        ) -> c.Resilience.TransactionOutcome:
            """Classify result retcode into transaction outcome (PUBLIC API).

            This is the BRIDGE function between:
            - ErrorClassification (7 values, internal, detailed)
            - TransactionOutcome (5 values, public, simplified)

            Mapping:
                SUCCESS → SUCCESS
                PARTIAL → PARTIAL
                RETRYABLE → RETRY
                VERIFY_REQUIRED → VERIFY_REQUIRED
                PERMANENT → PERMANENT_FAILURE
                CONDITIONAL → VERIFY_REQUIRED (conservative, verify state)
                UNKNOWN → VERIFY_REQUIRED (conservative, verify state)

            Why CONDITIONAL/UNKNOWN → VERIFY_REQUIRED (not PERMANENT_FAILURE)?
            - These represent ambiguous states where order MAY have executed
            - Conservative approach: verify state before deciding
            - Prevents both: double execution (retry when executed) AND
              missed execution (fail when actually succeeded)

            Args:
                retcode: MT5 TradeRetcode value.

            Returns:
                TransactionOutcome indicating next action for caller.

            Example:
                >>> outcome = TransactionHandler.classify_result(10012)  # TIMEOUT
                >>> outcome == TransactionOutcome.VERIFY_REQUIRED
                True

            """
            classification = MT5Utilities.ErrorClassifier.classify_mt5_retcode(retcode)

            if classification == c.Resilience.ErrorClassification.SUCCESS:
                return c.Resilience.TransactionOutcome.SUCCESS
            if classification == c.Resilience.ErrorClassification.PARTIAL:
                return c.Resilience.TransactionOutcome.PARTIAL
            if classification == c.Resilience.ErrorClassification.RETRYABLE:
                return c.Resilience.TransactionOutcome.RETRY
            if classification == c.Resilience.ErrorClassification.VERIFY_REQUIRED:
                return c.Resilience.TransactionOutcome.VERIFY_REQUIRED
            if classification == c.Resilience.ErrorClassification.PERMANENT:
                return c.Resilience.TransactionOutcome.PERMANENT_FAILURE
            # CONDITIONAL and UNKNOWN - verify state (conservative approach)
            return c.Resilience.TransactionOutcome.VERIFY_REQUIRED

        @staticmethod
        def should_retry(
            outcome: c.Resilience.TransactionOutcome,
            attempt: int,
            max_attempts: int,
        ) -> bool:
            """Determine if transaction should be retried.

            Args:
                outcome: Current transaction outcome.
                attempt: Current attempt number (0-based).
                max_attempts: Maximum attempts allowed.

            Returns:
                True if retry is allowed.

            """
            if attempt >= max_attempts - 1:
                return False
            return outcome == c.Resilience.TransactionOutcome.RETRY

        @staticmethod
        def get_retry_settings(
            config: MT5Settings,
            operation: str,
        ) -> tuple[int, bool]:
            """Get retry configuration for operation.

            Args:
                config: MT5Settings instance.
                operation: Operation name.

            Returns:
                Tuple of (max_attempts, is_critical).

            """
            criticality = MT5Utilities.ErrorClassifier.get_operation_criticality(
                operation
            )
            is_critical = criticality == c.Resilience.OperationCriticality.CRITICAL
            max_attempts = (
                config.critical_retry_max_attempts
                if is_critical
                else config.retry_max_attempts
            )
            return max_attempts, is_critical

        @staticmethod
        def handle_success(
            cb: _CircuitBreakerRecorder,
            result: object,
            outcome: c.Resilience.TransactionOutcome,
        ) -> None:
            """Record success in circuit breaker and log if partial.

            Args:
                cb: CircuitBreaker instance.
                result: Order result for logging.
                outcome: Transaction outcome (SUCCESS or PARTIAL).

            """
            cb.record_success()
            if outcome == c.Resilience.TransactionOutcome.PARTIAL:
                log.warning("Order partially filled: %s", result)

        @staticmethod
        def raise_permanent(retcode: int, comment: str | None) -> NoReturn:
            """Raise PermanentError for non-retryable errors.

            Args:
                retcode: MT5 retcode that caused the error.
                comment: Error description.

            Raises:
                PermanentError: Always raised.

            """
            raise MT5Utilities.Exceptions.PermanentError(
                retcode, comment or f"Permanent error: {retcode}"
            )

        @staticmethod
        def raise_exhausted(
            operation: str,
            max_attempts: int,
            last_result: object | None,
            last_error: Exception | None,
        ) -> NoReturn:
            """Raise appropriate error after all retries exhausted.

            Args:
                operation: Operation name for error message.
                max_attempts: Number of attempts made.
                last_result: Last result received (if any).
                last_error: Last exception (if any).

            Raises:
                PermanentError: If we have a result with retcode.
                MaxRetriesError: Otherwise.

            """
            if isinstance(last_result, _RetcodeResultProto) and last_result.retcode:
                raise MT5Utilities.Exceptions.PermanentError(
                    last_result.retcode,
                    f"Max retries exceeded. Last retcode: {last_result.retcode}",
                )
            raise MT5Utilities.Exceptions.MaxRetriesError(
                operation, max_attempts, last_error
            )

    # =========================================================================
    # TRANSACTION ORCHESTRATOR
    # =========================================================================

    class TransactionOrchestrator:
        """Orchestrates order_send with full transaction safety.

        Manages the complete lifecycle of critical transactions:
        1. Request preparation (idempotency marker via TransactionHandler)
        2. Circuit breaker check (via injected callback)
        3. WAL logging (intent/sent/verified/failed via injected callbacks)
        4. gRPC execution (via injected callback)
        5. Result classification and outcome handling
        6. State verification for ambiguous responses (via injected callback)
        7. Retry with delay for transient errors

        All I/O operations are injected via Dependencies, making this
        class fully testable in isolation without MT5/gRPC infrastructure.

        Usage:
            deps = TransactionOrchestrator.Dependencies(
                execute_grpc=client._execute_order_grpc,
                verify_state=client._verify_order_state,
                health_check=client._quick_health_check,
                ...
            )
            orchestrator = TransactionOrchestrator(config, deps)
            result = await orchestrator.execute(request)
        """

        @dataclass
        class Dependencies:
            """Injected dependencies for transaction orchestration.

            All callbacks are async except circuit breaker operations.
            Optional callbacks (CB, WAL) can be None if feature is disabled.
            """

            # Required callbacks
            execute_grpc: Callable[
                [Mapping[str, object], int], Awaitable[object | None]
            ]
            verify_state: Callable[[object, str | None], Awaitable[object | None]]
            health_check: Callable[[], Awaitable[bool]]

            # Circuit breaker (optional - can be None if disabled)
            check_circuit_breaker: Callable[[str], None] | None = None
            record_success: Callable[[], None] | None = None
            record_failure: Callable[[], None] | None = None

            # WAL (optional - can be None if disabled)
            wal_log_intent: (
                Callable[[str, Mapping[str, object]], Awaitable[None]] | None
            ) = None
            wal_mark_sent: Callable[[str], Awaitable[None]] | None = None
            wal_mark_verified: (
                Callable[[str, Mapping[str, object]], Awaitable[None]] | None
            ) = None
            wal_mark_failed: Callable[[str, str], Awaitable[None]] | None = None

        def __init__(
            self,
            config: MT5Settings,
            deps: Dependencies,
        ) -> None:
            """Initialize orchestrator with config and dependencies.

            Args:
                config: MT5Settings with retry parameters.
                deps: Injected dependencies for I/O operations.

            """
            self._settings = config
            self._deps = deps

        async def execute(
            self,
            request: dict[str, object],
        ) -> object | None:
            """Execute order with full transaction safety.

            Args:
                request: Order request dictionary.

            Returns:
                OrderResult on success/partial fill.

            Raises:
                PermanentError: Non-retryable error.
                MaxRetriesError: Retries exhausted.

            """
            th = MT5Utilities.TransactionHandler
            operation = "order_send"

            max_attempts, _ = th.get_retry_settings(self._settings, operation)
            request, request_id = th.prepare_request(dict(request), operation)

            # WAL: Log intent BEFORE sending (crash recovery)
            if self._deps.wal_log_intent:
                await self._deps.wal_log_intent(request_id, dict(request))

            last_result: object | None = None
            last_error: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    # PRE-EXECUTION: Check circuit breaker
                    if self._deps.check_circuit_breaker:
                        self._deps.check_circuit_breaker(operation)

                    # WAL: Mark as sent (gRPC call initiated)
                    if self._deps.wal_mark_sent:
                        await self._deps.wal_mark_sent(request_id)

                    # EXECUTION: Send order via gRPC
                    result = await self._deps.execute_grpc(request, attempt)

                    # Handle empty response
                    if result is None:
                        verified = await self._handle_empty_response(request_id)
                        if verified:
                            return verified
                        # Continue to retry if healthy
                        delay = self._settings.calculate_critical_retry_delay(attempt)
                        await asyncio.sleep(delay)
                        continue

                    last_result = result

                    # CLASSIFY and HANDLE
                    retcode = getattr(result, "retcode", 0)
                    outcome = th.classify_result(retcode)

                    if outcome in {
                        c.Resilience.TransactionOutcome.SUCCESS,
                        c.Resilience.TransactionOutcome.PARTIAL,
                    }:
                        if self._deps.record_success:
                            self._deps.record_success()
                        if outcome == c.Resilience.TransactionOutcome.PARTIAL:
                            log.warning("Order partially filled: %s", result)
                        # WAL: Mark as verified
                        if self._deps.wal_mark_verified:
                            wal_data = {
                                "retcode": retcode,
                                "order": getattr(result, "order", 0),
                                "deal": getattr(result, "deal", 0),
                            }
                            await self._deps.wal_mark_verified(request_id, wal_data)
                        return result

                    if outcome == c.Resilience.TransactionOutcome.PERMANENT_FAILURE:
                        if self._deps.record_failure:
                            self._deps.record_failure()
                        if self._deps.wal_mark_failed:
                            await self._deps.wal_mark_failed(
                                request_id, f"Permanent: {retcode}"
                            )
                        comment = getattr(result, "comment", "")
                        th.raise_permanent(retcode, comment)

                    if outcome == c.Resilience.TransactionOutcome.VERIFY_REQUIRED:
                        log.warning(
                            "TX_VERIFY_REQUIRED: retcode=%d, request_id=%s",
                            retcode,
                            request_id,
                        )
                        verified = await self._deps.verify_state(result, request_id)
                        if verified:
                            if self._deps.record_success:
                                self._deps.record_success()
                            if self._deps.wal_mark_verified:
                                wal_data = {
                                    "retcode": getattr(verified, "retcode", 0),
                                    "order": getattr(verified, "order", 0),
                                    "deal": getattr(verified, "deal", 0),
                                }
                                await self._deps.wal_mark_verified(request_id, wal_data)
                            return verified
                        if self._deps.record_failure:
                            self._deps.record_failure()
                        if self._deps.wal_mark_failed:
                            await self._deps.wal_mark_failed(
                                request_id, f"Verification failed: retcode={retcode}"
                            )
                        th.raise_permanent(retcode, f"Verify failed: {request_id}")

                    # RETRY outcome: Record failure and delay
                    if self._deps.record_failure:
                        self._deps.record_failure()
                    delay = self._settings.calculate_critical_retry_delay(attempt)
                    log.warning(
                        "Retryable error %d, attempt %d/%d, retrying in %.2fs",
                        retcode,
                        attempt + 1,
                        max_attempts,
                        delay,
                    )
                    await asyncio.sleep(delay)

                except MT5Utilities.Exceptions.PermanentError:
                    raise
                except Exception as e:
                    last_error = e
                    if not MT5Utilities.ErrorClassifier.is_retryable_exception(e):
                        if self._deps.record_failure:
                            self._deps.record_failure()
                        raise
                    if self._deps.record_failure:
                        self._deps.record_failure()

                    # Check health before retry
                    if not await self._deps.health_check():
                        log.exception(
                            "order_send exception with MT5 unreachable - "
                            "UNSAFE to retry (request_id=%s)",
                            request_id,
                        )
                        # Try verification one more time
                        verified = await self._try_verify_synthetic(request_id)
                        if verified:
                            log.info(
                                "order_send exception but order found: %s",
                                request_id,
                            )
                            return verified
                        th.raise_permanent(
                            0,
                            f"MT5 unreachable after exception: {e} ({request_id})",
                        )

                    delay = self._settings.calculate_critical_retry_delay(attempt)
                    log.warning(
                        "Exception in order_send: %s, attempt %d/%d, MT5 healthy - "
                        "retrying in %.2fs",
                        e,
                        attempt + 1,
                        max_attempts,
                        delay,
                    )
                    await asyncio.sleep(delay)

            th.raise_exhausted(operation, max_attempts, last_result, last_error)
            return None  # Unreachable

        async def _handle_empty_response(self, request_id: str) -> object | None:
            """Handle empty (None) gRPC response.

            Args:
                request_id: Request ID for verification.

            Returns:
                Verified result if found, None otherwise.

            Raises:
                PermanentError: If MT5 unreachable after verification.

            """
            log.warning(
                "TX_EMPTY_RESPONSE: Empty result for order_send, "
                "verifying state before retry (request_id=%s)",
                request_id,
            )

            verified = await self._try_verify_synthetic(request_id)
            if verified:
                log.info(
                    "TX_EMPTY_RESPONSE: Order found via verification, "
                    "avoiding duplicate (request_id=%s)",
                    request_id,
                )
                if self._deps.record_success:
                    self._deps.record_success()
                return verified

            # Not found - check MT5 health before retry
            if not await self._deps.health_check():
                log.error(
                    "TX_EMPTY_RESPONSE: MT5 unreachable after verification, "
                    "UNSAFE to retry (request_id=%s)",
                    request_id,
                )
                MT5Utilities.TransactionHandler.raise_permanent(
                    0,
                    f"MT5 unreachable after empty response: {request_id}",
                )

            log.warning(
                "TX_EMPTY_RESPONSE: Order not found via verification, "
                "MT5 healthy - safe to retry (request_id=%s)",
                request_id,
            )
            if self._deps.record_failure:
                self._deps.record_failure()
            return None

        async def _try_verify_synthetic(self, request_id: str) -> object | None:
            """Try to verify order state using synthetic result.

            Creates a synthetic result with zero IDs for verification
            when we don't have actual order/deal IDs.

            Args:
                request_id: Request ID for verification.

            Returns:
                Verified result if found, None otherwise.

            """
            # Create synthetic result - the verify_state callback should
            # handle the case where order/deal are 0 by using request_id
            # to search in comment field
            synthetic_result = type(
                "SyntheticResult",
                (),
                {
                    "retcode": 0,
                    "deal": 0,
                    "order": 0,
                    "volume": 0.0,
                    "price": 0.0,
                    "bid": 0.0,
                    "ask": 0.0,
                    "comment": "",
                    "request_id": 0,
                },
            )()
            return await self._deps.verify_state(synthetic_result, request_id)

    # =========================================================================
    # REQUEST QUEUE - PARALLEL EXECUTION
    # =========================================================================

    class RequestQueue:
        """Priority queue with PARALLEL execution.

        IMPORTANT: This is NOT a sequential queue!
        - Multiple operations execute SIMULTANEOUSLY
        - Semaphore controls max concurrent (default 10)
        - Priority only affects ORDER of dispatch, not serialization

        Architecture:
        1. submit() → enqueue with priority
        2. dispatcher task → picks from queue, fires execution
        3. Multiple executions run in PARALLEL via asyncio.create_task()
        4. Semaphore limits concurrent to server capacity

        Example with max_concurrent=10:
            t=0ms: 15 requests submitted
            t=1ms: 10 tasks dispatched and running in parallel
            t=50ms: 3 tasks complete, 3 more dispatched (still 10 running)
            t=100ms: all 15 complete

        Features:
        - Priority ordering (CRITICAL > HIGH > NORMAL > LOW)
        - Parallel execution (NOT sequential)
        - Semaphore-controlled concurrency (match server workers)
        - Request coalescing (dedupe identical calls)
        - Backpressure when queue full

        Usage:
            queue = MT5Utilities.RequestQueue(config)
            await queue.start()

            result = await queue.submit(
                operation="symbol_info_tick",
                coro_factory=lambda: fetch_tick(),
                coalesce_key="symbol_info_tick:EURUSD",
            )

            await queue.stop()
        """

        @dataclass(order=True)
        class _Request:
            """Internal request wrapper for priority queue."""

            priority: int  # Lower = higher priority (0=CRITICAL, 3=LOW)
            timestamp: float = field(compare=False)
            key: str = field(compare=False)  # For coalescing
            coro_factory: Callable[[], Awaitable[object]] = field(compare=False)
            future: asyncio.Future[object] = field(compare=False)

        def __init__(self, config: MT5Settings) -> None:
            """Initialize request queue.

            Args:
                config: MT5Settings with queue_max_concurrent and queue_max_depth.

            """
            self._settings = config
            self._queue: asyncio.PriorityQueue[MT5Utilities.RequestQueue._Request] = (
                asyncio.PriorityQueue(maxsize=config.queue_max_depth)
            )
            # Semaphore controls HOW MANY can execute in parallel
            self._semaphore = asyncio.Semaphore(config.queue_max_concurrent)
            self._coalesce: dict[str, asyncio.Future[object]] = {}
            self._running = False
            self._dispatcher_task: asyncio.Task[None] | None = None
            self._active_tasks: set[asyncio.Task[None]] = set()

        async def start(self) -> None:
            """Start dispatcher. Called by connect()."""
            if self._running:
                return
            self._running = True
            # Single dispatcher that fires multiple parallel executions
            self._dispatcher_task = asyncio.create_task(self._dispatcher())
            log.debug("RequestQueue started")

        async def stop(self) -> None:
            """Stop dispatcher and wait for active tasks. Called by disconnect()."""
            self._running = False

            # Cancel dispatcher
            if self._dispatcher_task:
                self._dispatcher_task.cancel()
                with suppress(asyncio.CancelledError):
                    await self._dispatcher_task
                self._dispatcher_task = None

            # Wait for active tasks to complete (graceful drain)
            if self._active_tasks:
                log.debug(
                    "RequestQueue draining %d active tasks", len(self._active_tasks)
                )
                await asyncio.gather(*self._active_tasks, return_exceptions=True)
            self._active_tasks.clear()
            self._coalesce.clear()
            log.debug("RequestQueue stopped")

        async def submit(
            self,
            operation: str,
            coro_factory: Callable[[], Awaitable[T]],
            coalesce_key: str | None = None,
        ) -> T:
            """Submit request for parallel execution.

            Args:
                operation: Operation name (e.g., "order_send", "symbol_info")
                coro_factory: Callable that returns the awaitable
                coalesce_key: Optional key for deduplication

            Returns:
                Result from the operation (may execute in parallel with others)

            Raises:
                QueueFullError: If queue is at max_depth capacity.

            """
            # Get priority from OPERATION_CRITICALITY (inverted: 0=highest)
            criticality = c.Resilience.OPERATION_CRITICALITY.get(operation, 1)
            priority = 3 - criticality  # 3 (CRITICAL) -> 0, 0 (LOW) -> 3

            # Coalescing: return existing future if identical request pending
            if coalesce_key and coalesce_key in self._coalesce:
                existing_future = self._coalesce[coalesce_key]
                log.debug("Request coalesced: %s", coalesce_key)
                return cast("T", await existing_future)

            loop = asyncio.get_running_loop()
            future: asyncio.Future[object] = loop.create_future()
            request = self._Request(
                priority=priority,
                timestamp=loop.time(),
                key=coalesce_key or "",
                coro_factory=coro_factory,
                future=future,
            )

            if coalesce_key:
                self._coalesce[coalesce_key] = future

            try:
                # put_nowait raises QueueFull if at capacity (backpressure)
                self._queue.put_nowait(request)
            except asyncio.QueueFull:
                if coalesce_key:
                    self._coalesce.pop(coalesce_key, None)
                msg = f"Request queue full ({self._settings.queue_max_depth})"
                raise MT5Utilities.Exceptions.QueueFullError(msg) from None

            try:
                return cast("T", await future)
            finally:
                if coalesce_key:
                    self._coalesce.pop(coalesce_key, None)

        async def _dispatcher(self) -> None:
            """Dispatcher that fires PARALLEL executions.

            Does NOT wait for execution to complete before picking next.
            Uses create_task() to fire-and-forget, semaphore controls concurrency.
            """
            while self._running:
                try:
                    # Get next request (blocks if queue empty)
                    request = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=1.0,
                    )
                except TimeoutError:
                    continue

                # Acquire semaphore BEFORE dispatching (controls max parallel)
                await self._semaphore.acquire()

                # Fire execution WITHOUT WAITING - true parallelism
                task = asyncio.create_task(self._execute_and_release(request))
                self._active_tasks.add(task)
                task.add_done_callback(self._active_tasks.discard)

        async def _execute_and_release(self, request: _Request) -> None:
            """Execute request and release semaphore when done."""
            try:
                result: object = await request.coro_factory()
                if not request.future.done():
                    request.future.set_result(result)
            except Exception as e:  # noqa: BLE001 - propagate to future
                if not request.future.done():
                    request.future.set_exception(e)
            finally:
                # Release semaphore → next request can be dispatched
                self._semaphore.release()

        @property
        def active_count(self) -> int:
            """Number of currently executing operations."""
            return len(self._active_tasks)

        @property
        def pending_count(self) -> int:
            """Number of requests waiting in queue."""
            return self._queue.qsize()

        @property
        def is_running(self) -> bool:
            """Check if queue is running."""
            return self._running

    # =========================================================================
    # WRITE-AHEAD LOG (WAL) - ORDER PERSISTENCE
    # =========================================================================

    class WAL:
        """Write-Ahead Log for order operations.

        100% transparent - called internally by order_send.
        Persists order intent BEFORE sending to MT5.
        Enables recovery of incomplete orders after crash.

        Storage: SQLite with WAL mode for async-friendly writes.

        Lifecycle:
        1. log_intent() - Record order request BEFORE sending
        2. mark_sent() - Mark after gRPC call initiated
        3. mark_verified() - Mark after MT5 confirms execution
        4. OR mark_failed() - Mark after permanent failure

        Recovery (on reconnect):
        1. get_incomplete() - Find PENDING/SENT entries
        2. Verify each against MT5 history
        3. Update status accordingly

        Usage:
            wal = MT5Utilities.WAL(config)
            await wal.initialize()

            # Before sending order
            await wal.log_intent(request_id, request)
            await wal.mark_sent(request_id)

            # After MT5 response
            if success:
                await wal.mark_verified(request_id, result)
            else:
                await wal.mark_failed(request_id, error_msg)

            await wal.close()
        """

        class Status(IntEnum):
            """WAL entry status."""

            PENDING = 0  # Logged, not yet sent
            SENT = 1  # gRPC call initiated
            VERIFIED = 2  # MT5 confirmed execution
            FAILED = 3  # Permanent failure
            RECOVERED = 4  # Recovered after crash

        @dataclass
        class Entry:
            """WAL entry for an order operation."""

            request_id: str
            timestamp: datetime
            request_json: str  # Serialized request
            status: int  # WAL.Status value
            result_json: str | None = None
            error: str | None = None

        def __init__(self, config: MT5Settings) -> None:
            """Initialize WAL.

            Args:
                config: MT5Settings with wal_path and wal_retention_days.

            """
            self._settings = config
            self._db_path = Path(config.wal_path).expanduser()
            self._conn: aiosqlite.Connection | None = None
            self._lock = asyncio.Lock()
            self._initialized = False

        async def initialize(self) -> None:
            """Initialize WAL database. Called by connect()."""
            if self._initialized:
                return

            # Ensure directory exists
            self._db_path.parent.mkdir(parents=True, exist_ok=True)

            self._conn = await aiosqlite.connect(str(self._db_path))
            await self._conn.execute("PRAGMA journal_mode=WAL")  # Async-friendly
            await self._conn.execute("PRAGMA synchronous=NORMAL")

            await self._conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    request_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    status INTEGER NOT NULL,
                    result_json TEXT,
                    error TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON orders(status)
            """)
            await self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON orders(timestamp)
            """)
            await self._conn.commit()
            self._initialized = True
            log.debug("WAL initialized at %s", self._db_path)

        async def close(self) -> None:
            """Close WAL database. Called by disconnect()."""
            if self._conn:
                await self._conn.close()
                self._conn = None
            self._initialized = False
            log.debug("WAL closed")

        async def log_intent(
            self,
            request_id: str,
            request: Mapping[str, object],
        ) -> None:
            """Log order intent BEFORE sending.

            Args:
                request_id: Unique request identifier.
                request: Order request dictionary.

            """
            if not self._conn:
                return

            async with self._lock:
                await self._conn.execute(
                    """INSERT OR REPLACE INTO orders
                       (request_id, timestamp, request_json, status, updated_at)
                       VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                    (
                        request_id,
                        datetime.now(UTC).isoformat(),
                        orjson.dumps(request).decode(),
                        self.Status.PENDING,
                    ),
                )
                await self._conn.commit()
            log.debug("WAL: logged intent %s", request_id)

        async def mark_sent(self, request_id: str) -> None:
            """Mark as sent after gRPC call initiated.

            Args:
                request_id: Request identifier to mark.

            """
            if not self._conn:
                return

            async with self._lock:
                await self._conn.execute(
                    """UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE request_id = ?""",
                    (self.Status.SENT, request_id),
                )
                await self._conn.commit()
            log.debug("WAL: marked sent %s", request_id)

        async def mark_verified(
            self,
            request_id: str,
            result: Mapping[str, object],
        ) -> None:
            """Mark as verified after MT5 confirmation.

            Args:
                request_id: Request identifier to mark.
                result: Order result dictionary.

            """
            if not self._conn:
                return

            async with self._lock:
                await self._conn.execute(
                    """UPDATE orders SET status = ?, result_json = ?,
                       updated_at = CURRENT_TIMESTAMP
                       WHERE request_id = ?""",
                    (
                        self.Status.VERIFIED,
                        orjson.dumps(result).decode(),
                        request_id,
                    ),
                )
                await self._conn.commit()
            log.debug("WAL: marked verified %s", request_id)

        async def mark_failed(self, request_id: str, error: str) -> None:
            """Mark as permanently failed.

            Args:
                request_id: Request identifier to mark.
                error: Error description.

            """
            if not self._conn:
                return

            async with self._lock:
                await self._conn.execute(
                    """UPDATE orders SET status = ?, error = ?,
                       updated_at = CURRENT_TIMESTAMP
                       WHERE request_id = ?""",
                    (self.Status.FAILED, error, request_id),
                )
                await self._conn.commit()
            log.debug("WAL: marked failed %s", request_id)

        async def mark_recovered(
            self,
            request_id: str,
            result: dict[str, object] | None = None,
        ) -> None:
            """Mark as recovered after crash recovery.

            Args:
                request_id: Request identifier to mark.
                result: Optional result if order was found executed.

            """
            if not self._conn:
                return

            async with self._lock:
                if result:
                    await self._conn.execute(
                        """UPDATE orders SET status = ?, result_json = ?,
                           updated_at = CURRENT_TIMESTAMP
                           WHERE request_id = ?""",
                        (
                            self.Status.RECOVERED,
                            orjson.dumps(result).decode(),
                            request_id,
                        ),
                    )
                else:
                    await self._conn.execute(
                        """UPDATE orders SET status = ?,
                           updated_at = CURRENT_TIMESTAMP
                           WHERE request_id = ?""",
                        (self.Status.RECOVERED, request_id),
                    )
                await self._conn.commit()
            log.debug("WAL: marked recovered %s", request_id)

        async def get_incomplete(self) -> list[Entry]:
            """Get entries needing recovery (PENDING or SENT).

            Returns:
                List of incomplete entries ordered by timestamp.

            """
            if not self._conn:
                return []

            async with self._lock:
                cursor = await self._conn.execute(
                    """SELECT request_id, timestamp, request_json, status,
                              result_json, error
                       FROM orders
                       WHERE status IN (?, ?)
                       ORDER BY timestamp ASC""",
                    (self.Status.PENDING, self.Status.SENT),
                )
                rows = await cursor.fetchall()
                return [
                    self.Entry(
                        request_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        request_json=row[2],
                        status=row[3],
                        result_json=row[4],
                        error=row[5],
                    )
                    for row in rows
                ]

        async def get_entry(self, request_id: str) -> Entry | None:
            """Get specific entry by request_id.

            Args:
                request_id: Request identifier to look up.

            Returns:
                Entry if found, None otherwise.

            """
            if not self._conn:
                return None

            async with self._lock:
                cursor = await self._conn.execute(
                    """SELECT request_id, timestamp, request_json, status,
                              result_json, error
                       FROM orders
                       WHERE request_id = ?""",
                    (request_id,),
                )
                row = await cursor.fetchone()
                if row:
                    return self.Entry(
                        request_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        request_json=row[2],
                        status=row[3],
                        result_json=row[4],
                        error=row[5],
                    )
                return None

        async def cleanup_old(self, days: int | None = None) -> int:
            """Remove entries older than retention period.

            Only removes VERIFIED and FAILED entries (completed transactions).
            PENDING and SENT entries are never cleaned up automatically.

            Args:
                days: Override retention days (defaults to config.wal_retention_days).

            Returns:
                Number of entries removed.

            """
            if not self._conn:
                return 0

            retention = days if days is not None else self._settings.wal_retention_days
            cutoff = datetime.now(UTC) - timedelta(days=retention)

            async with self._lock:
                cursor = await self._conn.execute(
                    """DELETE FROM orders
                       WHERE status IN (?, ?, ?) AND timestamp < ?""",
                    (
                        self.Status.VERIFIED,
                        self.Status.FAILED,
                        self.Status.RECOVERED,
                        cutoff.isoformat(),
                    ),
                )
                await self._conn.commit()
                count = cursor.rowcount
                if count > 0:
                    log.info("WAL: cleaned up %d old entries", count)
                return count

        @property
        def is_initialized(self) -> bool:
            """Check if WAL is initialized."""
            return self._initialized

        @property
        def db_path(self) -> Path:
            """Get database file path."""
            return self._db_path


# Module-level alias for convenient imports
# Usage: from mt5linux.utilities import u
u = MT5Utilities
