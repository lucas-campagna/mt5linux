"""End-to-end tracking of issue #51.

order_send() must not be rejected with retcode 10027 (AutoTrading disabled
by client). Reported cause: docker/src/config.sh writes [Experts] Enabled=0
and nothing enables the AutoTrading toolbar, so the container can log in and
read data but cannot trade.

The default test is safe (no order is placed): it checks the terminal's
trade_allowed flag. Both tests extract scalars server-side (container.eval)
so they do not depend on the serialization fix for issue #57. The order_send
test is opt-in because it places (and closes) a real market order on the
configured account.

https://github.com/lucas-campagna/mt5linux/issues/51
"""

import os

import pytest
from helpers import SYMBOL

pytestmark = pytest.mark.e2e

ISSUE = "https://github.com/lucas-campagna/mt5linux/issues/51"
RETCODE_AUTO_TRADING_DISABLED = 10027


def test_terminal_reports_trading_allowed(mt5_initialized):
    allowed = mt5_initialized.container.eval(
        "mt5.terminal_info().trade_allowed"
    )

    assert allowed is True, (
        "AutoTrading is disabled in the terminal: order_send() will fail "
        f"with retcode 10027 ({ISSUE})"
    )


@pytest.mark.trading
def test_order_send_is_not_blocked_by_autotrading(mt5_initialized):
    if os.environ.get("MT5_E2E_ALLOW_ORDER_SEND") != "1":
        pytest.skip(
            "set MT5_E2E_ALLOW_ORDER_SEND=1 to let this test place (and "
            "close) a real market order on the configured account"
        )
    container = mt5_initialized.container

    volume = container.eval(f"mt5.symbol_info({SYMBOL!r}).volume_min")
    price = container.eval(f"mt5.symbol_info_tick({SYMBOL!r}).ask")
    if not (volume and price):
        pytest.skip(f"no quote for {SYMBOL} on this account")

    request = {
        "action": 1,  # TRADE_ACTION_DEAL
        "symbol": SYMBOL,
        "volume": float(volume),
        "type": 0,  # ORDER_TYPE_BUY
        "price": float(price),
        "deviation": 20,
        "magic": 0,
        "comment": "mt5linux e2e (issue #51)",
        "type_time": 0,
        "type_filling": 2,  # ORDER_FILLING_RETURN (broker-dependent)
    }
    try:
        retcode = container.eval(f"mt5.order_send({request!r}).retcode")
        assert retcode != RETCODE_AUTO_TRADING_DISABLED, (
            f"order_send() rejected with retcode 10027 ({ISSUE})"
        )
    finally:
        _close_symbol_positions(container, SYMBOL)


def _close_symbol_positions(container, symbol):
    """Best-effort close of positions left open by the order_send test."""
    try:
        positions = container.eval(
            f"[(p.ticket, p.type, p.volume) for p in mt5.positions_get() "
            f"if p.symbol == {symbol!r}]"
        )
    except Exception:
        return
    for ticket, position_type, volume in positions:
        try:
            close_type = 1 if position_type == 0 else 0
            tick = "bid" if position_type == 0 else "ask"
            price = container.eval(
                f"mt5.symbol_info_tick({symbol!r}).{tick}"
            )
            request = {
                "action": 1,
                "position": ticket,
                "symbol": symbol,
                "volume": float(volume),
                "type": close_type,
                "price": float(price),
                "deviation": 20,
                "magic": 0,
                "comment": "mt5linux e2e cleanup",
                "type_time": 0,
                "type_filling": 2,
            }
            container.eval(f"mt5.order_send({request!r})")
        except Exception:
            pass
