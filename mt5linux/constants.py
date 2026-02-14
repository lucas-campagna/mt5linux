# Constants
ACCOUNT_MARGIN_MODE_RETAIL_NETTING = 0
ACCOUNT_MARGIN_MODE_EXCHANGE = 1
ACCOUNT_MARGIN_MODE_RETAIL_HEDGING = 2

ACCOUNT_STOPOUT_MODE_PERCENT = 0
ACCOUNT_STOPOUT_MODE_MONEY = 1

ACCOUNT_TRADE_MODE_DEMO = 0
ACCOUNT_TRADE_MODE_CONTEST = 1
ACCOUNT_TRADE_MODE_REAL = 2

COPY_TICKS_ALL = -1
COPY_TICKS_INFO = 1
COPY_TICKS_TRADE = 2

DAY_OF_WEEK_SUNDAY = 0
DAY_OF_WEEK_MONDAY = 1
DAY_OF_WEEK_TUESDAY = 2
DAY_OF_WEEK_WEDNESDAY = 3
DAY_OF_WEEK_THURSDAY = 4
DAY_OF_WEEK_FRIDAY = 5
DAY_OF_WEEK_SATURDAY = 6

DEAL_DIVIDEND = 15
DEAL_DIVIDEND_FRANKED = 16

DEAL_ENTRY_IN = 0
DEAL_ENTRY_OUT = 1
DEAL_ENTRY_INOUT = 2
DEAL_ENTRY_OUT_BY = 3

DEAL_REASON_CLIENT = 0
DEAL_REASON_MOBILE = 1
DEAL_REASON_WEB = 2
DEAL_REASON_EXPERT = 3
DEAL_REASON_SL = 4
DEAL_REASON_TP = 5
DEAL_REASON_SO = 6
DEAL_REASON_ROLLOVER = 7
DEAL_REASON_VMARGIN = 8
DEAL_REASON_SPLIT = 9

DEAL_TAX = 17

DEAL_TYPE_BUY = 0
DEAL_TYPE_SELL = 1
DEAL_TYPE_BALANCE = 2
DEAL_TYPE_CREDIT = 3
DEAL_TYPE_CHARGE = 4
DEAL_TYPE_CORRECTION = 5
DEAL_TYPE_BONUS = 6
DEAL_TYPE_COMMISSION = 7
DEAL_TYPE_COMMISSION_DAILY = 8
DEAL_TYPE_COMMISSION_MONTHLY = 9
DEAL_TYPE_COMMISSION_AGENT_DAILY = 10
DEAL_TYPE_COMMISSION_AGENT_MONTHLY = 11
DEAL_TYPE_INTEREST = 12
DEAL_TYPE_BUY_CANCELED = 13
DEAL_TYPE_SELL_CANCELED = 14

ORDER_REASON_CLIENT = 0
ORDER_REASON_MOBILE = 1
ORDER_REASON_WEB = 2
ORDER_REASON_EXPERT = 3
ORDER_REASON_SL = 4
ORDER_REASON_TP = 5
ORDER_REASON_SO = 6

ORDER_STATE_STARTED = 0
ORDER_STATE_PLACED = 1
ORDER_STATE_CANCELED = 2
ORDER_STATE_PARTIAL = 3
ORDER_STATE_FILLED = 4
ORDER_STATE_REJECTED = 5
ORDER_STATE_EXPIRED = 6
ORDER_STATE_REQUEST_ADD = 7
ORDER_STATE_REQUEST_MODIFY = 8
ORDER_STATE_REQUEST_CANCEL = 9

POSITION_REASON_CLIENT = 0
POSITION_REASON_MOBILE = 1
POSITION_REASON_WEB = 2
POSITION_REASON_EXPERT = 3

POSITION_TYPE_BUY = 0
POSITION_TYPE_SELL = 1

RES_E_INTERNAL_FAIL_TIMEOUT = -10005
RES_E_INTERNAL_FAIL_CONNECT = -10004
RES_E_INTERNAL_FAIL_INIT = -10003
RES_E_INTERNAL_FAIL_RECEIVE = -10002
RES_E_INTERNAL_FAIL_SEND = -10001
RES_E_INTERNAL_FAIL = -10000
RES_E_AUTO_TRADING_DISABLED = -8
RES_E_UNSUPPORTED = -7
RES_E_AUTH_FAILED = -6
RES_E_INVALID_VERSION = -5
RES_E_NOT_FOUND = -4
RES_E_NO_MEMORY = -3
RES_E_FAIL = -1
RES_E_INVALID_PARAMS = -2
RES_S_OK = 1

