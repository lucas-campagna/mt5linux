from mt5linux import MetaTrader5

mt5 = MetaTrader5(port=1235)
mt5.initialize()
print(mt5.terminal_info())
mt5.shutdown()
assert True