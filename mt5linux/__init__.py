import rpyc
from numpy import array

class MetaTrader5(object):
    ''' MetaTrader5'''
    
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


    def __init__(self,host='localhost',port=18812):
        '''
host: str
    default = localhost
port: int
    default = 18812
        '''
        self.__conn = rpyc.classic.connect(host,port)
        self.__conn.execute('import MetaTrader5 as mt5')

    def __del__(self):
        pass
            
    def initialize(self,*args,**kwargs):
        r'''
# initialize
        
Establish a connection with the MetaTrader 5 terminal. There are three call options.

Call without parameters. The terminal for connection is found automatically.

```python
initialize()
```

Call specifying the path to the MetaTrader 5 terminal we want to connect to.

```python
initialize(
   path                      # path to the MetaTrader 5 terminal EXE file
   )
```

Call specifying the trading account path and parameters.

```python
initialize(
   path,                     # path to the MetaTrader 5 terminal EXE file
   login=LOGIN,              # account number
   password="PASSWORD",      # password
   server="SERVER",          # server name as it is specified in the terminal
   timeout=TIMEOUT,          # timeout
   portable=False            # portable mode
   )
```

## Parameters

- path

    [in]  Path to the metatrader.exe or metatrader64.exe file. Optional unnamed parameter. It is indicated first without a parameter name. If the path is not specified, the module attempts to find the executable file on its own.

- login=LOGIN

    [in]  Trading account number. Optional named parameter. If not specified, the last trading account is used.

- password="PASSWORD"

    [in]  Trading account password. Optional named parameter. If the password is not set, the password for a specified trading account saved in the terminal database is applied automatically.

- server="SERVER"

    [in]  Trade server name. Optional named parameter. If the server is not set, the server for a specified trading account saved in the terminal database is applied automatically.

- timeout=TIMEOUT

    [in]  Connection timeout in milliseconds. Optional named parameter. If not specified, the value of 60 000 (60 seconds) is applied.

- portable=False

    [in]  Flag of the terminal launch in portable mode. Optional named parameter. If not specified, the value of False is used.

## Return Value

    Returns True in case of successful connection to the MetaTrader 5 terminal, otherwise - False.

## Note

    If required, the MetaTrader 5 terminal is launched to establish connection when executing the initialize() call.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)

# establish MetaTrader 5 connection to a specified trading account
if not mt5.initialize(login=25115284, server="MetaQuotes-Demo",password="4zatlbqx"):
    print("initialize() failed, error code =",mt5.last_error())
    quit()

# display data on connection status, server name and trading account
print(mt5.terminal_info())
# display data on MetaTrader 5 version
print(mt5.version())

# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## See also

    `shutdown`, `terminal_info`, `version`
        '''
        code=f'mt5.initialize(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def login(self,*args,**kwargs):
        r'''
# login

Connect to a trading account using specified parameters.

```python
login(
   login,                    # account number
   password="PASSWORD",      # password
   server="SERVER",          # server name as it is specified in the terminal
   timeout=TIMEOUT           # timeout
   )
```

## Parameters

- login

    [in]  Trading account number. Required unnamed parameter.

- password

    [in]  Trading account password. Optional named parameter. If the password is not set, the password saved in the terminal database is applied automatically.

- server

    [in]  Trade server name. Optional named parameter. If no server is set, the last used server is applied automatically.

- timeout=TIMEOUT

    [in]  Connection timeout in milliseconds. Optional named parameter. If not specified, the value of 60 000 (60 seconds) is applied. If the connection is not established within the specified time, the call is forcibly terminated and the exception is generated.

## Return Value

True in case of a successful connection to the trade account, otherwise – False.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# display data on MetaTrader 5 version
print(mt5.version())
# connect to the trade account without specifying a password and a server
account=17221085
authorized=mt5.login(account)  # the terminal database password is applied if connection data is set to be remembered
if authorized:
    print("connected to account #{}".format(account))
else:
    print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
 
# now connect to another trading account specifying the password
account=25115284
authorized=mt5.login(account, password="gqrtz0lbdm")
if authorized:
    # display trading account data 'as is'
    print(mt5.account_info())
    # display trading account data in the form of a list
    print("Show account_info()._asdict():")
    account_info_dict = mt5.account_info()._asdict()
    for prop in account_info_dict:
        print("  {}={}".format(prop, account_info_dict[prop]))
else:
    print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```
 
## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
[500, 2367, '23 Mar 2020']
 
connected to account #17221085
 
connected to account #25115284
AccountInfo(login=25115284, trade_mode=0, leverage=100, limit_orders=200, margin_so_mode=0, ...
account properties:
   login=25115284
   trade_mode=0
   leverage=100
   limit_orders=200
   margin_so_mode=0
   trade_allowed=True
   trade_expert=True
   margin_mode=2
   currency_digits=2
   fifo_close=False
   balance=99588.33
   credit=0.0
   profit=-45.23
   equity=99543.1
   margin=54.37
   margin_free=99488.73
   margin_level=183084.6054809638
   margin_so_call=50.0
   margin_so_so=30.0
   margin_initial=0.0
   margin_maintenance=0.0
   assets=0.0
   liabilities=0.0
   commission_blocked=0.0
   name=James Smith
   server=MetaQuotes-Demo
   currency=USD
   company=MetaQuotes Software Corp.
```

## See also

    `initialize`, `shutdown`
        '''
        code=f'mt5.login(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def shutdown(self,*args,**kwargs):
        r'''
# shutdown

Close the previously established connection to the MetaTrader 5 terminal.

```python
shutdown()
```

## Return Value

None.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed")
    quit()
 
# display data on connection status, server name and trading account
print(mt5.terminal_info())
# display data on MetaTrader 5 version
print(mt5.version())
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## See also

    `initialize`, `login_py`, `terminal_info`, `version`


        '''
        code=f'mt5.shutdown(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def version(self,*args,**kwargs):
        r'''
# version

Return the MetaTrader 5 terminal version.

```python
version()
```

## Return Value

Return the MetaTrader 5 terminal version, build and release date. Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The `version()` function returns the terminal version, build and release date as a tuple of three values:

| Type    | Description                   | Sample value  |
|---------|-------------------------------|---------------|
| integer | MetaTrader 5 terminal version | 500           |
| integer | Build                         | 2007          |
| string  | Build release date            | '25 Feb 2019' |

## Example:

```python
import MetaTrader5 as mt5
import pandas as pd
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# display data on MetaTrader 5 version
print(mt5.version())
 
# display data on connection status, server name and trading account 'as is'
print(mt5.terminal_info())
print()
 
# get properties in the form of a dictionary
terminal_info_dict=mt5.terminal_info()._asdict()
# convert the dictionary into DataFrame and print
df=pd.DataFrame(list(terminal_info_dict.items()),columns=['property','value'])
print("terminal_info() as dataframe:")
print(df[:-1])
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```
 
## Result:
```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
[500, 2367, '23 Mar 2020']
TerminalInfo(community_account=True, community_connection=True, connected=True, dlls_allowed=False, trade_allowed=False, ...
 
terminal_info() as dataframe:
                 property                         value
0       community_account                          True
1    community_connection                          True
2               connected                          True
3            dlls_allowed                         False
4           trade_allowed                         False
5       tradeapi_disabled                         False
6           email_enabled                         False
7             ftp_enabled                         False
8   notifications_enabled                         False
9                    mqid                         False
10                  build                          2367
11                maxbars                          5000
12               codepage                          1251
13              ping_last                         77881
14      community_balance                       707.107
15         retransmission                             0
16                company     MetaQuotes Software Corp.
17                   name                  MetaTrader 5
18               language                       Russian
19                   path  E:\ProgramFiles\MetaTrader 5
20              data_path  E:\ProgramFiles\MetaTrader 5
```

## See also

    `initialize`, `shutdown`, `terminal_info`
        '''
        code=f'mt5.version(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def last_error(self,*args,**kwargs):
        r'''
# last_error

Return data on the last error.

```python
last_error()
```

## Return Value

Return the last error code and description as a tuple.

## Note

`last_error()` allows obtaining an error code in case of a failed execution of a MetaTrader 5 library function. It is similar to `GetLastError()`. However, it applies its own error codes. Possible values:

| Constant                    | Value  | Description                      |
|-----------------------------|--------|----------------------------------|
| RES_S_OK                    | 1      | generic success                  |
| RES_E_FAIL                  | -1     | generic fail                     |
| RES_E_INVALID_PARAMS        | -2     | invalid arguments/parameters     |
| RES_E_NO_MEMORY             | -3     | no memory condition              |
| RES_E_NOT_FOUND             | -4     | no history                       |
| RES_E_INVALID_VERSION       | -5     | invalid version                  |
| RES_E_AUTH_FAILED           | -6     | authorization failed             |
| RES_E_UNSUPPORTED           | -7     | unsupported method               |
| RES_E_AUTO_TRADING_DISABLED | -8     | auto-trading disabled            |
| RES_E_INTERNAL_FAIL         | -10000 | internal IPC general error       |
| RES_E_INTERNAL_FAIL_SEND    | -10001 | internal IPC send failed         |
| RES_E_INTERNAL_FAIL_RECEIVE | -10002 | internal IPC recv failed         |
| RES_E_INTERNAL_FAIL_INIT    | -10003 | internal IPC initialization fail |
| RES_E_INTERNAL_FAIL_CONNECT | -10003 | internal IPC no ipc              |
| RES_E_INTERNAL_FAIL_TIMEOUT | -10005 | internal timeout                 |

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## See also

    `version`, `GetLastError`
        '''
        code=f'mt5.last_error(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def account_info(self,*args,**kwargs):
        r'''
# account_info

Get info on the current trading account.

```python
account_info()
```

## Return Value

Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The function returns all data that can be obtained using `AccountInfoInteger`, `AccountInfoDouble` and `AccountInfoString` in one call.

## Example:

```python
import MetaTrader5 as mt5
import pandas as pd
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# connect to the trade account specifying a password and a server
authorized=mt5.login(25115284, password="gqz0343lbdm")
if authorized:
    account_info=mt5.account_info()
    if account_info!=None:
        # display trading account data 'as is'
        print(account_info)
        # display trading account data in the form of a dictionary
        print("Show account_info()._asdict():")
        account_info_dict = mt5.account_info()._asdict()
        for prop in account_info_dict:
            print("  {}={}".format(prop, account_info_dict[prop]))
        print()
 
        # convert the dictionary into DataFrame and print
        df=pd.DataFrame(list(account_info_dict.items()),columns=['property','value'])
        print("account_info() as dataframe:")
        print(df)
else:
    print("failed to connect to trade account 25115284 with password=gqz0343lbdm, error code =",mt5.last_error())
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```
 
## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
AccountInfo(login=25115284, trade_mode=0, leverage=100, limit_orders=200, margin_so_mode=0, ....
Show account_info()._asdict():
  login=25115284
  trade_mode=0
  leverage=100
  limit_orders=200
  margin_so_mode=0
  trade_allowed=True
  trade_expert=True
  margin_mode=2
  currency_digits=2
  fifo_close=False
  balance=99511.4
  credit=0.0
  profit=41.82
  equity=99553.22
  margin=98.18
  margin_free=99455.04
  margin_level=101398.67590140559
  margin_so_call=50.0
  margin_so_so=30.0
  margin_initial=0.0
  margin_maintenance=0.0
  assets=0.0
  liabilities=0.0
  commission_blocked=0.0
  name=MetaQuotes Dev Demo
  server=MetaQuotes-Demo
  currency=USD
  company=MetaQuotes Software Corp.
 
account_info() as dataframe
              property                      value
0                login                   25115284
1           trade_mode                          0
2             leverage                        100
3         limit_orders                        200
4       margin_so_mode                          0
5        trade_allowed                       True
6         trade_expert                       True
7          margin_mode                          2
8      currency_digits                          2
9           fifo_close                      False
10             balance                    99588.3
11              credit                          0
12              profit                     -45.13
13              equity                    99543.2
14              margin                      54.37
15         margin_free                    99488.8
16        margin_level                     183085
17      margin_so_call                         50
18        margin_so_so                         30
19      margin_initial                          0
20  margin_maintenance                          0
21              assets                          0
22         liabilities                          0
23  commission_blocked                          0
24                name                James Smith
25              server            MetaQuotes-Demo
26            currency                        USD
27             company  MetaQuotes Software Corp.
```

## See also

    `initialize`, `shutdown`, `login`


        '''
        code=f'mt5.account_info(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def terminal_info(self,*args,**kwargs):
        r'''
# terminal_info

Get the connected MetaTrader 5 client terminal status and settings.

```python
terminal_info()
```

## Return Value

Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using last_error().

## Note

The function returns all data that can be obtained using `TerminalInfoInteger`, `TerminalInfoDouble` and `TerminalInfoDouble` in one call.

## Example:

```python
import MetaTrader5 as mt5
import pandas as pd
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# display data on MetaTrader 5 version
print(mt5.version())
# display info on the terminal settings and status
terminal_info=mt5.terminal_info()
if terminal_info!=None:
    # display the terminal data 'as is'
    print(terminal_info)
    # display data in the form of a list
    print("Show terminal_info()._asdict():")
    terminal_info_dict = mt5.terminal_info()._asdict()
    for prop in terminal_info_dict:
        print("  {}={}".format(prop, terminal_info_dict[prop]))
    print()
   # convert the dictionary into DataFrame and print
    df=pd.DataFrame(list(terminal_info_dict.items()),columns=['property','value'])
    print("terminal_info() as dataframe:")
    print(df)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
[500, 2366, '20 Mar 2020']
TerminalInfo(community_account=True, community_connection=True, connected=True,....
Show terminal_info()._asdict():
  community_account=True
  community_connection=True
  connected=True
  dlls_allowed=False
  trade_allowed=False
  tradeapi_disabled=False
  email_enabled=False
  ftp_enabled=False
  notifications_enabled=False
  mqid=False
  build=2366
  maxbars=5000
  codepage=1251
  ping_last=77850
  community_balance=707.10668201585
  retransmission=0.0
  company=MetaQuotes Software Corp.
  name=MetaTrader 5
  language=Russian
  path=E:\ProgramFiles\MetaTrader 5
  data_path=E:\ProgramFiles\MetaTrader 5
  commondata_path=C:\Users\Rosh\AppData\Roaming\MetaQuotes\Terminal\Common
 
terminal_info() as dataframe:
                 property                      value
0       community_account                       True
1    community_connection                       True
2               connected                       True
3            dlls_allowed                      False
4           trade_allowed                      False
5       tradeapi_disabled                      False
6           email_enabled                      False
7             ftp_enabled                      False
8   notifications_enabled                      False
9                    mqid                      False
10                  build                       2367
11                maxbars                       5000
12               codepage                       1251
13              ping_last                      80953
14      community_balance                    707.107
15         retransmission                   0.063593
16                company  MetaQuotes Software Corp.
17                   name               MetaTrader 5
18               language                    Russian
```

## See also

    `initialize`, `shutdown`, `version`


        '''
        code=f'mt5.terminal_info(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def symbols_total(self,*args,**kwargs):
        r'''
# symbols_total

Get the number of all financial instruments in the MetaTrader 5 terminal.

```python
symbols_total()
```

## Return Value

Integer value.

## Note

The function is similar to `SymbolsTotal()`. However, it returns the number of all symbols including custom ones and the ones disabled in MarketWatch.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get the number of financial instruments
symbols=mt5.symbols_total()
if symbols>0:
    print("Total symbols =",symbols)
else:
    print("symbols not found")
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## See also

    `symbols_get`, `symbol_select`, `symbol_info`


        '''
        code=f'mt5.symbols_total(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def symbols_get(self,*args,**kwargs):
        r'''
# symbols_get

Get all financial instruments from the MetaTrader 5 terminal.

```python
symbols_get(
   group="GROUP"      # symbol selection filter 
)
```

- group="GROUP"

    [in]  The filter for arranging a group of necessary symbols. Optional parameter. If the group is specified, the function returns only symbols meeting a specified criteria.

## Return Value

Return symbols in the form of a tuple. Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The group parameter allows sorting out symbols by name. '*' can be used at the beginning and the end of a string.

The group parameter can be used as a named or an unnamed one. Both options work the same way. The named option (group="GROUP") makes the code easier to read.

The group parameter may contain several comma separated conditions. A condition can be set as a mask using '*'. The logical negation symbol '!' can be used for an exclusion. All conditions are applied sequentially, which means conditions of including to a group should be specified first followed by an exclusion condition. For example, group="*, !EUR" means that all symbols should be selected first and the ones containing "EUR" in their names should be excluded afterwards.

Unlike `symbol_info()`, the `symbols_get()` function returns data on all requested symbols within a single call.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get all symbols
symbols=mt5.symbols_get()
print('Symbols: ', len(symbols))
count=0
# display the first five ones
for s in symbols:
    count+=1
    print("{}. {}".format(count,s.name))
    if count==5: break
print()
 
# get symbols containing RU in their names
ru_symbols=mt5.symbols_get("*RU*")
print('len(*RU*): ', len(ru_symbols))
for s in ru_symbols:
    print(s.name)
print()
 
# get symbols whose names do not contain USD, EUR, JPY and GBP
group_symbols=mt5.symbols_get(group="*,!*USD*,!*EUR*,!*JPY*,!*GBP*")
print('len(*,!*USD*,!*EUR*,!*JPY*,!*GBP*):', len(group_symbols))
for s in group_symbols:
    print(s.name,":",s)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
Symbols:  84
1. EURUSD
2. GBPUSD
3. USDCHF
4. USDJPY
5. USDCNH
 
len(*RU*):  8
EURUSD
USDRUB
USDRUR
EURRUR
EURRUB
FORTS.RUB.M5
EURUSD_T20
EURUSD4
 
len(*,!*USD*,!*EUR*,!*JPY*,!*GBP*):  13
AUDCAD : SymbolInfo(custom=False, chart_mode=0, select=True, visible=True, session_deals=0, session_buy_orders=0, session...
AUDCHF : SymbolInfo(custom=False, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, sessi...
AUDNZD : SymbolInfo(custom=False, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, sessi...
CADCHF : SymbolInfo(custom=False, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, sessi...
NZDCAD : SymbolInfo(custom=False, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, sessi...
NZDCHF : SymbolInfo(custom=False, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, sessi...
NZDSGD : SymbolInfo(custom=False, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, sessi...
CADMXN : SymbolInfo(custom=False, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, sessi...
CHFMXN : SymbolInfo(custom=False, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, sessi...
NZDMXN : SymbolInfo(custom=False, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, sessi...
FORTS.RTS.M5 : SymbolInfo(custom=True, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, ...
FORTS.RUB.M5 : SymbolInfo(custom=True, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, ...
FOREX.CHF.M5 : SymbolInfo(custom=True, chart_mode=0, select=False, visible=False, session_deals=0, session_buy_orders=0, ...
```

## See also

    `symbols_total`, `symbol_select`, `symbol_info`


        '''
        code=f'mt5.symbols_get(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def symbol_info(self,*args,**kwargs):
        r'''
# symbol_info

Get data on the specified financial instrument.

```python
symbol_info(
   symbol      # financial instrument name
)
```

- symbol

    [in]  Financial instrument name. Required unnamed parameter.

## Return Value

Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The function returns all data that can be obtained using `SymbolInfoInteger`, `SymbolInfoDouble` and `SymbolInfoString` in one call.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# attempt to enable the display of the EURJPY symbol in MarketWatch
selected=mt5.symbol_select("EURJPY",True)
if not selected:
    print("Failed to select EURJPY")
    mt5.shutdown()
    quit()
 
# display EURJPY symbol properties
symbol_info=mt5.symbol_info("EURJPY")
if symbol_info!=None:
    # display the terminal data 'as is'    
    print(symbol_info)
    print("EURJPY: spread =",symbol_info.spread,"  digits =",symbol_info.digits)
    # display symbol properties as a list
    print("Show symbol_info(\"EURJPY\")._asdict():")
    symbol_info_dict = mt5.symbol_info("EURJPY")._asdict()
    for prop in symbol_info_dict:
        print("  {}={}".format(prop, symbol_info_dict[prop]))
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
SymbolInfo(custom=False, chart_mode=0, select=True, visible=True, session_deals=0, session_buy_orders=0, session_sell_orders=0, ...
EURJPY: spread = 17   digits = 3
Show symbol_info()._asdict():
  custom=False
  chart_mode=0
  select=True
  visible=True
  session_deals=0
  session_buy_orders=0
  session_sell_orders=0
  volume=0
  volumehigh=0
  volumelow=0
  time=1585069682
  digits=3
  spread=17
  spread_float=True
  ticks_bookdepth=10
  trade_calc_mode=0
  trade_mode=4
  start_time=0
  expiration_time=0
  trade_stops_level=0
  trade_freeze_level=0
  trade_exemode=1
  swap_mode=1
  swap_rollover3days=3
  margin_hedged_use_leg=False
  expiration_mode=7
  filling_mode=1
  order_mode=127
  order_gtc_mode=0
  option_mode=0
  option_right=0
  bid=120.024
  bidhigh=120.506
  bidlow=118.798
  ask=120.041
  askhigh=120.526
  asklow=118.828
  last=0.0
  lasthigh=0.0
  lastlow=0.0
  volume_real=0.0
  volumehigh_real=0.0
  volumelow_real=0.0
  option_strike=0.0
  point=0.001
  trade_tick_value=0.8977708350166538
  trade_tick_value_profit=0.8977708350166538
  trade_tick_value_loss=0.8978272580355541
  trade_tick_size=0.001
  trade_contract_size=100000.0
  trade_accrued_interest=0.0
  trade_face_value=0.0
  trade_liquidity_rate=0.0
  volume_min=0.01
  volume_max=500.0
  volume_step=0.01
  volume_limit=0.0
  swap_long=-0.2
  swap_short=-1.2
  margin_initial=0.0
  margin_maintenance=0.0
  session_volume=0.0
  session_turnover=0.0
  session_interest=0.0
  session_buy_orders_volume=0.0
  session_sell_orders_volume=0.0
  session_open=0.0
  session_close=0.0
  session_aw=0.0
  session_price_settlement=0.0
  session_price_limit_min=0.0
  session_price_limit_max=0.0
  margin_hedged=100000.0
  price_change=0.0
  price_volatility=0.0
  price_theoretical=0.0
  price_greeks_delta=0.0
  price_greeks_theta=0.0
  price_greeks_gamma=0.0
  price_greeks_vega=0.0
  price_greeks_rho=0.0
  price_greeks_omega=0.0
  price_sensitivity=0.0
  basis=
  category=
  currency_base=EUR
  currency_profit=JPY
  currency_margin=EUR
  bank=
  description=Euro vs Japanese Yen
  exchange=
  formula=
  isin=
  name=EURJPY
  page=http://www.google.com/finance?q=EURJPY
  path=Forex\EURJPY
```

## See also

    `account_info`, `terminal_info`


        '''
        code=f'mt5.symbol_info(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def symbol_info_tick(self,*args,**kwargs):
        r'''
# symbol_info_tick

Get the last tick for the specified financial instrument.

```python
symbol_info_tick(
   symbol      # financial instrument name
)
```

- symbol

    [in]  Financial instrument name. Required unnamed parameter.

## Return Value

Return info in the form of a tuple. Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The function is similar to SymbolInfoTick.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# attempt to enable the display of the GBPUSD in MarketWatch
selected=mt5.symbol_select("GBPUSD",True)
if not selected:
    print("Failed to select GBPUSD")
    mt5.shutdown()
    quit()
 
# display the last GBPUSD tick
lasttick=mt5.symbol_info_tick("GBPUSD")
print(lasttick)
# display tick field values in the form of a list
print("Show symbol_info_tick(\"GBPUSD\")._asdict():")
symbol_info_tick_dict = mt5.symbol_info_tick("GBPUSD")._asdict()
for prop in symbol_info_tick_dict:
    print("  {}={}".format(prop, symbol_info_tick_dict[prop]))
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
Tick(time=1585070338, bid=1.17264, ask=1.17279, last=0.0, volume=0, time_msc=1585070338728, flags=2, volume_real=0.0)
Show symbol_info_tick._asdict():
  time=1585070338
  bid=1.17264
  ask=1.17279
  last=0.0
  volume=0
  time_msc=1585070338728
  flags=2
  volume_real=0.0
```

## See also

    ``symbol_info`
        '''
        code=f'mt5.symbol_info_tick(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def symbol_select(self,*args,**kwargs):
        r'''
# symbol_select

Select a symbol in the MarketWatch window or remove a symbol from the window.

```python
symbol_select(
   symbol,      # financial instrument name
   enable       # enable or disable
)
```

- symbol

    [in]  Financial instrument name. Required unnamed parameter.

- enable

    [in]  Switch. Optional unnamed parameter. If 'false', a symbol should be removed from the MarketWatch window. Otherwise, it should be selected in the MarketWatch window. A symbol cannot be removed if open charts with this symbol are currently present or positions are opened on it.

## Return Value

`True` if successful, otherwise – `False`.

## Note

The function is similar to `SymbolSelect`.

## Example:

```python
import MetaTrader5 as mt5
import pandas as pd
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
print()
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize(login=25115284, server="MetaQuotes-Demo",password="4zatlbqx"):
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# attempt to enable the display of the EURCAD in MarketWatch
selected=mt5.symbol_select("EURCAD",True)
if not selected:
    print("Failed to select EURCAD, error code =",mt5.last_error())
else:
    symbol_info=mt5.symbol_info("EURCAD")
    print(symbol_info)
    print("EURCAD: currency_base =",symbol_info.currency_base,"  currency_profit =",symbol_info.currency_profit,"  currency_margin =",symbol_info.currency_margin)
    print()
 
    # get symbol properties in the form of a dictionary
    print("Show symbol_info()._asdict():")
    symbol_info_dict = symbol_info._asdict()
    for prop in symbol_info_dict:
        print("  {}={}".format(prop, symbol_info_dict[prop]))
    print()
 
    # convert the dictionary into DataFrame and print
    df=pd.DataFrame(list(symbol_info_dict.items()),columns=['property','value'])
    print("symbol_info_dict() as dataframe:")
    print(df)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
SymbolInfo(custom=False, chart_mode=0, select=True, visible=True, session_deals=0, session_buy_orders=0, session_sell_orders=0, volume=0, volumehigh=0, ....
EURCAD: currency_base = EUR   currency_profit = CAD   currency_margin = EUR
 
Show symbol_info()._asdict():
  custom=False
  chart_mode=0
  select=True
  visible=True
  session_deals=0
  session_buy_orders=0
  session_sell_orders=0
  volume=0
  volumehigh=0
  volumelow=0
  time=1585217595
  digits=5
  spread=39
  spread_float=True
  ticks_bookdepth=10
  trade_calc_mode=0
  trade_mode=4
  start_time=0
  expiration_time=0
  trade_stops_level=0
  trade_freeze_level=0
  trade_exemode=1
  swap_mode=1
  swap_rollover3days=3
  margin_hedged_use_leg=False
  expiration_mode=7
  filling_mode=1
  order_mode=127
  order_gtc_mode=0
  option_mode=0
  option_right=0
  bid=1.55192
  bidhigh=1.55842
  bidlow=1.5419800000000001
  ask=1.5523099999999999
  askhigh=1.55915
  asklow=1.5436299999999998
  last=0.0
  lasthigh=0.0
  lastlow=0.0
  volume_real=0.0
  volumehigh_real=0.0
  volumelow_real=0.0
  option_strike=0.0
  point=1e-05
  trade_tick_value=0.7043642408362214
  trade_tick_value_profit=0.7043642408362214
  trade_tick_value_loss=0.7044535553770941
  trade_tick_size=1e-05
  trade_contract_size=100000.0
  trade_accrued_interest=0.0
  trade_face_value=0.0
  trade_liquidity_rate=0.0
  volume_min=0.01
  volume_max=500.0
  volume_step=0.01
  volume_limit=0.0
  swap_long=-1.1
  swap_short=-0.9
  margin_initial=0.0
  margin_maintenance=0.0
  session_volume=0.0
  session_turnover=0.0
  session_interest=0.0
  session_buy_orders_volume=0.0
  session_sell_orders_volume=0.0
  session_open=0.0
  session_close=0.0
  session_aw=0.0
  session_price_settlement=0.0
  session_price_limit_min=0.0
  session_price_limit_max=0.0
  margin_hedged=100000.0
  price_change=0.0
  price_volatility=0.0
  price_theoretical=0.0
  price_greeks_delta=0.0
  price_greeks_theta=0.0
  price_greeks_gamma=0.0
  price_greeks_vega=0.0
  price_greeks_rho=0.0
  price_greeks_omega=0.0
  price_sensitivity=0.0
  basis=
  category=
  currency_base=EUR
  currency_profit=CAD
  currency_margin=EUR
  bank=
  description=Euro vs Canadian Dollar
  exchange=
  formula=
  isin=
  name=EURCAD
  page=http://www.google.com/finance?q=EURCAD
  path=Forex\EURCAD
 
symbol_info_dict() as dataframe:
         property                                   value
0          custom                                   False
1      chart_mode                                       0
2          select                                    True
3         visible                                    True
4   session_deals                                       0
..            ...                                     ...
91        formula                                        
92           isin                                        
93           name                                  EURCAD
94           page  http://www.google.com/finance?q=EURCAD
95           path                            Forex\EURCAD
 
[96 rows x 2 columns]
```

## See also

    `symbol_info`
        '''
        code=f'mt5.symbol_select(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def market_book_add(self,*args,**kwargs):
        r'''
# market_book_add

Subscribes the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.

```python
market_book_add(
   symbol      # financial instrument name
)
```

- symbol

    [in]  Financial instrument name. Required unnamed parameter.

## Return Value

`True` if successful, otherwise – `False`.

## Note

The function is similar to `MarketBookAdd`.

## See also

    `market_book_get`, `market_book_release`, Market Depth structure


        '''
        code=f'mt5.market_book_add(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def market_book_get(self,*args,**kwargs):
        r'''
# market_book_get

Returns a tuple from `BookInfo` featuring Market Depth entries for the specified symbol.

```python
market_book_get(
   symbol      # financial instrument name
)
```

- symbol

    [in]  Financial instrument name. Required unnamed parameter.

## Return Value

Returns the Market Depth content as a tuple from `BookInfo` entries featuring order type, price and volume in lots. `BookInfo` is similar to the `MqlBookInfo` structure.

Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The subscription to the Market Depth change events should be preliminarily performed using the `market_book_add()` function.

The function is similar to `MarketBookGet`.

## Example:

```python
import MetaTrader5 as mt5
import time
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
print("")
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
   # shut down connection to the MetaTrader 5 terminal
    mt5.shutdown()
    quit()
 
# subscribe to market depth updates for EURUSD (Depth of Market)
if mt5.market_book_add('EURUSD'):
  # get the market depth data 10 times in a loop
   for i in range(10):
        # get the market depth content (Depth of Market)
        items = mt5.market_book_get('EURUSD')
        # display the entire market depth 'as is' in a single string
        print(items)
        # now display each order separately for more clarity
        if items:
            for it in items:
                # order content
                print(it._asdict())
        # pause for 5 seconds before the next request of the market depth data
        time.sleep(5)
  # cancel the subscription to the market depth updates (Depth of Market)
   mt5.market_book_release('EURUSD')
else:
    print("mt5.market_book_add('EURUSD') failed, error code =",mt5.last_error())
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.34
 
(BookInfo(type=1, price=1.20038, volume=250, volume_dbl=250.0), BookInfo(type=1, price=1.20032, volume=100, volume...
{'type': 1, 'price': 1.20038, 'volume': 250, 'volume_dbl': 250.0}
{'type': 1, 'price': 1.20032, 'volume': 100, 'volume_dbl': 100.0}
{'type': 1, 'price': 1.2003, 'volume': 50, 'volume_dbl': 50.0}
{'type': 1, 'price': 1.20028, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20026, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20025, 'volume': 50, 'volume_dbl': 50.0}
{'type': 2, 'price': 1.20023, 'volume': 100, 'volume_dbl': 100.0}
{'type': 2, 'price': 1.20017, 'volume': 250, 'volume_dbl': 250.0}
(BookInfo(type=1, price=1.2004299999999999, volume=250, volume_dbl=250.0), BookInfo(type=1, price=1.20037, volume...
{'type': 1, 'price': 1.2004299999999999, 'volume': 250, 'volume_dbl': 250.0}
{'type': 1, 'price': 1.20037, 'volume': 100, 'volume_dbl': 100.0}
{'type': 1, 'price': 1.20036, 'volume': 50, 'volume_dbl': 50.0}
{'type': 1, 'price': 1.20034, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20031, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20029, 'volume': 50, 'volume_dbl': 50.0}
{'type': 2, 'price': 1.20028, 'volume': 100, 'volume_dbl': 100.0}
{'type': 2, 'price': 1.20022, 'volume': 250, 'volume_dbl': 250.0}
(BookInfo(type=1, price=1.2004299999999999, volume=250, volume_dbl=250.0), BookInfo(type=1, price=1.20037, volume...
{'type': 1, 'price': 1.2004299999999999, 'volume': 250, 'volume_dbl': 250.0}
{'type': 1, 'price': 1.20037, 'volume': 100, 'volume_dbl': 100.0}
{'type': 1, 'price': 1.20036, 'volume': 50, 'volume_dbl': 50.0}
{'type': 1, 'price': 1.20034, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20031, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20029, 'volume': 50, 'volume_dbl': 50.0}
{'type': 2, 'price': 1.20028, 'volume': 100, 'volume_dbl': 100.0}
{'type': 2, 'price': 1.20022, 'volume': 250, 'volume_dbl': 250.0}
(BookInfo(type=1, price=1.20036, volume=250, volume_dbl=250.0), BookInfo(type=1, price=1.20029, volume=100, volume...
{'type': 1, 'price': 1.20036, 'volume': 250, 'volume_dbl': 250.0}
{'type': 1, 'price': 1.20029, 'volume': 100, 'volume_dbl': 100.0}
{'type': 1, 'price': 1.20028, 'volume': 50, 'volume_dbl': 50.0}
{'type': 1, 'price': 1.20026, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20023, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20022, 'volume': 50, 'volume_dbl': 50.0}
{'type': 2, 'price': 1.20021, 'volume': 100, 'volume_dbl': 100.0}
{'type': 2, 'price': 1.20014, 'volume': 250, 'volume_dbl': 250.0}
(BookInfo(type=1, price=1.20035, volume=250, volume_dbl=250.0), BookInfo(type=1, price=1.20029, volume=100, volume...
{'type': 1, 'price': 1.20035, 'volume': 250, 'volume_dbl': 250.0}
{'type': 1, 'price': 1.20029, 'volume': 100, 'volume_dbl': 100.0}
{'type': 1, 'price': 1.20027, 'volume': 50, 'volume_dbl': 50.0}
{'type': 1, 'price': 1.20025, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20023, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20022, 'volume': 50, 'volume_dbl': 50.0}
{'type': 2, 'price': 1.20021, 'volume': 100, 'volume_dbl': 100.0}
{'type': 2, 'price': 1.20014, 'volume': 250, 'volume_dbl': 250.0}
(BookInfo(type=1, price=1.20037, volume=250, volume_dbl=250.0), BookInfo(type=1, price=1.20031, volume=100, volume...
{'type': 1, 'price': 1.20037, 'volume': 250, 'volume_dbl': 250.0}
{'type': 1, 'price': 1.20031, 'volume': 100, 'volume_dbl': 100.0}
{'type': 1, 'price': 1.2003, 'volume': 50, 'volume_dbl': 50.0}
{'type': 1, 'price': 1.20028, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20025, 'volume': 36, 'volume_dbl': 36.0}
{'type': 2, 'price': 1.20023, 'volume': 50, 'volume_dbl': 50.0}
{'type': 2, 'price': 1.20022, 'volume': 100, 'volume_dbl': 100.0}
{'type': 2, 'price': 1.20016, 'volume': 250, 'volume_dbl': 250.0}
```

## See also

    `market_book_add`, `market_book_release`, Market Depth structure


        '''
        code=f'mt5.market_book_get(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def market_book_release(self,symbol):
        r'''
# market_book_release

Cancels subscription of the MetaTrader 5 terminal to the Market Depth change events for a specified symbol.

```python
market_book_release(
   symbol      # financial instrument name
)
```

- symbol

    [in]  Financial instrument name. Required unnamed parameter.

## Return Value

`True` if successful, otherwise – `False`.

## Note

The function is similar to `MarketBookRelease`.

## See also

    `market_book_add`, `market_book_get`, Market Depth structure


        '''
        code=f'mt5.market_book_release(symbol)'
        return self.__conn.eval(code)

    def copy_rates_from(self,symbol, timeframe, date_from, count):
        r'''
# copy_rates_from

Get bars from the MetaTrader 5 terminal starting from the specified date.

```python
copy_rates_from(
   symbol,       # symbol name
   timeframe,    # timeframe
   date_from,    # initial bar open date
   count         # number of bars
   )
```

## Parameters

- symbol

    [in]  Financial instrument name, for example, "EURUSD". Required unnamed parameter.

- timeframe

    [in]  Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration. Required unnamed parameter.

- date_from

    [in]  Date of opening of the first bar from the requested sample. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.

- count

    [in]  Number of bars to receive. Required unnamed parameter.

## Return Value

Returns bars as the numpy array with the named time, open, high, low, close, tick_volume, spread and real_volume columns. Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

See the `CopyRates()` function for more information.

MetaTrader 5 terminal provides bars only within a history available to a user on charts. The number of bars available to users is set in the "Max. bars in chart" parameter.

When creating the 'datetime' object, Python uses the local time zone, while MetaTrader 5 stores tick and bar open time in UTC time zone (without the shift). Therefore, 'datetime' should be created in UTC time for executing functions that use time. Data received from the MetaTrader 5 terminal has UTC time.  

TIMEFRAME is an enumeration with possible chart period values

| ID            | Description |
|---------------|-------------|
| TIMEFRAME_M1  | 1 minute    |
| TIMEFRAME_M2  | 2 minutes   |
| TIMEFRAME_M3  | 3 minutes   |
| TIMEFRAME_M4  | 4 minutes   |
| TIMEFRAME_M5  | 5 minutes   |
| TIMEFRAME_M6  | 6 minutes   |
| TIMEFRAME_M10 | 10 minutes  |
| TIMEFRAME_M12 | 12 minutes  |
| TIMEFRAME_M12 | 15 minutes  |
| TIMEFRAME_M20 | 20 minutes  |
| TIMEFRAME_M30 | 30 minutes  |
| TIMEFRAME_H1  | 1 hour      |
| TIMEFRAME_H2  | 2 hours     |
| TIMEFRAME_H3  | 3 hours     |
| TIMEFRAME_H4  | 4 hours     |
| TIMEFRAME_H6  | 6 hours     |
| TIMEFRAME_H8  | 8 hours     |
| TIMEFRAME_H12 | 12 hours    |
| TIMEFRAME_D1  | 1 day       |
| TIMEFRAME_W1  | 1 week      |
| TIMEFRAME_MN1 | 1 month     |


## Example:

```python
from datetime import datetime
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# import the 'pandas' module for displaying data obtained in the tabular form
import pandas as pd
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# import pytz module for working with time zone
import pytz
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2020, 1, 10, tzinfo=timezone)
# get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_H4, utc_from, 10)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
# display each element of obtained data in a new line
print("Display obtained data 'as is'")
for rate in rates:
    print(rate)
 
# create DataFrame out of the obtained data
rates_frame = pd.DataFrame(rates)
# convert time in seconds into the datetime format
rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
                           
# display data
print("\nDisplay dataframe with data")
print(rates_frame)  
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
Display obtained data 'as is'
(1578484800, 1.11382, 1.11385, 1.1111, 1.11199, 9354, 1, 0)
(1578499200, 1.11199, 1.11308, 1.11086, 1.11179, 10641, 1, 0)
(1578513600, 1.11178, 1.11178, 1.11016, 1.11053, 4806, 1, 0)
(1578528000, 1.11053, 1.11193, 1.11033, 1.11173, 3480, 1, 0)
(1578542400, 1.11173, 1.11189, 1.11126, 1.11182, 2236, 1, 0)
(1578556800, 1.11181, 1.11203, 1.10983, 1.10993, 7984, 1, 0)
(1578571200, 1.10994, 1.11173, 1.10965, 1.11148, 7406, 1, 0)
(1578585600, 1.11149, 1.11149, 1.10923, 1.11046, 7468, 1, 0)
(1578600000, 1.11046, 1.11097, 1.11033, 1.11051, 3450, 1, 0)
(1578614400, 1.11051, 1.11093, 1.11017, 1.11041, 2448, 1, 0)
 
Display dataframe with data
                 time     open     high      low    close  tick_volume  spread  real_volume
0 2020-01-08 12:00:00  1.11382  1.11385  1.11110  1.11199         9354       1            0
1 2020-01-08 16:00:00  1.11199  1.11308  1.11086  1.11179        10641       1            0
2 2020-01-08 20:00:00  1.11178  1.11178  1.11016  1.11053         4806       1            0
3 2020-01-09 00:00:00  1.11053  1.11193  1.11033  1.11173         3480       1            0
4 2020-01-09 04:00:00  1.11173  1.11189  1.11126  1.11182         2236       1            0
5 2020-01-09 08:00:00  1.11181  1.11203  1.10983  1.10993         7984       1            0
6 2020-01-09 12:00:00  1.10994  1.11173  1.10965  1.11148         7406       1            0
7 2020-01-09 16:00:00  1.11149  1.11149  1.10923  1.11046         7468       1            0
8 2020-01-09 20:00:00  1.11046  1.11097  1.11033  1.11051         3450       1            0
9 2020-01-10 00:00:00  1.11051  1.11093  1.11017  1.11041         2448       1            0
```

## See also

    `CopyRates`, `copy_rates_from_pos`, `copy_rates_range`, `copy_ticks_from`, `copy_ticks_range`


        '''
        code=f'mt5.copy_rates_from("{symbol}", {timeframe}, {repr(date_from.astimezone())}, {count})'
        return rpyc.classic.obtain(self.__conn.eval(code))

    def copy_rates_from_pos(self,symbol,timeframe,start_pos,count):
        r'''
# copy_rates_from_pos

Get bars from the MetaTrader 5 terminal starting from the specified index.

```python
copy_rates_from_pos(
   symbol,       # symbol name
   timeframe,    # timeframe
   start_pos,    # initial bar index
   count         # number of bars
   )
```

## Parameters

- symbol

    [in]  Financial instrument name, for example, "EURUSD". Required unnamed parameter.

- timeframe

    [in]  Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration. Required unnamed parameter.

- start_pos

    [in]  Initial index of the bar the data are requested from. The numbering of bars goes from present to past. Thus, the zero bar means the current one. Required unnamed parameter.

- count

    [in]  Number of bars to receive. Required unnamed parameter.

## Return Value

Returns bars as the numpy array with the named time, open, high, low, close, tick_volume, spread and real_volume columns. Returns None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

See the `CopyRates()` function for more information.

MetaTrader 5 terminal provides bars only within a history available to a user on charts. The number of bars available to users is set in the "Max. bars in chart" parameter.

## Example:

```python
from datetime import datetime
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# import the 'pandas' module for displaying data obtained in the tabular form
import pandas as pd
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get 10 GBPUSD D1 bars from the current day
rates = mt5.copy_rates_from_pos("GBPUSD", mt5.TIMEFRAME_D1, 0, 10)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
# display each element of obtained data in a new line
print("Display obtained data 'as is'")
for rate in rates:
    print(rate)
 
# create DataFrame out of the obtained data
rates_frame = pd.DataFrame(rates)
# convert time in seconds into the datetime format
rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
 
# display data
print("\nDisplay dataframe with data")
print(rates_frame) 
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
Display obtained data 'as is'
(1581552000, 1.29568, 1.30692, 1.29441, 1.30412, 68228, 0, 0)
(1581638400, 1.30385, 1.30631, 1.3001, 1.30471, 56498, 0, 0)
(1581897600, 1.30324, 1.30536, 1.29975, 1.30039, 49400, 0, 0)
(1581984000, 1.30039, 1.30486, 1.29705, 1.29952, 62288, 0, 0)
(1582070400, 1.29952, 1.3023, 1.29075, 1.29187, 57909, 0, 0)
(1582156800, 1.29186, 1.29281, 1.28489, 1.28792, 61033, 0, 0)
(1582243200, 1.28802, 1.29805, 1.28746, 1.29566, 66386, 0, 0)
(1582502400, 1.29426, 1.29547, 1.28865, 1.29283, 66933, 0, 0)
(1582588800, 1.2929, 1.30178, 1.29142, 1.30037, 80121, 0, 0)
(1582675200, 1.30036, 1.30078, 1.29136, 1.29374, 49286, 0, 0)
 
Display dataframe with data
        time     open     high      low    close  tick_volume  spread  real_volume
0 2020-02-13  1.29568  1.30692  1.29441  1.30412        68228       0            0
1 2020-02-14  1.30385  1.30631  1.30010  1.30471        56498       0            0
2 2020-02-17  1.30324  1.30536  1.29975  1.30039        49400       0            0
3 2020-02-18  1.30039  1.30486  1.29705  1.29952        62288       0            0
4 2020-02-19  1.29952  1.30230  1.29075  1.29187        57909       0            0
5 2020-02-20  1.29186  1.29281  1.28489  1.28792        61033       0            0
6 2020-02-21  1.28802  1.29805  1.28746  1.29566        66386       0            0
7 2020-02-24  1.29426  1.29547  1.28865  1.29283        66933       0            0
8 2020-02-25  1.29290  1.30178  1.29142  1.30037        80121       0            0
9 2020-02-26  1.30036  1.30078  1.29136  1.29374        49286       0            0
```

## See also

    `CopyRates`, `copy_rates_from`, `copy_rates_range`, `copy_ticks_from`, `copy_ticks_range`
        '''
        code=f'mt5.copy_rates_from_pos("{symbol}",{timeframe},{start_pos},{count})'
        print('code: ',code)
        return rpyc.utils.classic.obtain(self.__conn.eval(code))

    def copy_rates_range(self,symbol, timeframe, date_from, date_to):
        r'''
# copy_rates_range

Get bars in the specified date range from the MetaTrader 5 terminal.

```python
copy_rates_range(
   symbol,       # symbol name
   timeframe,    # timeframe
   date_from,    # date the bars are requested from
   date_to       # date, up to which the bars are requested
   )
```

## Parameters

- symbol

    [in]  Financial instrument name, for example, "EURUSD". Required unnamed parameter.

- timeframe

    [in]  Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration. Required unnamed parameter.

- date_from

    [in]  Date the bars are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time >= date_from are returned. Required unnamed parameter.

- date_to

    [in]  Date, up to which the bars are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned. Required unnamed parameter.

## Return Value

Returns bars as the numpy array with the named time, open, high, low, close, tick_volume, spread and real_volume columns. Returns None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

See the `CopyRates()` function for more information.

MetaTrader 5 terminal provides bars only within a history available to a user on charts. The number of bars available to users is set in the "Max. bars in chart" parameter.

When creating the 'datetime' object, Python uses the local time zone, while MetaTrader 5 stores tick and bar open time in UTC time zone (without the shift). Therefore, 'datetime' should be created in UTC time for executing functions that use time. Data received from the MetaTrader 5 terminal has UTC time.

## Example:

```python
from datetime import datetime
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# import the 'pandas' module for displaying data obtained in the tabular form
import pandas as pd
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# import pytz module for working with time zone
import pytz
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2020, 1, 10, tzinfo=timezone)
utc_to = datetime(2020, 1, 11, hour = 13, tzinfo=timezone)
# get bars from USDJPY M5 within the interval of 2020.01.10 00:00 - 2020.01.11 13:00 in UTC time zone
rates = mt5.copy_rates_range("USDJPY", mt5.TIMEFRAME_M5, utc_from, utc_to)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
 
# display each element of obtained data in a new line
print("Display obtained data 'as is'")
counter=0
for rate in rates:
    counter+=1
    if counter<=10:
        print(rate)
 
# create DataFrame out of the obtained data
rates_frame = pd.DataFrame(rates)
# convert time in seconds into the 'datetime' format
rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
 
# display data
print("\nDisplay dataframe with data")
print(rates_frame.head(10))
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
Display obtained data 'as is'
(1578614400, 109.513, 109.527, 109.505, 109.521, 43, 2, 0)
(1578614700, 109.521, 109.549, 109.518, 109.543, 215, 8, 0)
(1578615000, 109.543, 109.543, 109.466, 109.505, 98, 10, 0)
(1578615300, 109.504, 109.534, 109.502, 109.517, 155, 8, 0)
(1578615600, 109.517, 109.539, 109.513, 109.527, 71, 4, 0)
(1578615900, 109.526, 109.537, 109.484, 109.52, 106, 9, 0)
(1578616200, 109.52, 109.524, 109.508, 109.51, 205, 7, 0)
(1578616500, 109.51, 109.51, 109.491, 109.496, 44, 8, 0)
(1578616800, 109.496, 109.509, 109.487, 109.5, 85, 5, 0)
(1578617100, 109.5, 109.504, 109.487, 109.489, 82, 7, 0)
 
Display dataframe with data
                 time     open     high      low    close  tick_volume  spread  real_volume
0 2020-01-10 00:00:00  109.513  109.527  109.505  109.521           43       2            0
1 2020-01-10 00:05:00  109.521  109.549  109.518  109.543          215       8            0
2 2020-01-10 00:10:00  109.543  109.543  109.466  109.505           98      10            0
3 2020-01-10 00:15:00  109.504  109.534  109.502  109.517          155       8            0
4 2020-01-10 00:20:00  109.517  109.539  109.513  109.527           71       4            0
5 2020-01-10 00:25:00  109.526  109.537  109.484  109.520          106       9            0
6 2020-01-10 00:30:00  109.520  109.524  109.508  109.510          205       7            0
7 2020-01-10 00:35:00  109.510  109.510  109.491  109.496           44       8            0
8 2020-01-10 00:40:00  109.496  109.509  109.487  109.500           85       5            0
9 2020-01-10 00:45:00  109.500  109.504  109.487  109.489           82       7            0
```

## See also

    `CopyRates`, `copy_rates_from`, `copy_rates_range`, `copy_ticks_from`, `copy_ticks_range`


        '''
        code=f'mt5.copy_rates_range("{symbol}", {timeframe}, {repr(date_from.astimezone())}, {date_to})'
        return rpyc.utils.classic.obtain(self.__conn.eval(code))

    def copy_ticks_from(self,symbol, date_from, count, flags):
        r'''
# copy_ticks_from

Get ticks from the MetaTrader 5 terminal starting from the specified date.

```python
copy_ticks_from(
   symbol,       # symbol name
   date_from,    # date the ticks are requested from
   count,        # number of requested ticks
   flags         # combination of flags defining the type of requested ticks
   )
```

## Parameters

- symbol

    [in]  Financial instrument name, for example, "EURUSD". Required unnamed parameter.

- from

    [in]  Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.

- count

    [in]  Number of ticks to receive. Required unnamed parameter.

- flags

    [in]  A flag to define the type of the requested ticks. COPY_TICKS_INFO – ticks with Bid and/or Ask changes, COPY_TICKS_TRADE – ticks with changes in Last and Volume, COPY_TICKS_ALL – all ticks. Flag values are described in the COPY_TICKS enumeration. Required unnamed parameter.

## Return Value

Returns ticks as the numpy array with the named time, bid, ask, last and flags columns. The 'flags' value can be a combination of flags from the TICK_FLAG enumeration. Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

See the CopyTicks function for more information.

When creating the 'datetime' object, Python uses the local time zone, while MetaTrader 5 stores tick and bar open time in UTC time zone (without the shift). Therefore, 'datetime' should be created in UTC time for executing functions that use time. Data received from the MetaTrader 5 terminal has UTC time.

COPY_TICKS defines the types of ticks that can be requested using the `copy_ticks_from()` and `copy_ticks_range()` functions.

| ID               | Description                                       |
|------------------|---------------------------------------------------|
| COPY_TICKS_ALL   | all ticks                                         |
| COPY_TICKS_INFO  | ticks containing Bid and/or Ask price changes     |
| COPY_TICKS_TRADE | ticks containing Last and/or Volume price changes |

TICK_FLAG defines possible flags for ticks. These flags are used to describe ticks obtained by the `copy_ticks_from()` and `copy_ticks_range()` functions.

| ID               | Description             |
|------------------|-------------------------|
| TICK_FLAG_BID    | Bid price changed       |
| TICK_FLAG_ASK    | Ask price changed       |
| TICK_FLAG_LAST   | Last price changed      |
| TICK_FLAG_VOLUME | Volume changed          |
| TICK_FLAG_BUY    | last Buy price changed  |
| TICK_FLAG_SELL   | last Sell price changed |

## Example:

```python
from datetime import datetime
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# import the 'pandas' module for displaying data obtained in the tabular form
import pandas as pd
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# import pytz module for working with time zone
import pytz
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2020, 1, 10, tzinfo=timezone)
# request 100 000 EURUSD ticks starting from 10.01.2019 in UTC time zone
ticks = mt5.copy_ticks_from("EURUSD", utc_from, 100000, mt5.COPY_TICKS_ALL)
print("Ticks received:",len(ticks))
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
 
# display data on each tick on a new line
print("Display obtained ticks 'as is'")
count = 0
for tick in ticks:
    count+=1
    print(tick)
    if count >= 10:
        break
 
# create DataFrame out of the obtained data
ticks_frame = pd.DataFrame(ticks)
# convert time in seconds into the datetime format
ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
 
# display data
print("\nDisplay dataframe with ticks")
print(ticks_frame.head(10))  
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
Ticks received: 100000
Display obtained ticks 'as is'
(1578614400, 1.11051, 1.11069, 0., 0, 1578614400987, 134, 0.)
(1578614402, 1.11049, 1.11067, 0., 0, 1578614402025, 134, 0.)
(1578614404, 1.1105, 1.11066, 0., 0, 1578614404057, 134, 0.)
(1578614404, 1.11049, 1.11067, 0., 0, 1578614404344, 134, 0.)
(1578614412, 1.11052, 1.11064, 0., 0, 1578614412106, 134, 0.)
(1578614418, 1.11039, 1.11051, 0., 0, 1578614418265, 134, 0.)
(1578614418, 1.1104, 1.1105, 0., 0, 1578614418905, 134, 0.)
(1578614419, 1.11039, 1.11051, 0., 0, 1578614419519, 134, 0.)
(1578614456, 1.11037, 1.11065, 0., 0, 1578614456011, 134, 0.)
(1578614456, 1.11039, 1.11051, 0., 0, 1578614456015, 134, 0.)
 
Display dataframe with ticks
                 time      bid      ask  last  volume       time_msc  flags  volume_real
0 2020-01-10 00:00:00  1.11051  1.11069   0.0       0  1578614400987    134          0.0
1 2020-01-10 00:00:02  1.11049  1.11067   0.0       0  1578614402025    134          0.0
2 2020-01-10 00:00:04  1.11050  1.11066   0.0       0  1578614404057    134          0.0
3 2020-01-10 00:00:04  1.11049  1.11067   0.0       0  1578614404344    134          0.0
4 2020-01-10 00:00:12  1.11052  1.11064   0.0       0  1578614412106    134          0.0
5 2020-01-10 00:00:18  1.11039  1.11051   0.0       0  1578614418265    134          0.0
6 2020-01-10 00:00:18  1.11040  1.11050   0.0       0  1578614418905    134          0.0
7 2020-01-10 00:00:19  1.11039  1.11051   0.0       0  1578614419519    134          0.0
8 2020-01-10 00:00:56  1.11037  1.11065   0.0       0  1578614456011    134          0.0
9 2020-01-10 00:00:56  1.11039  1.11051   0.0       0  1578614456015    134          0.0
```

## See also

    `CopyRates`, `copy_rates_from_pos`, `copy_rates_range`, `copy_ticks_from`, `copy_ticks_range`


        '''
        code=f'mt5.copy_ticks_from("{symbol}", {repr(date_from.astimezone())}, {count}, {flags})'
        return rpyc.utils.classic.obtain(self.__conn.eval(code))

    def copy_ticks_range(self,symbol, date_from, date_to, flags):
        r'''
# copy_ticks_range

Get ticks for the specified date range from the MetaTrader 5 terminal.

```python
copy_ticks_range(
   symbol,       # symbol name
   date_from,    # date the ticks are requested from
   date_to,      # date, up to which the ticks are requested
   flags         # combination of flags defining the type of requested ticks
   )
```

## Parameters

- symbol

    [in]  Financial instrument name, for example, "EURUSD". Required unnamed parameter.

- date_from

    [in]  Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.

- date_to

    [in]  Date, up to which the ticks are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.

- flags

    [in]  A flag to define the type of the requested ticks. COPY_TICKS_INFO – ticks with Bid and/or Ask changes, COPY_TICKS_TRADE – ticks with changes in Last and Volume, COPY_TICKS_ALL – all ticks. Flag values are described in the COPY_TICKS enumeration. Required unnamed parameter.

## Return Value

Returns ticks as the numpy array with the named time, bid, ask, last and flags columns. The 'flags' value can be a combination of flags from the TICK_FLAG enumeration. Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

See the CopyTicks function for more information.

When creating the 'datetime' object, Python uses the local time zone, while MetaTrader 5 stores tick and bar open time in UTC time zone (without the shift). Therefore, 'datetime' should be created in UTC time for executing functions that use time. The data obtained from MetaTrader 5 have UTC time, but Python applies the local time shift again when trying to print them. Thus, the obtained data should also be corrected for visual presentation.

## Example:

```python
from datetime import datetime
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# import the 'pandas' module for displaying data obtained in the tabular form
import pandas as pd
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# import pytz module for working with time zone
import pytz
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
utc_from = datetime(2020, 1, 10, tzinfo=timezone)
utc_to = datetime(2020, 1, 11, tzinfo=timezone)
# request AUDUSD ticks within 11.01.2020 - 11.01.2020
ticks = mt5.copy_ticks_range("AUDUSD", utc_from, utc_to, mt5.COPY_TICKS_ALL)
print("Ticks received:",len(ticks))
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
 
# display data on each tick on a new line
print("Display obtained ticks 'as is'")
count = 0
for tick in ticks:
    count+=1
    print(tick)
    if count >= 10:
        break
 
# create DataFrame out of the obtained data
ticks_frame = pd.DataFrame(ticks)
# convert time in seconds into the datetime format
ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
 
# display data
print("\nDisplay dataframe with ticks")
print(ticks_frame.head(10)) 
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
Ticks received: 37008
Display obtained ticks 'as is'
(1578614400, 0.68577, 0.68594, 0., 0, 1578614400820, 134, 0.)
(1578614401, 0.68578, 0.68594, 0., 0, 1578614401128, 130, 0.)
(1578614401, 0.68575, 0.68594, 0., 0, 1578614401128, 130, 0.)
(1578614411, 0.68576, 0.68594, 0., 0, 1578614411388, 130, 0.)
(1578614411, 0.68575, 0.68594, 0., 0, 1578614411560, 130, 0.)
(1578614414, 0.68576, 0.68595, 0., 0, 1578614414973, 134, 0.)
(1578614430, 0.68576, 0.68594, 0., 0, 1578614430188, 4, 0.)
(1578614450, 0.68576, 0.68595, 0., 0, 1578614450408, 4, 0.)
(1578614450, 0.68576, 0.68594, 0., 0, 1578614450519, 4, 0.)
(1578614456, 0.68575, 0.68594, 0., 0, 1578614456363, 130, 0.)
 
Display dataframe with ticks
                 time      bid      ask  last  volume       time_msc  flags  volume_real
0 2020-01-10 00:00:00  0.68577  0.68594   0.0       0  1578614400820    134          0.0
1 2020-01-10 00:00:01  0.68578  0.68594   0.0       0  1578614401128    130          0.0
2 2020-01-10 00:00:01  0.68575  0.68594   0.0       0  1578614401128    130          0.0
3 2020-01-10 00:00:11  0.68576  0.68594   0.0       0  1578614411388    130          0.0
4 2020-01-10 00:00:11  0.68575  0.68594   0.0       0  1578614411560    130          0.0
5 2020-01-10 00:00:14  0.68576  0.68595   0.0       0  1578614414973    134          0.0
6 2020-01-10 00:00:30  0.68576  0.68594   0.0       0  1578614430188      4          0.0
7 2020-01-10 00:00:50  0.68576  0.68595   0.0       0  1578614450408      4          0.0
8 2020-01-10 00:00:50  0.68576  0.68594   0.0       0  1578614450519      4          0.0
9 2020-01-10 00:00:56  0.68575  0.68594   0.0       0  1578614456363    130          0.0
```

## See also

    `CopyRates`, `copy_rates_from_pos`, `copy_rates_range`, `copy_ticks_from`, `copy_ticks_range`
        '''
        code=f'mt5.copy_ticks_range("{symbol}", {repr(date_from.astimezone())}, {repr(date_to.astimezone())}, {flags})'
        return rpyc.utils.classic.obtain(self.__conn.eval(code))

    def orders_total(self,*args,**kwargs):
        r'''
# orders_total

Get the number of active orders.

```python
orders_total()
```

## Return Value

Integer value.

## Note

The function is similar to `OrdersTotal`.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# check the presence of active orders
orders=mt5.orders_total()
if orders>0:
    print("Total orders=",orders)
else:
    print("Orders not found")
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## See also

    `orders_get`, `positions_total`


        '''
        code=f'mt5.orders_total(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def orders_get(self,*args,**kwargs):
        r'''
# orders_get

Get active orders with the ability to filter by symbol or ticket. There are three call options.

Call without parameters. Return active orders on all symbols.

```python
orders_get()
```

Call specifying a symbol active orders should be received for.

```python
orders_get(
   symbol="SYMBOL"      # symbol name
)
```

Call specifying a group of symbols active orders should be received for.

```python
orders_get(
   group="GROUP"        # filter for selecting orders for symbols
)
```

Call specifying the order ticket.

```python
orders_get(
   ticket=TICKET        # ticket
)
```

- symbol="SYMBOL"

    [in]  Symbol name. Optional named parameter. If a symbol is specified, the ticket parameter is ignored.

- group="GROUP"

    [in]  The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only active orders meeting a specified criteria for a symbol name.

- ticket=TICKET

    [in]  Order ticket (ORDER_TICKET). Optional named parameter.

## Return Value

Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The function allows receiving all active orders within one call similar to the OrdersTotal and OrderSelect tandem.

The group parameter allows sorting out orders by symbols. '*' can be used at the beginning and the end of a string.

The group parameter may contain several comma separated conditions. A condition can be set as a mask using '*'. The logical negation symbol '!' can be used for an exclusion. All conditions are applied sequentially, which means conditions of including to a group should be specified first followed by an exclusion condition. For example, group="*, !EUR" means that orders for all symbols should be selected first and the ones containing "EUR" in symbol names should be excluded afterwards.

## Example:

```python
import MetaTrader5 as mt5
import pandas as pd
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
print()
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# display data on active orders on GBPUSD
orders=mt5.orders_get(symbol="GBPUSD")
if orders is None:
    print("No orders on GBPUSD, error code={}".format(mt5.last_error()))
else:
    print("Total orders on GBPUSD:",len(orders))
    # display all active orders
    for order in orders:
        print(order)
print()
 
# get the list of orders on symbols whose names contain "*GBP*"
gbp_orders=mt5.orders_get(group="*GBP*")
if gbp_orders is None:
    print("No orders with group=\"*GBP*\", error code={}".format(mt5.last_error()))
else:
    print("orders_get(group=\"*GBP*\")={}".format(len(gbp_orders)))
    # display these orders as a table using pandas.DataFrame
    df=pd.DataFrame(list(gbp_orders),columns=gbp_orders[0]._asdict().keys())
    df.drop(['time_done', 'time_done_msc', 'position_id', 'position_by_id', 'reason', 'volume_initial', 'price_stoplimit'], axis=1, inplace=True)
    df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
    print(df)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
Total orders on GBPUSD: 2
TradeOrder(ticket=554733548, time_setup=1585153667, time_setup_msc=1585153667718, time_done=0, time_done_msc=0, time_expiration=0, type=3, type_time=0, ...
TradeOrder(ticket=554733621, time_setup=1585153671, time_setup_msc=1585153671419, time_done=0, time_done_msc=0, time_expiration=0, type=2, type_time=0, ...
 
orders_get(group="*GBP*")=4
      ticket          time_setup  time_setup_msc  time_expiration  type  type_time  type_filling  state  magic  volume_current  price_open   sl   tp  price_current  symbol comment external_id
0  554733548 2020-03-25 16:27:47   1585153667718                0     3          0             2      1      0             0.2     1.25379  0.0  0.0        1.16803  GBPUSD                    
1  554733621 2020-03-25 16:27:51   1585153671419                0     2          0             2      1      0             0.2     1.14370  0.0  0.0        1.16815  GBPUSD                    
2  554746664 2020-03-25 16:38:14   1585154294401                0     3          0             2      1      0             0.2     0.93851  0.0  0.0        0.92428  EURGBP                    
3  554746710 2020-03-25 16:38:17   1585154297022                0     2          0             2      1      0             0.2     0.90527  0.0  0.0        0.92449  EURGBP    
```

## See also

    `orders_total`, `positions_get`


        '''
        code=f'mt5.orders_get(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def order_calc_margin(self,*args,**kwargs):
        r'''
# order_calc_margin

Return margin in the account currency to perform a specified trading operation.

```python
order_calc_margin(
   action,      # order type (ORDER_TYPE_BUY or ORDER_TYPE_SELL)
   symbol,      # symbol name
   volume,      # volume
   price        # open price
   )
```

## Parameters

- action

    [in]  Order type taking values from the `ORDER_TYPE` enumeration. Required unnamed parameter.

- symbol

    [in]  Financial instrument name. Required unnamed parameter.

- volume

    [in]  Trading operation volume. Required unnamed parameter.

- price

    [in]  Open price. Required unnamed parameter.

## Return Value

Real value if successful, otherwise None. The error info can be obtained using `last_error()`.

## Note

The function allows estimating the margin necessary for a specified order type on the current account and in the current market environment without considering the current pending orders and open positions. The function is similar to `OrderCalcMargin`.

| ID                         | Description                                                                          |
|----------------------------|--------------------------------------------------------------------------------------|
| ORDER_TYPE_BUY             | Market buy order                                                                     |
| ORDER_TYPE_SELL            | Market sell order                                                                    |
| ORDER_TYPE_BUY_LIMIT       | Buy Limit pending order                                                              |
| ORDER_TYPE_SELL_LIMIT      | Sell Limit pending order                                                             |
| ORDER_TYPE_BUY_STOP        | Buy Stop pending order                                                               |
| ORDER_TYPE_SELL_STOP       | Sell Stop pending order                                                              |
| ORDER_TYPE_BUY_STOP_LIMIT  | Upon reaching the order price, Buy Limit pending order is placed at StopLimit price  |
| ORDER_TYPE_SELL_STOP_LIMIT | Upon reaching the order price, Sell Limit pending order is placed at StopLimit price |
| ORDER_TYPE_CLOSE_BY        | Order for closing a position by an opposite one                                      |

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get account currency
account_currency=mt5.account_info().currency
print("Account сurrency:",account_currency)
 
# arrange the symbol list
symbols=("EURUSD","GBPUSD","USDJPY", "USDCHF","EURJPY","GBPJPY")
print("Symbols to check margin:", symbols)
action=mt5.ORDER_TYPE_BUY
lot=0.1
for symbol in symbols:
    symbol_info=mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol,"not found, skipped")
        continue
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol,True):
            print("symbol_select({}}) failed, skipped",symbol)
            continue
    ask=mt5.symbol_info_tick(symbol).ask
    margin=mt5.order_calc_margin(action,symbol,lot,ask)
    if margin != None:
        print("   {} buy {} lot margin: {} {}".format(symbol,lot,margin,account_currency));
    else:
        print("order_calc_margin failed: , error code =", mt5.last_error())
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
Account сurrency: USD
 
Symbols to check margin: ('EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'EURJPY', 'GBPJPY')
   EURUSD buy 0.1 lot margin: 109.91 USD
   GBPUSD buy 0.1 lot margin: 122.73 USD
   USDJPY buy 0.1 lot margin: 100.0 USD
   USDCHF buy 0.1 lot margin: 100.0 USD
   EURJPY buy 0.1 lot margin: 109.91 USD
   GBPJPY buy 0.1 lot margin: 122.73 USD
```

## See also

    `order_calc_profit`, `order_check`


        '''
        code=f'mt5.order_calc_margin(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def order_calc_profit(self,*args,**kwargs):
        r'''
# order_calc_profit

Return profit in the account currency for a specified trading operation.

```python
order_calc_profit(
   action,          # order type (ORDER_TYPE_BUY or ORDER_TYPE_SELL)
   symbol,          # symbol name
   volume,          # volume
   price_open,      # open price
   price_close      # close price
   );
```

## Parameters

- action

    [in]  Order type may take one of the two `ORDER_TYPE` enumeration values: `ORDER_TYPE_BUY` or `ORDER_TYPE_SELL`. Required unnamed parameter.

- symbol

    [in]  Financial instrument name. Required unnamed parameter.

- volume

    [in]  Trading operation volume. Required unnamed parameter.

- price_open

    [in]  Open price. Required unnamed parameter.

- price_close

    [in]  Close price. Required unnamed parameter.

## Return Value

Real value if successful, otherwise None. The error info can be obtained using `last_error()`.

## Note

The function allows estimating a trading operation result on the current account and in the current trading environment. The function is similar to `OrderCalcProfit`.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get account currency
account_currency=mt5.account_info().currency
print("Account сurrency:",account_currency)
 
# arrange the symbol list
symbols = ("EURUSD","GBPUSD","USDJPY")
print("Symbols to check margin:", symbols)
# estimate profit for buying and selling
lot=1.0
distance=300
for symbol in symbols:
    symbol_info=mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol,"not found, skipped")
        continue
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol,True):
            print("symbol_select({}}) failed, skipped",symbol)
            continue
    point=mt5.symbol_info(symbol).point
    symbol_tick=mt5.symbol_info_tick(symbol)
    ask=symbol_tick.ask
    bid=symbol_tick.bid
    buy_profit=mt5.order_calc_profit(mt5.ORDER_TYPE_BUY,symbol,lot,ask,ask+distance*point)
    if buy_profit!=None:
        print("   buy {} {} lot: profit on {} points => {} {}".format(symbol,lot,distance,buy_profit,account_currency));
    else:
        print("order_calc_profit(ORDER_TYPE_BUY) failed, error code =",mt5.last_error())
    sell_profit=mt5.order_calc_profit(mt5.ORDER_TYPE_SELL,symbol,lot,bid,bid-distance*point)
    if sell_profit!=None:
        print("   sell {} {} lots: profit on {} points => {} {}".format(symbol,lot,distance,sell_profit,account_currency));
    else:
        print("order_calc_profit(ORDER_TYPE_SELL) failed, error code =",mt5.last_error())
    print()
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
Account сurrency: USD
Symbols to check margin: ('EURUSD', 'GBPUSD', 'USDJPY')
   buy EURUSD 1.0 lot: profit on 300 points => 300.0 USD
   sell EURUSD 1.0 lot: profit on 300 points => 300.0 USD
 
   buy GBPUSD 1.0 lot: profit on 300 points => 300.0 USD
   sell GBPUSD 1.0 lot: profit on 300 points => 300.0 USD
 
   buy USDJPY 1.0 lot: profit on 300 points => 276.54 USD
   sell USDJPY 1.0 lot: profit on 300 points => 278.09 USD
```

## See also

    `order_calc_margin`, `order_check`
        '''
        code=f'mt5.order_calc_profit(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def order_check(self,*args,**kwargs):
        r'''
# order_check

Check funds sufficiency for performing a required trading operation. Check result are returned as the MqlTradeCheckResult structure.

```python
order_check(
   request      # request structure
   );
```

## Parameters

- request

    [in] MqlTradeRequest type structure describing a required trading action. Required unnamed parameter. Example of filling in a request and the enumeration content are described below.

## Return Value

Check result as the `MqlTradeCheckResult` structure. The request field in the answer contains the structure of a trading request passed to `order_check()`.

## Note

Successful sending of a request does not entail that the requested trading operation will be executed successfully. The order_check function is similar to `OrderCheck`.

### TRADE_REQUEST_ACTIONS

| ID                    | Description                                                                           |
|-----------------------|---------------------------------------------------------------------------------------|
| TRADE_ACTION_DEAL     | Place an order for an instant deal with the specified parameters (set a market order) |
| TRADE_ACTION_PENDING  | Place an order for performing a deal at specified conditions (pending order)          |
| TRADE_ACTION_SLTP     | Change open position Stop Loss and Take Profit                                        |
| TRADE_ACTION_MODIFY   | Change parameters of the previously placed trading order                              |
| TRADE_ACTION_REMOVE   | Remove previously placed pending order                                                |
| TRADE_ACTION_CLOSE_BY | Close a position by an opposite one                                                   |

### ORDER_TYPE_FILLING

| ID                   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ORDER_FILLING_FOK    | This execution policy means that an order can be executed only in the specified volume. If the necessary amount of a financial instrument is currently unavailable in the market, the order will not be executed. The desired volume can be made up of several available offers.                                                                                                                                                                                                                                                                                                                                 |
| ORDER_FILLING_IOC    | An agreement to execute a deal at the maximum volume available in the market within the volume specified in the order. If the request cannot be filled completely, an order with the available volume will be executed, and the remaining volume will be canceled.                                                                                                                                                                                                                                                                                                                                               |
| ORDER_FILLING_RETURN | This policy is used only for market (ORDER_TYPE_BUY and ORDER_TYPE_SELL), limit and stop limit orders (ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT, ORDER_TYPE_BUY_STOP_LIMIT and ORDER_TYPE_SELL_STOP_LIMIT) and only for the symbols with Market or Exchange execution modes. If filled partially, a market or limit order with the remaining volume is not canceled, and is processed further. During activation of the ORDER_TYPE_BUY_STOP_LIMIT and ORDER_TYPE_SELL_STOP_LIMIT orders, an appropriate limit order ORDER_TYPE_BUY_LIMIT/ORDER_TYPE_SELL_LIMIT with the ORDER_FILLING_RETURN type is created. |

### ORDER_TYPE_TIME

| ID                       | Description                                                                                                                                                            |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ORDER_TIME_GTC           | The order stays in the queue until it is manually canceled                                                                                                             |
| ORDER_TIME_DAY           | The order is active only during the current trading day                                                                                                                |
| ORDER_TIME_SPECIFIED     | The order is active until the specified date                                                                                                                           |
| ORDER_TIME_SPECIFIED_DAY | The order is active until 23:59:59 of the specified day. If this time appears to be out of a trading session, the expiration is processed at the nearest trading time. |

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get account currency
account_currency=mt5.account_info().currency
print("Account сurrency:",account_currency)
 
# prepare the request structure
symbol="USDJPY"
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(symbol, "not found, can not call order_check()")
    mt5.shutdown()
    quit()
 
# if the symbol is unavailable in MarketWatch, add it
if not symbol_info.visible:
    print(symbol, "is not visible, trying to switch on")
    if not mt5.symbol_select(symbol,True):
        print("symbol_select({}}) failed, exit",symbol)
        mt5.shutdown()
        quit()
 
# prepare the request
point=mt5.symbol_info(symbol).point
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": 1.0,
    "type": mt5.ORDER_TYPE_BUY,
    "price": mt5.symbol_info_tick(symbol).ask,
    "sl": mt5.symbol_info_tick(symbol).ask-100*point,
    "tp": mt5.symbol_info_tick(symbol).ask+100*point,
    "deviation": 10,
    "magic": 234000,
    "comment": "python script",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}
 
# perform the check and display the result 'as is'
result = mt5.order_check(request)
print(result);
# request the result as a dictionary and display it element by element
result_dict=result._asdict()
for field in result_dict.keys():
    print("   {}={}".format(field,result_dict[field]))
    # if this is a trading request structure, display it element by element as well
    if field=="request":
        traderequest_dict=result_dict[field]._asdict()
        for tradereq_filed in traderequest_dict:
            print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
Account сurrency: USD
   retcode=0
   balance=101300.53
   equity=68319.53
   profit=-32981.0
   margin=51193.67
   margin_free=17125.86
   margin_level=133.45308121101692
   comment=Done
   request=TradeRequest(action=1, magic=234000, order=0, symbol='USDJPY', volume=1.0, ...
       traderequest: action=1
       traderequest: magic=234000
       traderequest: order=0
       traderequest: symbol=USDJPY
       traderequest: volume=1.0
       traderequest: price=108.081
       traderequest: stoplimit=0.0
       traderequest: sl=107.98100000000001
       traderequest: tp=108.181
       traderequest: deviation=10
       traderequest: type=0
       traderequest: type_filling=2
       traderequest: type_time=0
       traderequest: expiration=0
       traderequest: comment=python script
       traderequest: position=0
       traderequest: position_by=0
```

## See also

    `order_send`, `OrderCheck`, Trading operation types, Trading request structure, Structure of the trading request check results, Structure of the trading request result


        '''
        code=f'mt5.order_check(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def order_send(self,*args,**kwargs):
        r'''
# order_send

Send a request to perform a trading operation from the terminal to the trade server. The function is similar to OrderSend.

```python
order_send(
   request      # request structure
   );
```

## Parameters

request

    [in] `MqlTradeRequest` type structure describing a required trading action. Required unnamed parameter. Example of filling in a request and the enumeration content are described below.

## Return Value

Execution result as the `MqlTradeResult` structure. The request field in the answer contains the structure of a trading request passed to `order_send()`.

The `MqlTradeRequest` trading request structure

| Field        | Description                                                                                                                                                                                                |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| action       | Trading operation type. The value can be one of the values of the TRADE_REQUEST_ACTIONS enumeration                                                                                                        |
| magic        | EA ID. Allows arranging the analytical handling of trading orders. Each EA can set a unique ID when sending a trading request                                                                              |
| order        | Order ticket. Required for modifying pending orders                                                                                                                                                        |
| symbol       | The name of the trading instrument, for which the order is placed. Not required when modifying orders and closing positions                                                                                |
| volume       | Requested volume of a deal in lots. A real volume when making a deal depends on an order execution type.                                                                                                   |
| price        | Price at which an order should be executed. The price is not set in case of market orders for instruments of the "Market Execution" (SYMBOL_TRADE_EXECUTION_MARKET) type having the TRADE_ACTION_DEAL type |
| stoplimit    | A price a pending Limit order is set at when the price reaches the 'price' value (this condition is mandatory). The pending order is not passed to the trading system until that moment                    |
| sl           | A price a Stop Loss order is activated at when the price moves in an unfavorable direction                                                                                                                 |
| tp           | A price a Take Profit order is activated at when the price moves in a favorable direction                                                                                                                  |
| deviation    | Maximum acceptable deviation from the requested price, specified in points                                                                                                                                 |
| type         | Order type. The value can be one of the values of the ORDER_TYPE enumeration                                                                                                                               |
| type_filling | Order filling type. The value can be one of the ORDER_TYPE_FILLING values                                                                                                                                  |
| type_time    | Order type by expiration. The value can be one of the ORDER_TYPE_TIME values                                                                                                                               |
| expiration   | Pending order expiration time (for TIME_SPECIFIED type orders)                                                                                                                                             |
| comment      | Comment to an order                                                                                                                                                                                        |
| position     | Position ticket. Fill it when changing and closing a position for its clear identification. Usually, it is the same as the ticket of the order that opened the position.                                   |
| position_by  | Opposite position ticket. It is used when closing a position by an opposite one (opened at the same symbol but in the opposite direction).                                                                 |

## Note

A trading request passes several verification stages on the trade server. First, the validity of all the necessary request fields is checked. If there are no errors, the server accepts the order for further handling. See the OrderSend function description for the details about executing trading operations.

## Example:

```python
import time
import MetaTrader5 as mt5
 
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# prepare the buy request structure
symbol = "USDJPY"
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(symbol, "not found, can not call order_check()")
    mt5.shutdown()
    quit()
 
# if the symbol is unavailable in MarketWatch, add it
if not symbol_info.visible:
    print(symbol, "is not visible, trying to switch on")
    if not mt5.symbol_select(symbol,True):
        print("symbol_select({}}) failed, exit",symbol)
        mt5.shutdown()
        quit()
 
lot = 0.1
point = mt5.symbol_info(symbol).point
price = mt5.symbol_info_tick(symbol).ask
deviation = 20
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "sl": price - 100 * point,
    "tp": price + 100 * point,
    "deviation": deviation,
    "magic": 234000,
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}
 
# send a trading request
result = mt5.order_send(request)
# check the execution result
print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation));
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print("2. order_send failed, retcode={}".format(result.retcode))
    # request the result as a dictionary and display it element by element
    result_dict=result._asdict()
    for field in result_dict.keys():
        print("   {}={}".format(field,result_dict[field]))
        # if this is a trading request structure, display it element by element as well
        if field=="request":
            traderequest_dict=result_dict[field]._asdict()
            for tradereq_filed in traderequest_dict:
                print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
    print("shutdown() and quit")
    mt5.shutdown()
    quit()
 
print("2. order_send done, ", result)
print("   opened position with POSITION_TICKET={}".format(result.order))
print("   sleep 2 seconds before closing position #{}".format(result.order))
time.sleep(2)
# create a close request
position_id=result.order
price=mt5.symbol_info_tick(symbol).bid
deviation=20
request={
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_SELL,
    "position": position_id,
    "price": price,
    "deviation": deviation,
    "magic": 234000,
    "comment": "python script close",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}
# send a trading request
result=mt5.order_send(request)
# check the execution result
print("3. close position #{}: sell {} {} lots at {} with deviation={} points".format(position_id,symbol,lot,price,deviation));
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print("4. order_send failed, retcode={}".format(result.retcode))
    print("   result",result)
else:
    print("4. position #{} closed, {}".format(position_id,result))
    # request the result as a dictionary and display it element by element
    result_dict=result._asdict()
    for field in result_dict.keys():
        print("   {}={}".format(field,result_dict[field]))
        # if this is a trading request structure, display it element by element as well
        if field=="request":
            traderequest_dict=result_dict[field]._asdict()
            for tradereq_filed in traderequest_dict:
                print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

# Result

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
1. order_send(): by USDJPY 0.1 lots at 108.023 with deviation=20 points
2. order_send done,  OrderSendResult(retcode=10009, deal=535084512, order=557416535, volume=0.1, price=108.023, ...
   opened position with POSITION_TICKET=557416535
   sleep 2 seconds before closing position #557416535
3. close position #557416535: sell USDJPY 0.1 lots at 108.018 with deviation=20 points
4. position #557416535 closed, OrderSendResult(retcode=10009, deal=535084631, order=557416654, volume=0.1, price=...
   retcode=10009
   deal=535084631
   order=557416654
   volume=0.1
   price=108.015
   bid=108.015
   ask=108.02
   comment=Request executed
   request_id=55
   retcode_external=0
   request=TradeRequest(action=1, magic=234000, order=0, symbol='USDJPY', volume=0.1, price=108.018, stoplimit=0.0, ...
       traderequest: action=1
       traderequest: magic=234000
       traderequest: order=0
       traderequest: symbol=USDJPY
       traderequest: volume=0.1
       traderequest: price=108.018
       traderequest: stoplimit=0.0
       traderequest: sl=0.0
       traderequest: tp=0.0
       traderequest: deviation=20
       traderequest: type=1
       traderequest: type_filling=2
       traderequest: type_time=0
       traderequest: expiration=0
       traderequest: comment=python script close
       traderequest: position=557416535
       traderequest: position_by=0
```

## See also

    `order_check`, `OrderSend`,Trading operation types, Trading request structure, Structure of the trading request check results, Structure of the trading request result
        '''
        code=f'mt5.order_send(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def positions_total(self,*args,**kwargs):
        r'''
# positions_total

Get the number of open positions.

```python
positions_total()
```

## Return Value

Integer value.

## Note

The function is similar to `PositionsTotal`.

## Example:

```python
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# check the presence of open positions
positions_total=mt5.positions_total()
if positions_total>0:
    print("Total positions=",positions_total)
else:
    print("Positions not found")
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## See also

    `positions_get`, `orders_total`


        '''
        code=f'mt5.positions_total(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def positions_get(self,*args,**kwargs):
        r'''
# positions_get

Get open positions with the ability to filter by symbol or ticket. There are three call options.

Call without parameters. Return open positions for all symbols.

```python
positions_get()
```

Call specifying a symbol open positions should be received for.

```python
positions_get(
   symbol="SYMBOL"      # symbol name
)
```

Call specifying a group of symbols open positions should be received for.

```python
positions_get(
   group="GROUP"        # filter for selecting positions by symbols
)
```

Call specifying a position ticket.

```python
positions_get(
   ticket=TICKET        # ticket
)
```

## Parameters

- symbol="SYMBOL"

    [in]  Symbol name. Optional named parameter. If a symbol is specified, the ticket parameter is ignored.

- group="GROUP"

    [in]  The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only positions meeting a specified criteria for a symbol name.

- ticket=TICKET

    [in]  Position ticket (`POSITION_TICKET`). Optional named parameter.

## Return Value

Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The function allows receiving all open positions within one call similar to the `PositionsTotal` and `PositionSelect` tandem.

The group parameter may contain several comma separated conditions. A condition can be set as a mask using '*'. The logical negation symbol '!' can be used for an exclusion. All conditions are applied sequentially, which means conditions of including to a group should be specified first followed by an exclusion condition. For example, group="*, !EUR" means that positions for all symbols should be selected first and the ones containing "EUR" in symbol names should be excluded afterwards.

## Example:

```python
import MetaTrader5 as mt5
import pandas as pd
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
print()
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get open positions on USDCHF
positions=mt5.positions_get(symbol="USDCHF")
if positions==None:
    print("No positions on USDCHF, error code={}".format(mt5.last_error()))
elif len(positions)>0:
    print("Total positions on USDCHF =",len(positions))
    # display all open positions
    for position in positions:
        print(position)
 
# get the list of positions on symbols whose names contain "*USD*"
usd_positions=mt5.positions_get(group="*USD*")
if usd_positions==None:
    print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
elif len(usd_positions)>0:
    print("positions_get(group=\"*USD*\")={}".format(len(usd_positions)))
    # display these positions as a table using pandas.DataFrame
    df=pd.DataFrame(list(usd_positions),columns=usd_positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    print(df)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
positions_get(group="*USD*")=5
      ticket                time  type  magic  identifier  reason  volume  price_open       sl       tp  price_current  swap  profit  symbol comment
0  548297723 2020-03-18 15:00:55     1      0   548297723       3    0.01     1.09301  1.11490  1.06236        1.10104 -0.10   -8.03  EURUSD        
1  548655158 2020-03-18 20:31:26     0      0   548655158       3    0.01     1.08676  1.06107  1.12446        1.10099 -0.08   14.23  EURUSD        
2  548663803 2020-03-18 20:40:04     0      0   548663803       3    0.01     1.08640  1.06351  1.11833        1.10099 -0.08   14.59  EURUSD        
3  548847168 2020-03-19 01:10:05     0      0   548847168       3    0.01     1.09545  1.05524  1.15122        1.10099 -0.06    5.54  EURUSD        
4  548847194 2020-03-19 01:10:07     0      0   548847194       3    0.02     1.09536  1.04478  1.16587        1.10099 -0.08   11.26  EURUSD   
```

## See also

    `positions_total`, `orders_get`


        '''
        code=f'mt5.positions_get(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def history_orders_total(self,date_from, date_to):
        r'''
# history_orders_total

Get the number of orders in trading history within the specified interval.

```python
history_orders_total(
   date_from,    # date the orders are requested from
   date_to       # date, up to which the orders are requested
   )
```

## Parameters

- date_from

    [in]  Date the orders are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.

- date_to

    [in]  Date, up to which the orders are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.

## Return Value

Integer value.

## Note

The function is similar to `HistoryOrdersTotal`.

## Example:

```python
from datetime import datetime
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get the number of orders in history
from_date=datetime(2020,1,1)
to_date=datetime.now()
history_orders=mt5.history_orders_total(from_date, datetime.now())
if history_orders>0:
    print("Total history orders=",history_orders)
else:
    print("Orders not found in history")
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## See also

    `history_orders_get`, `history_deals_total`
        '''
        code=f'mt5.history_orders_total({repr(date_from.astimezone())}, {repr(date_to.astimezone())})'
        return self.__conn.eval(code)

    def history_orders_get(self,*args,**kwargs):
        r'''
#history_orders_get

Get orders from trading history with the ability to filter by ticket or position. There are three call options.

Call specifying a time interval. Return all orders falling within the specified interval.

```python
history_orders_get(
   date_from,                # date the orders are requested from
   date_to,                  # date, up to which the orders are requested
   group="GROUP"        # filter for selecting orders by symbols
   )
```

Call specifying the order ticket. Return an order with the specified ticket.

```python
positions_get(
   ticket=TICKET        # order ticket
)
```

Call specifying the position ticket. Return all orders with a position ticket specified in the ORDER_POSITION_ID property.

```python
positions_get(
   position=POSITION    # position ticket
)
```

## Parameters

- date_from

    [in]  Date the orders are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter is specified first.

- date_to

    [in]  Date, up to which the orders are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter is specified second.

- group="GROUP"

    [in]  The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only orders meeting a specified criteria for a symbol name.

- ticket=TICKET

    [in]  Order ticket that should be received. Optional parameter. If not specified, the filter is not applied.

- position=POSITION

    [in]  Ticket of a position (stored in `ORDER_POSITION_ID`) all orders should be received for. Optional parameter. If not specified, the filter is not applied.

## Return Value

Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The function allows receiving all history orders within a specified period in a single call similar to the HistoryOrdersTotal and HistoryOrderSelect tandem.

The group parameter may contain several comma separated conditions. A condition can be set as a mask using '*'. The logical negation symbol '!' can be used for an exclusion. All conditions are applied sequentially, which means conditions of including to a group should be specified first followed by an exclusion condition. For example, group="*, !EUR" means that deals for all symbols should be selected first and the ones containing "EUR" in symbol names should be excluded afterwards.

## Example:

```python
from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
print()
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get the number of orders in history
from_date=datetime(2020,1,1)
to_date=datetime.now()
history_orders=mt5.history_orders_get(from_date, to_date, group="*GBP*")
if history_orders==None:
    print("No history orders with group=\"*GBP*\", error code={}".format(mt5.last_error()))
elif len(history_orders)>0:
    print("history_orders_get({}, {}, group=\"*GBP*\")={}".format(from_date,to_date,len(history_orders)))
print()
 
# display all historical orders by a position ticket
position_id=530218319
position_history_orders=mt5.history_orders_get(position=position_id)
if position_history_orders==None:
    print("No orders with position #{}".format(position_id))
    print("error code =",mt5.last_error())
elif len(position_history_orders)>0:
    print("Total history orders on position #{}: {}".format(position_id,len(position_history_orders)))
    # display all historical orders having a specified position ticket
    for position_order in position_history_orders:        
        print(position_order)
    print()
    # display these orders as a table using pandas.DataFrame
    df=pd.DataFrame(list(position_history_orders),columns=position_history_orders[0]._asdict().keys())
    df.drop(['time_expiration','type_time','state','position_by_id','reason','volume_current','price_stoplimit','sl','tp'], axis=1, inplace=True)
    df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
    df['time_done'] = pd.to_datetime(df['time_done'], unit='s')
    print(df)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
history_orders_get(2020-01-01 00:00:00, 2020-03-25 17:17:32.058795, group="*GBP*")=14
 
Total history orders on position #530218319: 2
TradeOrder(ticket=530218319, time_setup=1582282114, time_setup_msc=1582282114681, time_done=1582303777, time_done_msc=1582303777582, time_expiration=0, ...
TradeOrder(ticket=535548147, time_setup=1583176242, time_setup_msc=1583176242265, time_done=1583176242, time_done_msc=1583176242265, time_expiration=0, ...
 
      ticket          time_setup  time_setup_msc           time_done  time_done_msc  type  type_filling  magic  position_id  volume_initial  price_open  price_current  symbol comment external_id
0  530218319 2020-02-21 10:48:34   1582282114681 2020-02-21 16:49:37  1582303777582     2             2      0    530218319            0.01     0.97898        0.97863  USDCHF                    
1  535548147 2020-03-02 19:10:42   1583176242265 2020-03-02 19:10:42  1583176242265     1             0      0    530218319            0.01     0.95758        0.95758  USDCHF   
```

## See also

    `history_deals_total`, `history_deals_get`


        '''
        code=f'mt5.history_orders_get(*{args},**{kwargs})'
        return self.__conn.eval(code)

    def history_deals_total(self,date_from, date_to):
        r'''
#history_deals_total

Get the number of deals in trading history within the specified interval.

```python
history_deals_total(
   date_from,    # date the deals are requested from
   date_to       # date, up to which the deals are requested
   )
```

## Parameters

- date_from

    [in]  Date the deals are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.

- date_to

    [in]  Date, up to which the deals are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.

## Return Value

Integer value.

## Note

The function is similar to `HistoryDealsTotal`.

## Example:

```python
from datetime import datetime
import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get the number of deals in history
from_date=datetime(2020,1,1)
to_date=datetime.now()
deals=mt5.history_deals_total(from_date, to_date)
if deals>0:
    print("Total deals=",deals)
else:
    print("Deals not found in history")
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## See also

    `history_deals_get`, `history_orders_total`


        '''
        code=f'mt5.history_deals_total({repr(date_from.astimezone())}, {repr(date_to.astimezone())})'
        return self.__conn.eval(code)

    def history_deals_get(self,*args,**kwargs):
        r'''
#history_deals_get

Get deals from trading history within the specified interval with the ability to filter by ticket or position.

Call specifying a time interval. Return all deals falling within the specified interval.

```python
history_deals_get(
   date_from,                # date the deals are requested from
   date_to,                  # date, up to which the deals are requested
   group="GROUP"        # filter for selecting deals for symbols
   )
```

Call specifying the order ticket. Return all deals having the specified order ticket in the DEAL_ORDER property.

```python
history_deals_get(
   ticket=TICKET        # order ticket
)
```

Call specifying the position ticket. Return all deals having the specified position ticket in the DEAL_POSITION_ID property.

```python
history_deals_get(
   position=POSITION    # position ticket
)
```

## Parameters

- date_from

    [in]  Date the orders are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter is specified first.

- date_to

    [in]  Date, up to which the orders are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter is specified second.

- group="GROUP"

    [in]  The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only deals meeting a specified criteria for a symbol name.

- ticket=TICKET

    [in]  Ticket of an order (stored in `DEAL_ORDER`) all deals should be received for. Optional parameter. If not specified, the filter is not applied.

- position=POSITION

    [in]  Ticket of a position (stored in `DEAL_POSITION_ID`) all deals should be received for. Optional parameter. If not specified, the filter is not applied.

## Return Value

Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using `last_error()`.

## Note

The function allows receiving all history deals within a specified period in a single call similar to the HistoryDealsTotal and `HistoryDealSelect` tandem.

The group parameter allows sorting out deals by symbols. '*' can be used at the beginning and the end of a string.

The group parameter may contain several comma separated conditions. A condition can be set as a mask using '*'. The logical negation symbol '!' can be used for an exclusion. All conditions are applied sequentially, which means conditions of including to a group should be specified first followed by an exclusion condition. For example, group="*, !EUR" means that deals for all symbols should be selected first and the ones containing "EUR" in symbol names should be excluded afterwards.

## Example:

```python
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', 500) # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
print()
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# get the number of deals in history
from_date=datetime(2020,1,1)
to_date=datetime.now()
# get deals for symbols whose names contain "GBP" within a specified interval
deals=mt5.history_deals_get(from_date, to_date, group="*GBP*")
if deals==None:
    print("No deals with group=\"*USD*\", error code={}".format(mt5.last_error()))
elif len(deals)> 0:
    print("history_deals_get({}, {}, group=\"*GBP*\")={}".format(from_date,to_date,len(deals)))
 
# get deals for symbols whose names contain neither "EUR" nor "GBP"
deals = mt5.history_deals_get(from_date, to_date, group="*,!*EUR*,!*GBP*")
if deals == None:
    print("No deals, error code={}".format(mt5.last_error()))
elif len(deals) > 0:
    print("history_deals_get(from_date, to_date, group=\"*,!*EUR*,!*GBP*\") =", len(deals))
    # display all obtained deals 'as is'
    for deal in deals:
        print("  ",deal)
    print()
    # display these deals as a table using pandas.DataFrame
    df=pd.DataFrame(list(deals),columns=deals[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    print(df)
print("")
 
# get all deals related to the position #530218319
position_id=530218319
position_deals = mt5.history_deals_get(position=position_id)
if position_deals == None:
    print("No deals with position #{}".format(position_id))
    print("error code =", mt5.last_error())
elif len(position_deals) > 0:
    print("Deals with position id #{}: {}".format(position_id, len(position_deals)))
    # display these deals as a table using pandas.DataFrame
    df=pd.DataFrame(list(position_deals),columns=position_deals[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    print(df)
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
```

## Result:

```
MetaTrader5 package author:  MetaQuotes Software Corp.
MetaTrader5 package version:  5.0.29
 
history_deals_get(from_date, to_date, group="*GBP*") = 14
 
history_deals_get(from_date, to_date, group="*,!*EUR*,!*GBP*") = 7
   TradeDeal(ticket=506966741, order=0, time=1582202125, time_msc=1582202125419, type=2, entry=0, magic=0, position_id=0, reason=0, volume=0.0, pri ...
   TradeDeal(ticket=507962919, order=530218319, time=1582303777, time_msc=1582303777582, type=0, entry=0, magic=0, position_id=530218319, reason=0, ...
   TradeDeal(ticket=513149059, order=535548147, time=1583176242, time_msc=1583176242265, type=1, entry=1, magic=0, position_id=530218319, reason=0, ...
   TradeDeal(ticket=516943494, order=539349382, time=1583510003, time_msc=1583510003895, type=1, entry=0, magic=0, position_id=539349382, reason=0, ...
   TradeDeal(ticket=516943915, order=539349802, time=1583510025, time_msc=1583510025054, type=0, entry=0, magic=0, position_id=539349802, reason=0, ...
   TradeDeal(ticket=517139682, order=539557870, time=1583520201, time_msc=1583520201227, type=0, entry=1, magic=0, position_id=539349382, reason=0, ...
   TradeDeal(ticket=517139716, order=539557909, time=1583520202, time_msc=1583520202971, type=1, entry=1, magic=0, position_id=539349802, reason=0, ...
 
      ticket      order                time       time_msc  type  entry  magic  position_id  reason  volume    price  commission  swap     profit  fee  symbol comment external_id
0  506966741          0 2020-02-20 12:35:25  1582202125419     2      0      0            0       0    0.00  0.00000         0.0   0.0  100000.00  0.0                            
1  507962919  530218319 2020-02-21 16:49:37  1582303777582     0      0      0    530218319       0    0.01  0.97898         0.0   0.0       0.00  0.0  USDCHF                    
2  513149059  535548147 2020-03-02 19:10:42  1583176242265     1      1      0    530218319       0    0.01  0.95758         0.0   0.0     -22.35  0.0  USDCHF                    
3  516943494  539349382 2020-03-06 15:53:23  1583510003895     1      0      0    539349382       0    0.10  0.93475         0.0   0.0       0.00  0.0  USDCHF                    
4  516943915  539349802 2020-03-06 15:53:45  1583510025054     0      0      0    539349802       0    0.10  0.66336         0.0   0.0       0.00  0.0  AUDUSD                    
5  517139682  539557870 2020-03-06 18:43:21  1583520201227     0      1      0    539349382       0    0.10  0.93751         0.0   0.0     -29.44  0.0  USDCHF                    
6  517139716  539557909 2020-03-06 18:43:22  1583520202971     1      1      0    539349802       0    0.10  0.66327         0.0   0.0      -0.90  0.0  AUDUSD                    
 
Deals with position id #530218319: 2
      ticket      order                time       time_msc  type  entry  magic  position_id  reason  volume    price  commission  swap  profit  fee  symbol comment external_id
0  507962919  530218319 2020-02-21 16:49:37  1582303777582     0      0      0    530218319       0    0.01  0.97898         0.0   0.0    0.00  0.0  USDCHF                    
1  513149059  535548147 2020-03-02 19:10:42  1583176242265     1      1      0    530218319       0    0.01  0.95758         0.0   0.0  -22.35  0.0  USDCHF   
```

## See also

    `history_deals_total`, `history_orders_get`
        '''
        code=f'mt5.history_deals_get(*{args},**{kwargs})'
        response = self.__conn.eval(code)
        return response

    def eval(self,command:str):
        return self.__conn.eval(command)
    
    def execute(self,command:str):
        self.__conn.execute(command)

