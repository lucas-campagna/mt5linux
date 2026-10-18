#!/usr/bin/env python3
"""Minimal RPyC server simulating an MT5 server for standalone engine tests."""

import sys
import importlib
import types
import rpyc
from rpyc.core.service import Service


class MT5Service(Service):
    _namespace = {}

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def getmodule(self, name):
        if isinstance(name, tuple):
            name = ".".join(name)
        return importlib.import_module(name)

    def exposed_eval(self, expr):
        return eval(expr, self._namespace)

    def exposed_execute(self, code):
        try:
            exec(code, self._namespace)
        except ModuleNotFoundError as e:
            if "MetaTrader5" in str(e):
                mt5_mod = types.ModuleType("mt5")
                mt5_mod.initialize = lambda *args, **kwargs: True
                mt5_mod.shutdown = lambda *args, **kwargs: None
                mt5_mod.version = lambda *args, **kwargs: [500, 2007, "25 Feb 2019"]
                mt5_mod.last_error = lambda *args, **kwargs: (1, "ok")
                mt5_mod.terminal_info = lambda *args, **kwargs: {
                    "__TAG__": "TerminalInfo",
                    "community_account": True,
                    "community_connection": True,
                    "connected": True,
                    "dlls_allowed": False,
                    "trade_allowed": False,
                }
                mt5_mod.account_info = lambda *args, **kwargs: {
                    "__TAG__": "AccountInfo",
                    "login": 123456,
                    "trade_mode": 0,
                    "leverage": 100,
                    "balance": 10000.0,
                }
                self._namespace["mt5"] = mt5_mod
            else:
                raise

    @property
    def exposed_namespace(self):
        return self._namespace

    def exposed_initialize(self, *args, **kwargs):
        return True

    def exposed_version(self, *args, **kwargs):
        return [500, 2007, "25 Feb 2019"]

    def exposed_last_error(self, *args, **kwargs):
        return (1, "ok")

    def exposed_shutdown(self, *args, **kwargs):
        return None

    def exposed_terminal_info(self, *args, **kwargs):
        return {
            "__TAG__": "TerminalInfo",
            "community_account": True,
            "community_connection": True,
            "connected": True,
            "dlls_allowed": False,
            "trade_allowed": False,
        }

    def exposed_account_info(self, *args, **kwargs):
        return {
            "__TAG__": "AccountInfo",
            "login": 123456,
            "trade_mode": 0,
            "leverage": 100,
            "balance": 10000.0,
        }


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(
        MT5Service(),
        port=18812,
        protocol_config={"allow_public_attrs": True},
    )
    print(f"RPyC MT5 server listening on port 18812", flush=True)
    server.start()
