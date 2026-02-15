from .constants import Constants
from .metatrader5 import MetaTrader5 as MetaTrader5Base


class MetaTrader5(MetaTrader5Base, Constants):
    pass


__all__ = ["MetaTrader5"]
