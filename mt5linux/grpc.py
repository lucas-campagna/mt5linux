"""gRPC transport surface for mt5linux.

This module is additive to the upstream RPyC runtime: it publishes the gRPC
client, bridge models and settings without changing the upstream
``MetaTrader5`` entry point. The bridge server runs inside the MetaTrader 5
container (``python -m mt5linux.bridge``) and the client talks to it over the
gRPC endpoint.

Copyright (c) 2026 Marlon Costa. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from mt5linux.async_client import AsyncMetaTrader5 as AsyncGrpcMetaTrader5
from mt5linux.client import MetaTrader5 as GrpcMetaTrader5
from mt5linux.grpc_constants import MT5Constants
from mt5linux.grpc_types import MT5Types
from mt5linux.models import MT5Models
from mt5linux.protocols import AsyncMT5Protocol, MT5Protocol
from mt5linux.settings import MT5Settings
from mt5linux.utilities import MT5Utilities

__all__ = [
    "AsyncGrpcMetaTrader5",
    "AsyncMT5Protocol",
    "GrpcMetaTrader5",
    "MT5Constants",
    "MT5Models",
    "MT5Protocol",
    "MT5Settings",
    "MT5Types",
    "MT5Utilities",
]
