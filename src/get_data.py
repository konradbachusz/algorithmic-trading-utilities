# TODO import specific methods
from alpaca.data.live.stock import *
from alpaca.data.historical.stock import *
from alpaca.data.requests import *
from alpaca.data.timeframe import *
from alpaca.trading.client import *
from alpaca.trading.stream import *
from alpaca.trading.requests import *
from alpaca.trading.enums import *
from typing import List, Any, Tuple
import yfinance
from datetime import date


def get_assets(trading_client):
    """
    Get a list of active tradable assets.

    Parameters:
        trading_client (TradingClient): An instance of the TradingClient class.

    Returns:
        List[Asset]: A list of Asset objects representing the active tradable assets.

    """
    # ref. https://docs.alpaca.markets/reference/get-v2-assets-1
    req = GetAssetsRequest(status=AssetStatus.ACTIVE, tradable=True)
    assets = trading_client.get_all_assets(req)
    return assets


def get_asset_list(assets):
    """
    Get a list of active tradable assets.

    Parameters:
        trading_client (TradingClient): An instance of the TradingClient class.

    Returns:
        List[Asset]: A list of Asset objects representing the active tradable assets.

    """
    asset_list = []
    for asset in assets:
        try:
            asset_symbol = asset.symbol
        except AttributeError as e:
            asset_symbol = asset["symbol"]
        asset_list.append(asset_symbol)

    return asset_list


def get_asset_df(assets: List[Tuple[str, Any]]) -> pd.DataFrame:
    """
    Get a pandas DataFrame from a list of tuples representing assets.

    Parameters:
        assets (List[Tuple[str, Any]]): A list of tuples where each tuple contains a string representing the column name and any data type representing the column values.

    Returns:
        pd.DataFrame: A pandas DataFrame where each column is extracted from the first item of each tuple in the 'columns' column with error handling, and the values are extracted from the second item of each tuple in the respective column.

    """
    if not assets:
        return pd.DataFrame()

    assets_df = pd.DataFrame(assets)

    # Get the first item from each tuple in the 'columns' column.
    column_list = [assets_df[column][0][0] for column in assets_df.columns]

    # Get the 2nd item from each tuple to obtain the value
    assets_df = pd.DataFrame(
        [
            [assets_df[column][i][1] for column in assets_df.columns]
            for i in range(len(assets_df))
        ]
    )

    assets_df.columns = column_list

    return assets_df


def get_historical_data(symbol, stock_historical_data_client):
    """
    Get historical stock data for a specific symbol.

    Parameters:
        symbol (str): The symbol of the stock for which historical data is requested.
        stock_historical_data_client (StockHistoricalDataClient): An instance of the StockHistoricalDataClient class.

    Returns:
        DataFrame: A pandas DataFrame containing the historical stock data for the specified symbol.

    """
    # get historical bars by symbol
    # ref. https://docs.alpaca.markets/reference/stockbars-1
    now = datetime.now()
    req = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame(amount=1, unit=TimeFrameUnit.Day),
        start=now - timedelta(days=365),
        limit=365,  # Get data for the whole year
    )

    return stock_historical_data_client.get_stock_bars(req).df


def get_last_price(symbol, stock_historical_data_client):
    """
    Get the last close price of a stock symbol from historical data.

    Args:
        symbol (str): The stock symbol to retrieve the price for.
        stock_historical_data_client (Any): The client for accessing historical stock data.

    Returns:
        float: The last close price of the stock symbol.
    """
    # get historical bars by symbol
    # ref. https://docs.alpaca.markets/reference/stockbars-1
    now = datetime.now()
    req = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame(amount=1, unit=TimeFrameUnit.Day),
        start=now
        - timedelta(days=5),  # Get last few days in case of weekends and bank holidays
        limit=3,  # Limit to 3 last rows
    )

    last_prices_df = stock_historical_data_client.get_stock_bars(req).df

    if not last_prices_df.empty:
        last_close_price = last_prices_df.tail(1)["close"].values[0]
    else:
        last_close_price = None

    return last_close_price


# TODO unit test
def get_sp500_prices(start_date: str) -> pd.DataFrame:
    """
    Get S&P 500 prices since a specified start date until today using yfinance.

    Parameters:
        start_date (str): The start date in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the historical S&P 500 prices.
    """
    sp500_symbol = "^GSPC"  # S&P 500 index symbol in yfinance
    sp500_prices_df = yfinance.download(
        tickers=[sp500_symbol],
        start=start_date,
        end=date.today().isoformat(),
        interval="1d",
    )["Close"]
    return sp500_prices_df
