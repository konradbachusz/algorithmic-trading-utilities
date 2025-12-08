import pandas as pd
import requests
import math
from decimal import Decimal

symbol = "BTCUSDT"
url = "https://api.binance.com/api/v3/depth"



params = {
    "symbol":symbol,
    "limit":5000,
}

data = requests.get(url, params).json()
print(data['bids'])
print  (data['asks'])


print(data.keys())

print("Highest Bid:", data['bids'][0])
print("Lowest Ask:", data['asks'][0])

#Create dataframes from data
bids_df = pd.DataFrame({
    'lastUpdateId': [data['lastUpdateId']] * len(data['bids']),
    'timestamp': [pd.Timestamp.now()] * len(data['bids']),
    'price': [float(bid[0]) for bid in data['bids']],
    'qty': [float(bid[1]) for bid in data['bids']]
})

asks_df = pd.DataFrame({
    'lastUpdateId': [data['lastUpdateId']] * len(data['asks']),
    'timestamp': [pd.Timestamp.now()] * len(data['asks']),
    'price': [float(ask[0]) for ask in data['asks']],
    'qty': [float(ask[1]) for ask in data['asks']]
})

print("Bids DataFrame:")
print(bids_df)
print("\nAsks DataFrame:")
print(asks_df)

print("Max Bid Price:", bids_df['price'].max())
print("Min Ask Price:", asks_df['price'].min())