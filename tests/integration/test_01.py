import unittest
import os
from dotenv import load_dotenv

from mt5linux import MetaTrader5

load_dotenv()


class TestBasicContainerInitialization(unittest.TestCase):
    def test_basic_container_initialization(self):
        mt5 = MetaTrader5(image_tag="local")
        assert mt5.initialize(
            server=os.environ["SERVER"],
            login=int(os.environ["LOGIN"]),
            password=os.environ["PASSWORD"],
        )


if __name__ == "__main__":
    unittest.main()