SYMBOL_CALC_MODE_FOREX = 0
SYMBOL_CALC_MODE_FUTURES = 1
SYMBOL_CALC_MODE_CFD = 2
SYMBOL_CALC_MODE_CFDINDEX = 3
SYMBOL_CALC_MODE_CFDLEVERAGE = 4
SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE = 5
SYMBOL_CALC_MODE_EXCH_STOCKS = 32
SYMBOL_CALC_MODE_EXCH_FUTURES = 33
SYMBOL_CALC_MODE_EXCH_OPTIONS = 34
SYMBOL_CALC_MODE_EXCH_OPTIONS_MARGIN = 36
SYMBOL_CALC_MODE_EXCH_BONDS = 37
SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX = 38
SYMBOL_CALC_MODE_EXCH_BONDS_MOEX = 39
SYMBOL_CALC_MODE_SERV_COLLATERAL = 64

SYMBOL_CHART_MODE_BID = 0
SYMBOL_CHART_MODE_LAST = 1

SYMBOL_OPTION_MODE_EUROPEAN = 0
SYMBOL_OPTION_MODE_AMERICAN = 1

SYMBOL_OPTION_RIGHT_CALL = 0
SYMBOL_OPTION_RIGHT_PUT = 1

SYMBOL_ORDERS_GTC = 0
SYMBOL_ORDERS_DAILY = 1
SYMBOL_ORDERS_DAILY_NO_STOPS = 2

SYMBOL_SWAP_MODE_DISABLED = 0
SYMBOL_SWAP_MODE_POINTS = 1
SYMBOL_SWAP_MODE_CURRENCY_SYMBOL = 2
SYMBOL_SWAP_MODE_CURRENCY_MARGIN = 3
SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT = 4
SYMBOL_SWAP_MODE_INTEREST_CURRENT = 5
SYMBOL_SWAP_MODE_INTEREST_OPEN = 6
SYMBOL_SWAP_MODE_REOPEN_CURRENT = 7
SYMBOL_SWAP_MODE_REOPEN_BID = 8

SYMBOL_TRADE_EXECUTION_REQUEST = 0
SYMBOL_TRADE_EXECUTION_INSTANT = 1
SYMBOL_TRADE_EXECUTION_MARKET = 2
SYMBOL_TRADE_EXECUTION_EXCHANGE = 3

SYMBOL_TRADE_MODE_DISABLED = 0
SYMBOL_TRADE_MODE_LONGONLY = 1
SYMBOL_TRADE_MODE_SHORTONLY = 2
SYMBOL_TRADE_MODE_CLOSEONLY = 3
SYMBOL_TRADE_MODE_FULL = 4

TICK_FLAG_BID = 2
TICK_FLAG_ASK = 4
TICK_FLAG_LAST = 8
TICK_FLAG_VOLUME = 16
TICK_FLAG_BUY = 32
TICK_FLAG_SELL = 64

# TIMEFRAME
# 1 minute
TIMEFRAME_M1 = 1
# 2 minutes
TIMEFRAME_M2 = 2
# 3 minutes
TIMEFRAME_M3 = 3
# 4 minutes
TIMEFRAME_M4 = 4
# 5 minutes
TIMEFRAME_M5 = 5
# 6 minutes
TIMEFRAME_M6 = 6
# 10 minutes
TIMEFRAME_M10 = 10
# 12 minutes
TIMEFRAME_M12 = 12
# 15 minutes
TIMEFRAME_M15 = 15
# 20 minutes
TIMEFRAME_M20 = 20
# 30 minutes
TIMEFRAME_M30 = 30
# 1 hour
TIMEFRAME_H1 = 16385
# 2 hours
TIMEFRAME_H2 = 16386
# 3 hours
TIMEFRAME_H3 = 16387
# 4 hours
TIMEFRAME_H4 = 16388
# 6 hours
TIMEFRAME_H6 = 16390
# 8 hours
TIMEFRAME_H8 = 16392
# 12 hours
TIMEFRAME_H12 = 16396
# 1 day
TIMEFRAME_D1 = 16408
# 1 week
TIMEFRAME_W1 = 32769
# 1 month
TIMEFRAME_MN1 = 49153

