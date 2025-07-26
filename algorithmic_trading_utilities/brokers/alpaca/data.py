"""
Alpaca data operations module.

This module provides functions to retrieve historical and real-time market data
through the Alpaca API.
"""

from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize data client
data_client = StockHistoricalDataClient(
    api_key=os.environ["PAPER_KEY"], secret_key=os.environ["PAPER_SECRET"]
)


def get_historical_bars(symbol, start_date=None, end_date=None, timeframe="1Day"):
    """
    Get historical bar data for a symbol.

    Parameters:
        symbol (str): Stock symbol
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        timeframe (str): Bar timeframe (e.g., "1Day", "1Hour")

    Returns:
        pd.DataFrame: Historical bar data
    """
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    request = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Day if timeframe == "1Day" else TimeFrame.Hour,
        start=start_date,
        end=end_date,
    )

    bars = data_client.get_stock_bars(request)
    return bars.df


def get_sp500_prices():
    """
    Get S&P 500 index prices for benchmark comparison.

    Returns:
        pd.DataFrame: S&P 500 price data
    """
    try:
        return get_historical_bars("SPY")
    except Exception as e:
        print(f"Error fetching S&P 500 data: {e}")
        return None
