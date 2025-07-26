import sys

sys.path.insert(1, "src")
import pandas as pd

pd.set_option("display.max_columns", None)
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from get_data import get_assets, get_historical_data, get_asset_df
from alpaca.data.requests import *
from alpaca.data.timeframe import *
from alpaca.trading.client import *
from alpaca.trading.stream import *
from alpaca.trading.requests import *
from alpaca.trading.enums import *
from yfinance_ops import get_stock_gainers_table
from orders import get_orders, get_orders_symbol_list
from positions import get_open_positions, get_positions_symbol_list


api_key = os.environ["PAPER_KEY"]
secret_key = os.environ["PAPER_SECRET"]

# setup clients
trading_client = TradingClient(
    api_key=api_key, secret_key=secret_key, paper=True, url_override=None
)


def is_in_strong_upward_trend(historical_data):
    """
    This function takes historical_data to detect if the asset has been in a strong upward trend since the last 2 weeks.

    Args:
        historical_data (pd.DataFrame): A pandas DataFrame containing the historical stock data for the specified symbol.

    Returns:
        bool: True if the asset has been in a strong upward trend since the last 2 weeks, False otherwise.

    """
    # Calculate the 14-day exponential moving average (EMA)
    ema = historical_data["close"].ewm(span=14, adjust=False).mean()

    # Calculate the 2-day EMA
    ema_short = historical_data["close"].ewm(span=2, adjust=False).mean()

    # Calculate the percentage change between the 2-day EMA and the 14-day EMA
    percentage_change = (ema_short - ema) / ema * 100

    # Check if the percentage change is greater than 5%
    if percentage_change.iloc[-1] > 5:
        return True
    else:
        return False


def get_upward_trending_assets(asset_list, stock_historical_data_client):
    upward_trending_assets = []
    for asset in asset_list:
        print(asset)

        historical_data = get_historical_data(asset, stock_historical_data_client)

        # Check if dataframe is empty
        if len(historical_data) < 1:
            pass

        # Check if asset has been in a strong upward trend since the last 2 weeks
        elif is_in_strong_upward_trend(historical_data):
            upward_trending_assets.append(asset)
    return upward_trending_assets


def get_tradable_gainers(assets_df, gainers_df):
    """
    Filter and merge the Alpaca assets and y_finance gainers dataframes based on symbol and exchange.

    Args:
        assets_df (pd.DataFrame): Alpaca DataFrame containing asset information with columns 'symbol', 'name', and 'exchange'.
        gainers_df (pd.DataFrame): y_finance DataFrame containing gainer information with columns 'symbol', 'shortName', and 'exchange'.

    Returns:
        pd.DataFrame: Merged DataFrame with columns 'symbol', 'exchange', 'shortName', and 'name' for tradable gainers.
    """

    assets_df = assets_df[["symbol", "name", "exchange"]]
    gainers_df = gainers_df[["symbol", "shortName", "exchange"]]

    # Map y_finance exchange name to Alpaca name
    gainers_df["exchange"] = gainers_df["exchange"].replace("PNK", "OTC")
    gainers_df["exchange"] = gainers_df["exchange"].replace("NYQ", "NYSE")
    gainers_df["exchange"] = gainers_df["exchange"].replace("NCM", "NASDAQ")
    gainers_df["exchange"] = gainers_df["exchange"].replace("NGM", "NASDAQ")
    gainers_df["exchange"] = gainers_df["exchange"].replace("NMS", "NASDAQ")
    gainers_df["exchange"] = gainers_df["exchange"].replace("OQX", "OTC")

    tradable_gainers_df = pd.merge(
        assets_df, gainers_df, on=["symbol", "exchange"], how="inner"
    )
    tradable_gainers_df = tradable_gainers_df[
        ["symbol", "exchange", "shortName", "name"]
    ]

    return tradable_gainers_df


def get_momentum_trades_list(trading_client):
    """
    Generate a list of momentum trades based on tradable gainers available on Alpaca. It excludes live orders and positions.

    Parameters:
        trading_client (TradingClient): An instance of the TradingClient class.

    Returns:
        List[Dict]: A list of dictionaries representing the momentum trades to be executed. Each dictionary contains the following keys:
            - 'symbol': The symbol of the asset to trade.
            - 'notional': The amount of the asset to trade (None for market order).
            - 'side': The side of the order (BUY).
            - 'type': The type of order (MarketOrderRequest).
            - 'time_in_force': The time in force for the order (DAY).

    Example:
        trades_list = get_momentum_trades_list(trading_client)
        # Output:
        # [
        #     {
        #         'symbol': 'AAPL',
        #         'notional': None,
        #         'side': OrderSide.BUY,
        #         'type': 'MarketOrderRequest',
        #         'time_in_force': TimeInForce.DAY
        #     },
        #     {
        #         'symbol': 'GOOGL',
        #         'notional': None,
        #         'side': OrderSide.BUY,
        #         'type': 'MarketOrderRequest',
        #         'time_in_force': TimeInForce.DAY
        #     },
        #     ...
        # ]
    """

    # Get all assets
    assets = get_assets(trading_client)

    # Convert assets into a dataframe
    assets_df = get_asset_df(assets)

    # Get a dataframe of gainers
    gainers_df = get_stock_gainers_table()

    # Get a dataframe of gainers available on Alpaca
    tradable_gainers_df = get_tradable_gainers(assets_df, gainers_df)

    # Get live orders
    orders = get_orders()
    order_symbols = get_orders_symbol_list(orders)

    # Get live positions
    positions = get_open_positions()
    position_symbols = get_positions_symbol_list(positions)

    # Combine orders and positions list
    live_orders_and_positions = order_symbols + position_symbols

    # Exclude live orders and positions
    tradable_gainers_df = tradable_gainers_df[
        ~tradable_gainers_df["symbol"].isin(live_orders_and_positions)
    ]

    print(tradable_gainers_df)

    trades_list = []
    for index, row in tradable_gainers_df.iterrows():
        trades_list.append(
            {
                "symbol": row["symbol"],
                "notional": None,
                "side": OrderSide.BUY,
                "type": "TrailingStopLoss",
                "time_in_force": TimeInForce.DAY,
            }
        )
    return trades_list