# Requote
TRADE_RETCODE_REQUOTE = 10004
# Request rejected
TRADE_RETCODE_REJECT = 10006
# Request canceled by trader
TRADE_RETCODE_CANCEL = 10007
# Order placed
TRADE_RETCODE_PLACED = 10008
# Request completed
TRADE_RETCODE_DONE = 10009
# Only part of the request was completed
TRADE_RETCODE_DONE_PARTIAL = 10010
# Request processing error
TRADE_RETCODE_ERROR = 10011
# Request canceled by timeout
TRADE_RETCODE_TIMEOUT = 10012
# Invalid request
TRADE_RETCODE_INVALID = 10013
# Invalid volume in the request
TRADE_RETCODE_INVALID_VOLUME = 10014
# Invalid price in the request
TRADE_RETCODE_INVALID_PRICE = 10015
# Invalid stops in the request
TRADE_RETCODE_INVALID_STOPS = 10016
# Trade is disabled
TRADE_RETCODE_TRADE_DISABLED = 10017
# Market is closed
TRADE_RETCODE_MARKET_CLOSED = 10018
# There is not enough money to complete the request
TRADE_RETCODE_NO_MONEY = 10019
# Prices changed
TRADE_RETCODE_PRICE_CHANGED = 10020
# There are no quotes to process the request
TRADE_RETCODE_PRICE_OFF = 10021
# Invalid order expiration date in the request
TRADE_RETCODE_INVALID_EXPIRATION = 10022
# Order state changed
TRADE_RETCODE_ORDER_CHANGED = 10023
# Too frequent requests
TRADE_RETCODE_TOO_MANY_REQUESTS = 10024
# No changes in request
TRADE_RETCODE_NO_CHANGES = 10025
# Autotrading disabled by server
TRADE_RETCODE_SERVER_DISABLES_AT = 10026
# Autotrading disabled by client terminal
TRADE_RETCODE_CLIENT_DISABLES_AT = 10027
# Request locked for processing
TRADE_RETCODE_LOCKED = 10028
# Order or position frozen
TRADE_RETCODE_FROZEN = 10029
# Invalid order filling type
TRADE_RETCODE_INVALID_FILL = 10030
# No connection with the trade server
TRADE_RETCODE_CONNECTION = 10031
# Operation is allowed only for live accounts
TRADE_RETCODE_ONLY_REAL = 10032
# The number of pending orders has reached the limit
TRADE_RETCODE_LIMIT_ORDERS = 10033
# The volume of orders and positions for the symbol has reached the limit
TRADE_RETCODE_LIMIT_VOLUME = 10034
# Incorrect or prohibited order type
TRADE_RETCODE_INVALID_ORDER = 10035
# Position with the specified POSITION_IDENTIFIER has already been closed
TRADE_RETCODE_POSITION_CLOSED = 10036
# A close volume exceeds the current position volume
TRADE_RETCODE_INVALID_CLOSE_VOLUME = 10038
# A close order already exists for a specified position. This may happen when working in the hedging system:
# i) when attempting to close a position with an opposite one, while close orders for the position already exist;
# ii) when attempting to fully or partially close a position if the total volume of the already present close orders and the newly placed one exceeds the current position volume;
TRADE_RETCODE_CLOSE_ORDER_EXIST = 10039
# The number of open positions simultaneously present on an account can be limited by the server settings. After a limit is reached, the server returns the TRADE_RETCODE_LIMIT_POSITIONS error when attempting to place an order. The limitation operates differently depending on the position accounting type:
# Netting — number of open positions is considered. When a limit is reached, the platform does not let placing new orders whose execution may increase the number of open positions. In fact, the platform allows placing orders only for the symbols that already have open positions. The current pending orders are not considered since their execution may lead to changes in the current positions but it cannot increase their number.
# Hedging — pending orders are considered together with open positions, since a pending order activation always leads to opening a new position. When a limit is reached, the platform does not allow placing both new market orders for opening positions and pending orders.
TRADE_RETCODE_LIMIT_POSITIONS = 10040
# The pending order activation request is rejected, the order is canceled
TRADE_RETCODE_REJECT_CANCEL = 10041
# The request is rejected, because the "Only long positions are allowed" rule is set for the symbol (POSITION_TYPE_BUY)
TRADE_RETCODE_LONG_ONLY = 10042
# The request is rejected, because the "Only short positions are allowed" rule is set for the symbol (POSITION_TYPE_SELL)
TRADE_RETCODE_SHORT_ONLY = 10043
# The request is rejected, because the "Only position closing is allowed" rule is set for the symbol
TRADE_RETCODE_CLOSE_ONLY = 10044
# The request is rejected, because "Position closing is allowed only by FIFO rule" flag is set for the trading account (ACCOUNT_FIFO_CLOSE=true)
TRADE_RETCODE_FIFO_CLOSE = 10045
# The request is rejected, because the "Opposite positions on a single symbol are disabled" rule is set for the trading account. For example, if the account has a Buy position, then a user cannot open a Sell position or place a pending sell order. The rule is only applied to accounts with hedging accounting system (ACCOUNT_MARGIN_MODE=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING).
TRADE_RETCODE_HEDGE_PROHIBITED = 10046

