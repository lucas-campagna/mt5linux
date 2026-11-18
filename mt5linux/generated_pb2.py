"""Typed boundary for generated mt5_pb2 protobuf classes."""

from __future__ import annotations

from collections.abc import Sequence
from importlib import import_module
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:

    class Empty:
        """Empty protobuf message."""

        def __init__(self) -> None: ...

    class BoolResponse:
        result: bool

        def __init__(self, result: bool = False) -> None: ...

    class IntResponse:
        value: int

        def __init__(self, value: int = 0) -> None: ...

    class FloatResponse:
        value: float

        def __init__(self, value: float = 0.0) -> None: ...
        def HasField(self, name: str) -> bool: ...

    class ErrorInfo:
        code: int
        message: str

        def __init__(self, code: int = 0, message: str = "") -> None: ...

    class MT5Version:
        major: int
        minor: int
        build: str

        def __init__(
            self,
            major: int = 0,
            minor: int = 0,
            build: str = "",
        ) -> None: ...

    class Constants:
        values: dict[str, int]

        def __init__(self, values: dict[str, int] | None = None) -> None: ...

    class ParameterInfo:
        name: str
        type_hint: str
        kind: str
        has_default: bool
        default_value: str

        def __init__(
            self,
            name: str = "",
            type_hint: str = "",
            kind: str = "",
            has_default: bool = False,
            default_value: str = "",
        ) -> None: ...

    class MethodInfo:
        name: str
        parameters: list[ParameterInfo]
        return_type: str
        is_callable: bool

        def __init__(
            self,
            name: str = "",
            parameters: list[ParameterInfo] | None = None,
            return_type: str = "",
            is_callable: bool = False,
        ) -> None: ...

    class MethodsResponse:
        methods: list[MethodInfo]
        total: int

        def __init__(
            self,
            methods: list[MethodInfo] | None = None,
            total: int = 0,
        ) -> None: ...

    class FieldInfo:
        name: str
        type_hint: str
        index: int

        def __init__(
            self,
            name: str = "",
            type_hint: str = "",
            index: int = 0,
        ) -> None: ...

    class ModelInfo:
        name: str
        fields: list[FieldInfo]
        is_namedtuple: bool

        def __init__(
            self,
            name: str = "",
            fields: list[FieldInfo] | None = None,
            is_namedtuple: bool = False,
        ) -> None: ...

    class ModelsResponse:
        models: list[ModelInfo]
        total: int

        def __init__(
            self,
            models: list[ModelInfo] | None = None,
            total: int = 0,
        ) -> None: ...

    class DictData:
        json_data: str

        def __init__(self, json_data: str = "") -> None: ...

    class DictList:
        json_items: list[str]

        def __init__(self, json_items: list[str] | None = None) -> None: ...

    class NumpyArray:
        data: bytes
        dtype: str
        shape: Sequence[int]

        def __init__(
            self,
            data: bytes = b"",
            dtype: str = "",
            shape: Sequence[int] | None = None,
        ) -> None: ...

    class SymbolsResponse:
        total: int
        chunks: Sequence[str]

        def __init__(
            self,
            total: int = 0,
            chunks: Sequence[str] | None = None,
        ) -> None: ...

    class HealthStatus:
        healthy: bool
        mt5_available: bool
        connected: bool
        trade_allowed: bool
        build: int
        reason: str

        def __init__(
            self,
            healthy: bool = False,
            mt5_available: bool = False,
            connected: bool = False,
            trade_allowed: bool = False,
            build: int = 0,
            reason: str = "",
        ) -> None: ...

    class InitRequest:
        path: str
        login: int
        password: str
        server: str
        timeout: int
        portable: bool

        def __init__(
            self,
            path: str = "",
            login: int = 0,
            password: str = "",
            server: str = "",
            timeout: int = 0,
            portable: bool = False,
        ) -> None: ...
        def HasField(self, name: str) -> bool: ...

    class LoginRequest:
        login: int
        password: str
        server: str
        timeout: int

        def __init__(
            self,
            login: int = 0,
            password: str = "",
            server: str = "",
            timeout: int = 0,
        ) -> None: ...

    class SymbolRequest:
        symbol: str

        def __init__(self, symbol: str = "") -> None: ...

    class SymbolsRequest:
        group: str

        def __init__(self, group: str = "") -> None: ...
        def HasField(self, name: str) -> bool: ...

    class SymbolSelectRequest:
        symbol: str
        enable: bool

        def __init__(self, symbol: str = "", enable: bool = False) -> None: ...

    class CopyRatesRequest:
        symbol: str
        timeframe: int
        date_from: int
        count: int

        def __init__(
            self,
            symbol: str = "",
            timeframe: int = 0,
            date_from: int = 0,
            count: int = 0,
        ) -> None: ...

    class CopyRatesPosRequest:
        symbol: str
        timeframe: int
        start_pos: int
        count: int

        def __init__(
            self,
            symbol: str = "",
            timeframe: int = 0,
            start_pos: int = 0,
            count: int = 0,
        ) -> None: ...

    class CopyRatesRangeRequest:
        symbol: str
        timeframe: int
        date_from: int
        date_to: int

        def __init__(
            self,
            symbol: str = "",
            timeframe: int = 0,
            date_from: int = 0,
            date_to: int = 0,
        ) -> None: ...

    class CopyTicksRequest:
        symbol: str
        date_from: int
        count: int
        flags: int

        def __init__(
            self,
            symbol: str = "",
            date_from: int = 0,
            count: int = 0,
            flags: int = 0,
        ) -> None: ...

    class CopyTicksRangeRequest:
        symbol: str
        date_from: int
        date_to: int
        flags: int

        def __init__(
            self,
            symbol: str = "",
            date_from: int = 0,
            date_to: int = 0,
            flags: int = 0,
        ) -> None: ...

    class OrderRequest:
        json_request: str

        def __init__(self, json_request: str = "") -> None: ...

    class PositionsRequest:
        symbol: str
        group: str
        ticket: int

        def __init__(
            self,
            symbol: str = "",
            group: str = "",
            ticket: int = 0,
        ) -> None: ...
        def HasField(self, name: str) -> bool: ...

    class OrdersRequest:
        symbol: str
        group: str
        ticket: int

        def __init__(
            self,
            symbol: str = "",
            group: str = "",
            ticket: int = 0,
        ) -> None: ...
        def HasField(self, name: str) -> bool: ...

    class HistoryRequest:
        date_from: int
        date_to: int
        group: str
        ticket: int
        position: int

        def __init__(
            self,
            date_from: int = 0,
            date_to: int = 0,
            group: str = "",
            ticket: int = 0,
            position: int = 0,
        ) -> None: ...
        def HasField(self, name: str) -> bool: ...

    class MarginRequest:
        action: int
        symbol: str
        volume: float
        price: float

        def __init__(
            self,
            action: int = 0,
            symbol: str = "",
            volume: float = 0.0,
            price: float = 0.0,
        ) -> None: ...

    class ProfitRequest:
        action: int
        symbol: str
        volume: float
        price_open: float
        price_close: float

        def __init__(
            self,
            action: int = 0,
            symbol: str = "",
            volume: float = 0.0,
            price_open: float = 0.0,
            price_close: float = 0.0,
        ) -> None: ...

    class ProvisionedAccount:
        login: int
        server: str
        email: str
        created_at: str
        login_confirmed: bool
        credentials_persisted: bool
        connected: bool
        source: str

        def __init__(
            self,
            login: int = 0,
            server: str = "",
            email: str = "",
            created_at: str = "",
            login_confirmed: bool = False,
            credentials_persisted: bool = False,
            connected: bool = False,
            source: str = "",
        ) -> None: ...

    class CreateDemoRequest:
        server: str
        email: str
        phone: str
        first_name: str
        last_name: str
        dob_year: str

        def __init__(
            self,
            server: str = "",
            email: str = "",
            phone: str = "",
            first_name: str = "",
            last_name: str = "",
            dob_year: str = "",
        ) -> None: ...

