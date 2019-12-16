# IMPORTS
import pandas as pd
import numpy as np
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
import streamlit as st
import matplotlib.pyplot as plt

st.title("Bono's Lab")
### API
#Enter your own API-secret here
binance_api_key = 'KFgjwkzplHoZVVBBtbORvhTgdGpQWMY8P82EoxBhWoCncRvJDDWCeBlJZTrgCRZO'    #Enter your own API-key here
binance_api_secret = 'ftlXFPU0YUlB2v1Xx1vN9EbevZnMDjAUFZymjYAAi6EVWs3CZ88JUw5cuLxEbcvo' #Enter your own API-secret here

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
batch_size = 750
binance_client = Client(api_key=binance_api_key, api_secret=binance_api_secret)


### FUNCTIONS
def minutes_of_new_data(symbol, kline_size, data):
    if len(data) > 0:  old = parser.parse(data["timestamp"].iloc[-1])
    old = datetime.strptime('1 Jan 2019', '%d %b %Y')
    new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')
    return old, new

def get_all_binance(symbol, kline_size, save = False):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename): data_df = pd.read_csv(filename)
    else: data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df)
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    if oldest_point == datetime.strptime('1 Jan 2019', '%d %b %Y'): print('Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol))
    else: print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (delta_min, symbol, available_data, kline_size))
    klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else: data_df = data
    data_df.set_index('timestamp', inplace=True)
    if save: data_df.to_csv(filename)
    print('All caught up..!')
    return data_df


# In[19]:


# For Binance
products = binance_client.get_products()
binance_symbols = [x['symbol'] for x in products['data']]
a = st.sidebar.multiselect('Select your assets',binance_symbols)
d = dict()

for symbol in a:
    d[symbol] = get_all_binance(symbol, '1d', save = True)

for symbol in a:
	st.subheader(symbol)
	st.write(d[symbol])
	c = d[symbol]['close'].values.astype('float')[:1000]
	st.line_chart(pd.DataFrame(c, columns = ['close']))
	