# Sell order (Offer)
BOOK_TYPE_SELL = 1
# Buy order (Bid)
BOOK_TYPE_BUY = 2
# Sell order by Market
BOOK_TYPE_SELL_MARKET = 3
# Buy order by Market
BOOK_TYPE_BUY_MARKET = 4

# Market buy order
ORDER_TYPE_BUY = 0
# Market sell order
ORDER_TYPE_SELL = 1
# Buy Limit pending order
ORDER_TYPE_BUY_LIMIT = 2
# Sell Limit pending order
ORDER_TYPE_SELL_LIMIT = 3
# Buy Stop pending order
ORDER_TYPE_BUY_STOP = 4
# Sell Stop pending order
ORDER_TYPE_SELL_STOP = 5
# Upon reaching the order price, Buy Limit pending order is placed at StopLimit price
ORDER_TYPE_BUY_STOP_LIMIT = 6
# Upon reaching the order price, Sell Limit pending order is placed at StopLimit price
ORDER_TYPE_SELL_STOP_LIMIT = 7
# Order for closing a position by an opposite one
ORDER_TYPE_CLOSE_BY = 8

# Place an order for an instant deal with the specified parameters (set a market order)
TRADE_ACTION_DEAL = 1
# Place an order for performing a deal at specified conditions (pending order)
TRADE_ACTION_PENDING = 5
# Change open position Stop Loss and Take Profit
TRADE_ACTION_SLTP = 6
# Change parameters of the previously placed trading order
TRADE_ACTION_MODIFY = 7
# Remove previously placed pending order
TRADE_ACTION_REMOVE = 8
# Close a position by an opposite one
TRADE_ACTION_CLOSE_BY = 10

# This execution policy means that an order can be executed only in the specified volume. If the necessary amount of a financial instrument is currently unavailable in the market, the order will not be executed. The desired volume can be made up of several available offers.
ORDER_FILLING_FOK = 0
# An agreement to execute a deal at the maximum volume available in the market within the volume specified in the order. If the request cannot be filled completely, an order with the available volume will be executed, and the remaining volume will be canceled.
ORDER_FILLING_IOC = 1
# This policy is used only for market (ORDER_TYPE_BUY and ORDER_TYPE_SELL), limit and stop limit orders (ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT, ORDER_TYPE_BUY_STOP_LIMIT and ORDER_TYPE_SELL_STOP_LIMIT) and only for the symbols with Market or Exchange execution modes. If filled partially, a market or limit order with the remaining volume is not canceled, and is processed further. During activation of the ORDER_TYPE_BUY_STOP_LIMIT and ORDER_TYPE_SELL_STOP_LIMIT orders, an appropriate limit order ORDER_TYPE_BUY_LIMIT/ORDER_TYPE_SELL_LIMIT with the ORDER_FILLING_RETURN type is created.
ORDER_FILLING_RETURN = 2

# The order stays in the queue until it is manually canceled
ORDER_TIME_GTC = 0
# The order is active only during the current trading day
ORDER_TIME_DAY = 1
# The order is active until the specified date
ORDER_TIME_SPECIFIED = 2
# The order is active until 23:59:59 of the specified day. If this time appears to be out of a trading session, the expiration is processed at the nearest trading time.
ORDER_TIME_SPECIFIED_DAY = 3