else:
    _real = import_module("mt5linux.mt5_pb2")
    Empty = cast("type[Empty]", _real.Empty)
    BoolResponse = cast("type[BoolResponse]", _real.BoolResponse)
    IntResponse = cast("type[IntResponse]", _real.IntResponse)
    FloatResponse = cast("type[FloatResponse]", _real.FloatResponse)
    ErrorInfo = cast("type[ErrorInfo]", _real.ErrorInfo)
    MT5Version = cast("type[MT5Version]", _real.MT5Version)
    Constants = cast("type[Constants]", _real.Constants)
    ParameterInfo = cast("type[ParameterInfo]", _real.ParameterInfo)
    MethodInfo = cast("type[MethodInfo]", _real.MethodInfo)
    MethodsResponse = cast("type[MethodsResponse]", _real.MethodsResponse)
    FieldInfo = cast("type[FieldInfo]", _real.FieldInfo)
    ModelInfo = cast("type[ModelInfo]", _real.ModelInfo)
    ModelsResponse = cast("type[ModelsResponse]", _real.ModelsResponse)
    DictData = cast("type[DictData]", _real.DictData)
    DictList = cast("type[DictList]", _real.DictList)
    NumpyArray = cast("type[NumpyArray]", _real.NumpyArray)
    SymbolsResponse = cast("type[SymbolsResponse]", _real.SymbolsResponse)
    HealthStatus = cast("type[HealthStatus]", _real.HealthStatus)
    InitRequest = cast("type[InitRequest]", _real.InitRequest)
    LoginRequest = cast("type[LoginRequest]", _real.LoginRequest)
    SymbolRequest = cast("type[SymbolRequest]", _real.SymbolRequest)
    SymbolsRequest = cast("type[SymbolsRequest]", _real.SymbolsRequest)
    SymbolSelectRequest = cast("type[SymbolSelectRequest]", _real.SymbolSelectRequest)
    CopyRatesRequest = cast("type[CopyRatesRequest]", _real.CopyRatesRequest)
    CopyRatesPosRequest = cast(
        "type[CopyRatesPosRequest]",
        _real.CopyRatesPosRequest,
    )
    CopyRatesRangeRequest = cast(
        "type[CopyRatesRangeRequest]",
        _real.CopyRatesRangeRequest,
    )
    CopyTicksRequest = cast("type[CopyTicksRequest]", _real.CopyTicksRequest)
    CopyTicksRangeRequest = cast(
        "type[CopyTicksRangeRequest]",
        _real.CopyTicksRangeRequest,
    )
    OrderRequest = cast("type[OrderRequest]", _real.OrderRequest)
    PositionsRequest = cast("type[PositionsRequest]", _real.PositionsRequest)
    OrdersRequest = cast("type[OrdersRequest]", _real.OrdersRequest)
    HistoryRequest = cast("type[HistoryRequest]", _real.HistoryRequest)
    MarginRequest = cast("type[MarginRequest]", _real.MarginRequest)
    ProfitRequest = cast("type[ProfitRequest]", _real.ProfitRequest)
    ProvisionedAccount = cast("type[ProvisionedAccount]", _real.ProvisionedAccount)
    CreateDemoRequest = cast("type[CreateDemoRequest]", _real.CreateDemoRequest)