def __generate_server_classic(fname):
    code = r'''#!/usr/bin/env python

# Code from: https://github.com/tomerfiliba-org/rpyc
    
"""
classic rpyc server (threaded, forking or std) running a SlaveService
usage:
    rpyc_classic.py                         # default settings
    rpyc_classic.py -m forking -p 12345     # custom settings

    # ssl-authenticated server (keyfile and certfile are required)
    rpyc_classic.py --ssl-keyfile keyfile.pem --ssl-certfile certfile.pem --ssl-cafile cafile.pem
"""
import sys
import os
import rpyc
from plumbum import cli
from rpyc.utils.server import ThreadedServer, ForkingServer, OneShotServer
from rpyc.utils.classic import DEFAULT_SERVER_PORT, DEFAULT_SERVER_SSL_PORT
from rpyc.utils.registry import REGISTRY_PORT
from rpyc.utils.registry import UDPRegistryClient, TCPRegistryClient
from rpyc.utils.authenticators import SSLAuthenticator
from rpyc.lib import setup_logger
from rpyc.core import SlaveService


class ClassicServer(cli.Application):
    mode = cli.SwitchAttr(["-m", "--mode"], cli.Set("threaded", "forking", "stdio", "oneshot"),
                          default="threaded", help="The serving mode (threaded, forking, or 'stdio' for "
                          "inetd, etc.)")

    port = cli.SwitchAttr(["-p", "--port"], cli.Range(0, 65535), default=None,
                          help="The TCP listener port ("
                               "default = {DEFAULT_SERVER_PORT!r}, "
                               "default for SSL = {DEFAULT_SERVER_SSL_PORT!r})",
                          group="Socket Options")
    host = cli.SwitchAttr(["--host"], str, default="", help="The host to bind to. "
                          "The default is localhost", group="Socket Options")
    ipv6 = cli.Flag(["--ipv6"], help="Enable IPv6", group="Socket Options")

    logfile = cli.SwitchAttr("--logfile", str, default=None, help="Specify the log file to use; "
                             "the default is stderr", group="Logging")
    quiet = cli.Flag(["-q", "--quiet"], help="Quiet mode (only errors will be logged)",
                     group="Logging")

    ssl_keyfile = cli.SwitchAttr("--ssl-keyfile", cli.ExistingFile,
                                 help="The keyfile to use for SSL. Required for SSL", group="SSL",
                                 requires=["--ssl-certfile"])
    ssl_certfile = cli.SwitchAttr("--ssl-certfile", cli.ExistingFile,
                                  help="The certificate file to use for SSL. Required for SSL", group="SSL",
                                  requires=["--ssl-keyfile"])
    ssl_cafile = cli.SwitchAttr("--ssl-cafile", cli.ExistingFile,
                                help="The certificate authority chain file to use for SSL. "
                                "Optional; enables client-side authentication",
                                group="SSL", requires=["--ssl-keyfile"])

    auto_register = cli.Flag("--register", help="Asks the server to attempt registering with "
                             "a registry server. By default, the server will not attempt to register",
                             group="Registry")
    registry_type = cli.SwitchAttr("--registry-type", cli.Set("UDP", "TCP"),
                                   default="UDP", help="Specify a UDP or TCP registry", group="Registry")
    registry_port = cli.SwitchAttr("--registry-port", cli.Range(0, 65535), default=REGISTRY_PORT,
                                   help="The registry's UDP/TCP port", group="Registry")
    registry_host = cli.SwitchAttr("--registry-host", str, default=None,
                                   help="The registry host machine. For UDP, the default is 255.255.255.255; "
                                   "for TCP, a value is required", group="Registry")

    def main(self):
        if not self.host:
            self.host = "::1" if self.ipv6 else "127.0.0.1"

        if self.registry_type == "UDP":
            if self.registry_host is None:
                self.registry_host = "255.255.255.255"
            self.registrar = UDPRegistryClient(ip=self.registry_host, port=self.registry_port)
        else:
            if self.registry_host is None:
                raise ValueError("With TCP registry, you must specify --registry-host")
            self.registrar = TCPRegistryClient(ip=self.registry_host, port=self.registry_port)

        if self.ssl_keyfile:
            self.authenticator = SSLAuthenticator(self.ssl_keyfile, self.ssl_certfile,
                                                  self.ssl_cafile)
            default_port = DEFAULT_SERVER_SSL_PORT
        else:
            self.authenticator = None
            default_port = DEFAULT_SERVER_PORT
        if self.port is None:
            self.port = default_port

        setup_logger(self.quiet, self.logfile)

        if self.mode == "threaded":
            self._serve_mode(ThreadedServer)
        elif self.mode == "forking":
            self._serve_mode(ForkingServer)
        elif self.mode == "oneshot":
            self._serve_oneshot()
        elif self.mode == "stdio":
            self._serve_stdio()

    def _serve_mode(self, factory):
        t = factory(SlaveService, hostname=self.host, port=self.port,
                    reuse_addr=True, ipv6=self.ipv6, authenticator=self.authenticator,
                    registrar=self.registrar, auto_register=self.auto_register)
        t.start()

    def _serve_oneshot(self):
        t = OneShotServer(SlaveService, hostname=self.host, port=self.port,
                          reuse_addr=True, ipv6=self.ipv6, authenticator=self.authenticator,
                          registrar=self.registrar, auto_register=self.auto_register)
        t._listen()
        sys.stdout.write("rpyc-oneshot\n")
        sys.stdout.write(f"{t.host}\t{t.port}\n")
        sys.stdout.flush()
        t.start()

    def _serve_stdio(self):
        origstdin = sys.stdin
        origstdout = sys.stdout
        sys.stdin = open(os.devnull, "r")
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
        conn = rpyc.classic.connect_pipes(origstdin, origstdout)
        try:
            try:
                conn.serve_all()
            except KeyboardInterrupt:
                print("User interrupt!")
        finally:
            conn.close()


if __name__ == "__main__":
    ClassicServer.run()
'''
    with open(fname,'w') as fp:
        fp.write(code)

