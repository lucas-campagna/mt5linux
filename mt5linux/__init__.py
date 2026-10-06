from .constants import Constants
from .metatrader5 import MetaTrader5 as MetaTrader5Base
from .types import (
    MT5_TYPES,
    AccountInfo,
    BookInfo,
    OrderCheckResult,
    OrderSendResult,
    SymbolInfo,
    TerminalInfo,
    Tick,
    TradeDeal,
    TradeOrder,
    TradePosition,
    TradeRequest,
)


class MetaTrader5(MetaTrader5Base, Constants):
    pass


__all__ = [
    "MT5_TYPES",
    "AccountInfo",
    "BookInfo",
    "MetaTrader5",
    "OrderCheckResult",
    "OrderSendResult",
    "SymbolInfo",
    "TerminalInfo",
    "Tick",
    "TradeDeal",
    "TradeOrder",
    "TradePosition",
    "TradeRequest",
]
