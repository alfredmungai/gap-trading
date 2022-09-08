import datetime
import pandas as pd

import os
import sys

import config

from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

# Get API keys
api = REST(key_id = config.API_KEY, secret_key = config.SECRET_KEY, base_url = config.ENDPOINT)

# Check to see if market is open
# if not api.get_clock().is_open:
#     sys.exit("Market is closed")

# Create a dataframe of positions between 2 dates
bars = api.get_bars(config.QQQ_SYMBOLS, TimeFrame.Day, config.START_DATE, config.TODAY).df

# Get previous close
bars['previous_close'] = bars.groupby('symbol')['close'].shift(1)

# Calculate moving average
bars['mv_avg'] = bars.groupby('symbol')['previous_close'].transform(lambda x: x.rolling(20, 20).mean())
bars.dropna(inplace=True)
bars['gain'] = bars.open / bars.previous_close - 1
gapdowns = bars.query(f'gain <= - {config.THRESHOLD}').copy()
# print(config.START_DATE,"\n", config.TODAY)

market_order_symbols = list(set(gapdowns.query('gain <= - 0.015').symbol))
bracket_order_symbols = gapdowns.query('gain > -0.015').symbol.to_list()

for symbol in market_order_symbols:
    open_price = gapdowns.query(f'symbol == "{symbol}"').open.iloc[-1]
    quantity = config.ORDER_DOLLAR_SIZE // open_price
    print(f'{datetime.datetime.now()} shorting {quantity} of {symbol} at {open_price}')

    try:
        order = api.submit_order(symbol, quantity, 'sell', 'market')
        print(f'successfully submitted market order with order_id {order.id}')
    except Exception as e:
        print(f'Error submitting above order {e}')
