"""Typed async boundary for generated mt5_pb2_grpc classes."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, cast

import grpc.aio

from mt5linux import generated_pb2 as mt5_pb2

if TYPE_CHECKING:

    class MT5ServiceStub:
        def __init__(self, channel: grpc.aio.Channel) -> None: ...
        async def HealthCheck(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.HealthStatus: ...
        async def Initialize(
            self, request: mt5_pb2.InitRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...
        async def Login(
            self, request: mt5_pb2.LoginRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...
        async def Shutdown(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.Empty: ...
        async def Version(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.MT5Version: ...
        async def LastError(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.ErrorInfo: ...
        async def GetConstants(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.Constants: ...
        async def GetMethods(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.MethodsResponse: ...
        async def GetModels(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.ModelsResponse: ...
        async def TerminalInfo(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        async def AccountInfo(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        async def GetProvisionedAccount(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.ProvisionedAccount: ...
        async def CreateDemoAccount(
            self, request: mt5_pb2.CreateDemoRequest, timeout: float | None = None
        ) -> mt5_pb2.ProvisionedAccount: ...
        async def SymbolsTotal(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        async def SymbolsGet(
            self, request: mt5_pb2.SymbolsRequest, timeout: float | None = None
        ) -> mt5_pb2.SymbolsResponse: ...
        async def SymbolInfo(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        async def SymbolInfoTick(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        async def SymbolSelect(
            self, request: mt5_pb2.SymbolSelectRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...
        async def CopyRatesFrom(
            self, request: mt5_pb2.CopyRatesRequest, timeout: float | None = None
        ) -> mt5_pb2.NumpyArray: ...
        async def CopyRatesFromPos(
            self, request: mt5_pb2.CopyRatesPosRequest, timeout: float | None = None
        ) -> mt5_pb2.NumpyArray: ...
        async def CopyRatesRange(
            self,
            request: mt5_pb2.CopyRatesRangeRequest,
            timeout: float | None = None,
        ) -> mt5_pb2.NumpyArray: ...
        async def CopyTicksFrom(
            self, request: mt5_pb2.CopyTicksRequest, timeout: float | None = None
        ) -> mt5_pb2.NumpyArray: ...
        async def CopyTicksRange(
            self,
            request: mt5_pb2.CopyTicksRangeRequest,
            timeout: float | None = None,
        ) -> mt5_pb2.NumpyArray: ...
        async def OrderCalcMargin(
            self, request: mt5_pb2.MarginRequest, timeout: float | None = None
        ) -> mt5_pb2.FloatResponse: ...
        async def OrderCalcProfit(
            self, request: mt5_pb2.ProfitRequest, timeout: float | None = None
        ) -> mt5_pb2.FloatResponse: ...
        async def OrderCheck(
            self, request: mt5_pb2.OrderRequest, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        async def OrderSend(
            self, request: mt5_pb2.OrderRequest, timeout: float | None = None
        ) -> mt5_pb2.DictData: ...
        async def PositionsTotal(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        async def PositionsGet(
            self, request: mt5_pb2.PositionsRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        async def OrdersTotal(
            self, request: mt5_pb2.Empty, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        async def OrdersGet(
            self, request: mt5_pb2.OrdersRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        async def HistoryOrdersTotal(
            self, request: mt5_pb2.HistoryRequest, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        async def HistoryOrdersGet(
            self, request: mt5_pb2.HistoryRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        async def HistoryDealsTotal(
            self, request: mt5_pb2.HistoryRequest, timeout: float | None = None
        ) -> mt5_pb2.IntResponse: ...
        async def HistoryDealsGet(
            self, request: mt5_pb2.HistoryRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        async def MarketBookAdd(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...
        async def MarketBookGet(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.DictList: ...
        async def MarketBookRelease(
            self, request: mt5_pb2.SymbolRequest, timeout: float | None = None
        ) -> mt5_pb2.BoolResponse: ...

else:
    _real = import_module("mt5linux.mt5_pb2_grpc")
    MT5ServiceStub = cast("type[MT5ServiceStub]", _real.MT5ServiceStub)
