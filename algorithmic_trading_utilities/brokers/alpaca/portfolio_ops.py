"""
Alpaca portfolio operations and performance analytics.

This module provides functions to calculate portfolio performance metrics,
compare against benchmarks, and analyze portfolio health.
"""
import sys
sys.path.insert(1, "algorithmic_trading_utilities")
import numpy as np
from alpaca_trade_api.rest import REST
import os
from dotenv import load_dotenv
from datetime import date
import pandas as pd
# Try different import approaches for yfinance_ops module
try:
    from data.yfinance_ops import get_sp500_prices
except ImportError:
    from algorithmic_trading_utilities.data.yfinance_ops import get_sp500_prices

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


def get_average_return(equity):
    """
    Calculate the average return from equity data.

    Parameters:
        equity (list): List of daily equity values.

    Returns:
        float: Average return.
    """
    returns = [
        (equity[i] - equity[i - 1]) / equity[i - 1] for i in range(1, len(equity))
    ]
    return np.mean(returns)


def get_total_return(equity):
    """
    Calculate the total return from equity data.

    Parameters:
        equity (list): List of daily equity values.

    Returns:
        float: Total return as a percentage.
    """
    if len(equity) < 2:
        return 0.0
    return ((equity[-1] - equity[0]) / equity[0]) * 100


def calculate_performance_metrics():
    """
    Calculate comprehensive portfolio performance metrics.

    Returns:
        dict: Dictionary containing various performance metrics including:
            - Total return
            - Average return
            - Sharpe ratio
            - Max drawdown
            - Other risk metrics
    """
    portfolio_history = get_portfolio_history()
    equity = portfolio_history.equity

    if not equity or len(equity) < 2:
        return {
            "total_return": 0.0,
            "average_return": 0.0,
            "annual_sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
        }

    total_return = get_total_return(equity)
    avg_return = get_average_return(equity)

    # Calculate returns for Sharpe ratio
    returns = [
        (equity[i] - equity[i - 1]) / equity[i - 1] for i in range(1, len(equity))
    ]

    # Sharpe ratio calculation
    if len(returns) > 0:
        std_dev = np.std(returns)
        sharpe_ratio = (avg_return / std_dev) * np.sqrt(252) if std_dev > 0 else 0.0
    else:
        sharpe_ratio = 0.0

    # Max drawdown calculation
    max_drawdown = 0.0
    peak = equity[0]
    for value in equity:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return {
        "total_return": total_return,
        "average_return": avg_return,
        "annual_sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown * 100,  # Convert to percentage
    }


def get_portfolio_and_benchmark_returns():
    """
    Compare portfolio returns vs S&P 500 benchmark.

    Returns:
        pd.DataFrame: DataFrame with portfolio and benchmark returns
    """
    portfolio_history = get_portfolio_history()

    # Convert to DataFrame for easy manipulation
    portfolio_df = pd.DataFrame(
        {
            "date": portfolio_history.timestamp,
            "portfolio_value": portfolio_history.equity,
        }
    )

    # Calculate portfolio returns
    portfolio_df["portfolio_return"] = portfolio_df["portfolio_value"].pct_change()

    # Get S&P 500 data for comparison
    sp500_data = get_sp500_prices("2025-04-08")

    print("\n get_sp500_prices executed")

    print("S&P 500 Data:")
    print(sp500_data)

    # Merge data if available
    if sp500_data is not None:
        comparison_df = pd.merge(portfolio_df, sp500_data, on="date", how="inner")
        return comparison_df
    else:
        return portfolio_df

#TODO remove
print(get_portfolio_and_benchmark_returns())