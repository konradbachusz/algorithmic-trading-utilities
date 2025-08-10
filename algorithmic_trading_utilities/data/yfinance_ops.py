import pandas as pd
import yfinance
# TODO unit test and move to yfinance_ops.py

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