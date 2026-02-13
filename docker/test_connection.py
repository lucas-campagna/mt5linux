from mt5linux import MetaTrader5

print("Establishing connection...")
mt5 = MetaTrader5(host="localhost", port=8001)

print("Closing connection...")
mt5.shutdown()
