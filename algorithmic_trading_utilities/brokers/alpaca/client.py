"""
Alpaca client configuration and setup.

This module contains configuration variables and Alpaca API setup.
It includes API keys, trading thresholds, and other environment-specific settings.
"""

from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

## Configuration ##
api_key = os.environ["PAPER_KEY"]
secret_key = os.environ["PAPER_SECRET"]

#### We use paper environment for this example ####
paper = True  # Please do not modify this. This example is for paper trading only.

# Below are the variables for development this documents
# Please do not change these variables
trade_api_wss = None
data_api_url = None
stream_data_wss = None

# Risk management parameters
loss_threshold = 0.05  # Set loss threshold for closing positions to 5%
trailing_stop_loss_threshold = 0.1  # Set trailing stop loss threshold to 10%

# Setup clients
trading_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)


def get_trading_client():
    """
    Get the configured Alpaca trading client.

    Returns:
        TradingClient: Configured Alpaca trading client instance
    """
    return trading_client