def main():
    from rpyc.utils.classic import DEFAULT_SERVER_PORT, DEFAULT_SERVER_SSL_PORT
    import os
    from subprocess import Popen
    import argparse
    parser = argparse.ArgumentParser(description='Create Server.')
    parser.add_argument('python', type=str, help='Python that will run the server (must be a windows installation)')
    parser.add_argument('--host', type=str, default='localhost', help='The host to bind to. The default is localhost')
    parser.add_argument('-p','--port', type=int, default=18812, help='The TCP listener port (default = {DEFAULT_SERVER_PORT!r}, default for SSL = {DEFAULT_SERVER_SSL_PORT!r})')
    parser.add_argument('-w','--wine', type=str, default='wine', help='Command line to call wine program (default = wine)')
    parser.add_argument('-s','--server', type=str, default='/tmp/mt5linux', help='Path where server will be build')
    args = parser.parse_args()
    #
    wine_cmd=args.wine
    win_python_path=args.python
    server_dir=args.server
    server_code='server.py'
    port=args.port
    host=args.host
    #
    Popen(['mkdir','-p',server_dir]).wait()
    __generate_server_classic(os.path.join(server_dir,server_code))
    Popen([
            wine_cmd,
            os.path.join(win_python_path),
            os.path.join(server_dir,server_code),
            '--host',
            host,
            '-p',
            str(port),
        ],
    ).wait()


if __name__ == '__main__':
    main()