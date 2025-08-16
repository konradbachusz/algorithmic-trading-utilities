import sys
sys.path.insert(1, "algorithmic_trading_utilities")
import numpy as np
from alpaca_trade_api.rest import REST
import os
from dotenv import load_dotenv
from datetime import date
from yfinance import download
from data.yfinance_ops import get_sp500_prices
import pandas as pd
from common.viz_ops import compare_portfolio_and_benchmark

# Load environment variables from .env file
load_dotenv()

# Initialize Alpaca API
api = REST(
    os.environ["PAPER_KEY"],
    os.environ["PAPER_SECRET"],
    base_url="https://paper-api.alpaca.markets",
)


def get_portfolio_history():
    """
    Retrieve portfolio history from Alpaca API.

    Returns:
        object: Portfolio history object containing equity data.
    """
    return api.get_portfolio_history(
        timeframe="1D", date_start="2025-04-08", date_end=date.today().isoformat()
    )