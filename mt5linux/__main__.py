"""Command-line entrypoint for the mt5linux RPyC classic server."""

from __future__ import annotations

from rpyc.cli.rpyc_classic import ClassicServer

if __name__ == "__main__":
    ClassicServer.run()
