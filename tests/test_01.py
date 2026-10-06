import unittest
from unittest.mock import patch, MagicMock

import rpyc


class TestMetaTrader5Instantiation(unittest.TestCase):
    def setUp(self):
        self.mock_runtime = MagicMock()
        self.mock_runtime.start_container.return_value = None
        self.mock_runtime._name = "test-container"

    @patch("mt5linux._container_manager.create_runtime")
    @patch("mt5linux._container_manager.rpyc")
    def test_meta_trader5_can_be_instantiated(self, mock_rpyc, mock_create_runtime):
        mock_rpyc.classic.connect.return_value = MagicMock()
        mock_create_runtime.return_value = self.mock_runtime

        from mt5linux import MetaTrader5

        mt5 = MetaTrader5(host="localhost", port=12345)
        self.assertIsNotNone(mt5)

    @patch("mt5linux._container_manager.create_runtime")
    @patch("mt5linux._container_manager.rpyc")
    def test_enable_algo_defaults_to_false(self, mock_rpyc, mock_create_runtime):
        mock_rpyc.classic.connect.return_value = MagicMock()
        mock_create_runtime.return_value = self.mock_runtime

        from mt5linux import MetaTrader5

        MetaTrader5(host="localhost", port=12345)

        self.assertFalse(self.mock_runtime.start_container.call_args.kwargs["enable_algo"])

    @patch("mt5linux._container_manager.create_runtime")
    @patch("mt5linux._container_manager.rpyc")
    def test_enable_algo_true_reaches_start_container(self, mock_rpyc, mock_create_runtime):
        mock_rpyc.classic.connect.return_value = MagicMock()
        mock_create_runtime.return_value = self.mock_runtime

        from mt5linux import MetaTrader5

        MetaTrader5(host="localhost", port=12345, enable_algo=True)

        self.assertTrue(self.mock_runtime.start_container.call_args.kwargs["enable_algo"])


if __name__ == "__main__":
    unittest.main()
