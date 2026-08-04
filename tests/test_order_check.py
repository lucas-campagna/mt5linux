import unittest
from unittest.mock import patch, MagicMock

import rpyc


class FakeConnection:
    def __init__(self):
        self._config = {}
        self.executed = []
        self.evaluated = []

    def execute(self, code):
        self.executed.append(code)

    def eval(self, code):
        self.evaluated.append(code)
        return "order-check-result"


class OrderCheckTests(unittest.TestCase):
    def setUp(self):
        self.connection = FakeConnection()
        self.mock_runtime = MagicMock()
        self.mock_runtime.start_container.return_value = None
        self.mock_runtime._name = "test-container"

    @patch("mt5linux._container_manager.create_runtime")
    @patch("mt5linux._container_manager.rpyc")
    def test_order_check_forwards_request_as_single_argument(
        self, mock_rpyc, mock_create_runtime
    ):
        mock_connection = MagicMock()
        mock_connection._config = {}
        mock_connection.execute = self.connection.execute
        mock_connection.eval = self.connection.eval
        mock_rpyc.classic.connect.return_value = mock_connection
        mock_rpyc.classic.obtain.side_effect = lambda x: x
        mock_create_runtime.return_value = self.mock_runtime

        from mt5linux.metatrader5 import MetaTrader5

        mt5 = MetaTrader5(host="mt5", port=8001)

        result = mt5.order_check({"action": 1, "symbol": "XAUUSD", "volume": 0.01})

        self.assertEqual(result, "order-check-result")
        self.assertEqual(
            self.connection.evaluated[-1],
            "mt5.order_check({'action': 1, 'symbol': 'XAUUSD', 'volume': 0.01})",
        )

    @patch("mt5linux._container_manager.create_runtime")
    @patch("mt5linux._container_manager.rpyc")
    def test_order_check_request_keyword_uses_same_call_shape(
        self, mock_rpyc, mock_create_runtime
    ):
        mock_connection = MagicMock()
        mock_connection._config = {}
        mock_connection.execute = self.connection.execute
        mock_connection.eval = self.connection.eval
        mock_rpyc.classic.connect.return_value = mock_connection
        mock_rpyc.classic.obtain.side_effect = lambda x: x
        mock_create_runtime.return_value = self.mock_runtime

        from mt5linux.metatrader5 import MetaTrader5

        mt5 = MetaTrader5(host="mt5", port=8001)

        result = mt5.order_check(
            request={"action": 1, "symbol": "XAUUSD", "volume": 0.01}
        )

        self.assertEqual(result, "order-check-result")
        self.assertEqual(
            self.connection.evaluated[-1],
            "mt5.order_check({'action': 1, 'symbol': 'XAUUSD', 'volume': 0.01})",
        )

    @patch("mt5linux._container_manager.create_runtime")
    @patch("mt5linux._container_manager.rpyc")
    def test_order_check_uses_repr_for_request_literal(
        self, mock_rpyc, mock_create_runtime
    ):
        mock_connection = MagicMock()
        mock_connection._config = {}
        mock_connection.execute = self.connection.execute
        mock_connection.eval = self.connection.eval
        mock_rpyc.classic.connect.return_value = mock_connection
        mock_rpyc.classic.obtain.side_effect = lambda x: x
        mock_create_runtime.return_value = self.mock_runtime

        from mt5linux.metatrader5 import MetaTrader5

        mt5 = MetaTrader5(host="mt5", port=8001)

        result = mt5.order_check("not a request dict")

        self.assertEqual(result, "order-check-result")
        self.assertEqual(
            self.connection.evaluated[-1], "mt5.order_check('not a request dict')"
        )


if __name__ == "__main__":
    unittest.main()
