import sys

sys.path.insert(1, "algorithmic_trading_utilities")
from alpaca_trade_api.rest import REST
import os
from dotenv import load_dotenv
from datetime import date


# Load environment variables from .env file
load_dotenv()

# TODO fix for real API keys
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
    # TODO: Ensure that it returns Portfolio Equity as pd.Series with pd.DatetimeIndex index.
    return api.get_portfolio_history(
        timeframe="1D", date_start="2025-04-08", date_end=date.today().isoformat()
    )
