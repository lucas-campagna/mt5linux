"""Typed sync boundary for generated mt5_pb2_grpc classes."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, cast

import grpc

from mt5linux import generated_pb2 as mt5_pb2

if TYPE_CHECKING:

    class MT5ServiceStub:
        def __init__(self, channel: grpc.Channel) -> None: ...
        def HealthCheck(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.HealthStatus: ...
        def Initialize(
            self, request: mt5_pb2.InitRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...
        def Login(
            self, request: mt5_pb2.LoginRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...
        def Shutdown(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.Empty: ...
        def Version(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.MT5Version: ...
        def LastError(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.ErrorInfo: ...
        def GetConstants(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.Constants: ...
        def GetMethods(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.MethodsResponse: ...
        def GetModels(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.ModelsResponse: ...
        def TerminalInfo(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        def AccountInfo(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        def GetProvisionedAccount(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.ProvisionedAccount: ...
        def CreateDemoAccount(
            self, request: mt5_pb2.CreateDemoRequest, timeout: float | None = None
        ) -> mt5_pb2.ProvisionedAccount: ...
        def SymbolsTotal(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        def SymbolsGet(
            self, request: mt5_pb2.SymbolsRequest, timeout: float | None = None
        ) -> mt5_pb2.SymbolsResponse: ...
        def SymbolInfo(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        def SymbolInfoTick(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        def SymbolSelect(
            self, request: mt5_pb2.SymbolSelectRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...
        def CopyRatesFrom(
            self, request: mt5_pb2.CopyRatesRequest, timeout: float | None = None
        ) -> mt5_pb2.NumpyArray: ...
        def CopyRatesFromPos(
            self, request: mt5_pb2.CopyRatesPosRequest, timeout: float | None = None
        ) -> mt5_pb2.NumpyArray: ...
        def CopyRatesRange(
            self,
            request: mt5_pb2.CopyRatesRangeRequest,
            timeout: float | None = None,
        ) -> mt5_pb2.NumpyArray: ...
        def CopyTicksFrom(
            self, request: mt5_pb2.CopyTicksRequest, timeout: float | None = None
        ) -> mt5_pb2.NumpyArray: ...
        def CopyTicksRange(
            self,
            request: mt5_pb2.CopyTicksRangeRequest,
            timeout: float | None = None,
        ) -> mt5_pb2.NumpyArray: ...
        def OrderCalcMargin(
            self, request: mt5_pb2.MarginRequest, timeout: float | None = None
        ) -> mt5_pb2.FloatResponse: ...
        def OrderCalcProfit(
            self, request: mt5_pb2.ProfitRequest, timeout: float | None = None
        ) -> mt5_pb2.FloatResponse: ...
        def OrderCheck(
            self, request: mt5_pb2.OrderRequest, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        def OrderSend(
            self, request: mt5_pb2.OrderRequest, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        def PositionsTotal(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        def PositionsGet(
            self, request: mt5_pb2.PositionsRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        def OrdersTotal(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        def OrdersGet(
            self, request: mt5_pb2.OrdersRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        def HistoryOrdersTotal(
            self, request: mt5_pb2.HistoryRequest, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        def HistoryOrdersGet(
            self, request: mt5_pb2.HistoryRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        def HistoryDealsTotal(
            self, request: mt5_pb2.HistoryRequest, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        def HistoryDealsGet(
            self, request: mt5_pb2.HistoryRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        def MarketBookAdd(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...
        def MarketBookGet(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        def MarketBookRelease(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...

    class MT5ServiceServicer:
        """Nominal gRPC servicer base."""

    def add_MT5ServiceServicer_to_server(
        servicer: MT5ServiceServicer,
        server: grpc.Server,
    ) -> None: ...

else:
    _real = import_module("mt5linux.mt5_pb2_grpc")
    MT5ServiceStub = cast("type[MT5ServiceStub]", _real.MT5ServiceStub)
    MT5ServiceServicer = cast("type[MT5ServiceServicer]", _real.MT5ServiceServicer)
    add_MT5ServiceServicer_to_server = _real.add_MT5ServiceServicer_to_server
