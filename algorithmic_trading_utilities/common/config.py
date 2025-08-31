"""
Configuration module.

This module contains configuration variables and Alpaca API setup.
It includes API keys, trading thresholds, and other environment-specific settings.
"""

# TODO get specific method instead of *
from alpaca.trading.client import *
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

## DEV ##

api_key = os.environ["PAPER_KEY"]
secret_key = os.environ["PAPER_SECRET"]

#### We use paper environment for this example ####
paper = True  # Please do not modify this. This example is for paper trading only.
####

# Below are the variables for development this documents
# Please do not change these variables
trade_api_wss = None
data_api_url = None
stream_data_wss = None

# Ensure loss_threshold is defined at the top level for proper import
loss_threshold = 0.05  # Set loss threshold for closing positions to 5%
trailing_stop_loss_threshold = 0.1  # Set trailing stop loss threshold to 10%
# TODO add remaining variables

# setup clients
trading_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)


# LLM Model configuration
model="gemma3:1b"
ollama_url="http://localhost:11434/api/generate"
## PROD ##
#TODO