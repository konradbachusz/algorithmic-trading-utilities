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
print  (data['lastUpdateId'])
print(data.keys())