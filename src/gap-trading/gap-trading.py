# Inspired by part time Larry @ https://github.com/hackingthemarkets/gap-trading
import datetime
import pandas as pd
import sys

import config

from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

# Get API keys
try:
    api = REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.ENDPOINT)

except:
    print("REST didn't work")

# Check to see if market is open
# if not api.get_clock().is_open:
#     sys.exit("Market is closed")

# Create a dataframe of positions between 2 dates
try:
    bars = api.get_bars(config.IWM_SYMBOLS, TimeFrame.Day, config.START_DATE, config.TODAY).df
except:
    print("get_bars didn't work")

# Get previous close
bars['previous_close'] = bars.groupby('symbol')['close'].shift(1)
bars.head()
# Calculate moving average
bars['mv_avg'] = bars.groupby('symbol')['previous_close'].transform(lambda x: x.rolling(20, 20).mean())
bars.dropna(inplace=True)
bars['gain'] = bars.open / bars.previous_close - 1
gapdowns = bars.query(f'gain <= - {config.THRESHOLD}').copy()
# print(config.START_DATE,"\n", config.TODAY)

market_order_symbols = list(set(gapdowns.query('gain <= - 0.015').symbol))
bracket_order_symbols = gapdowns.query('gain > -0.015').symbol.to_list()

quotes = api.get_latest_quotes(market_order_symbols)

for symbol in market_order_symbols:
    open_price = gapdowns.query(f'symbol == "{symbol}"').open.iloc[-1]
    quantity = config.ORDER_DOLLAR_SIZE // open_price
    print(f'{datetime.datetime.now()} shorting {quantity} of {symbol} at {open_price}')

    take_profit = round(quotes[symbol].bp * 0.99, 2)
    stop_price = round(quotes[symbol].bp * 1.01, 2)
    stop_limit_price = round(quotes[symbol].bp * 1.02, 2)

    try:
        order = api.submit_order(symbol, quantity, 'sell', 
                                    order_class='market') 
                                    

        print(f'successfully submitted a bracket order with order_id {order.id}')
    except Exception as e:
        print(f'Error submitting above order {e}')

    # try:
    #     order = api.submit_order(symbol, quantity, 'sell', 
    #                                 order_class='bracket', 
    #                                 take_profit={
    #                                     'limit_price': take_profit
    #                                 }, 
    #                                 stop_loss={
    #                                     'stop_price': stop_price, 
    #                                     'limit_price': stop_limit_price
    #                                 })

    #     print(f'successfully submitted a bracket order with order_id {order.id}')
    # except Exception as e:
    #     print(f'Error submitting above order {e}')
