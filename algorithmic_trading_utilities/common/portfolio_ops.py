import sys

sys.path.insert(1, "algorithmic_trading_utilities")
import numpy as np
import pandas as pd

# Try different import approaches for data modules
try:
    from data.yfinance_ops import get_sp500_prices
except ImportError:
    from algorithmic_trading_utilities.data.yfinance_ops import get_sp500_prices


# Try different import approaches for broker modules
try:
    from brokers.alpaca.alpaca_ops import get_portfolio_history
except ImportError:
    from algorithmic_trading_utilities.brokers.alpaca.alpaca_ops import (
        get_portfolio_history,
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
        float: Total return percentage.
    """
    return round(((equity[-1] - equity[0]) / equity[0]) * 100, 2)


def get_cumulative_return(equity):
    """
    Calculate the cumulative return from equity data.

    Parameters:
        equity (list): List of daily equity values.

    Returns:
        float: Cumulative return percentage.
    """
    return round(((equity[-1] - equity[0]) / equity[0]) * 100, 2)


def get_std_dev(equity):
    """
    Calculate the standard deviation of returns from equity data.

    Parameters:
        equity (list): List of daily equity values.

    Returns:
        float: Standard deviation of returns.
    """
    returns = [
        (equity[i] - equity[i - 1]) / equity[i - 1] for i in range(1, len(equity))
    ]
    return np.std(returns)


def get_sharpe_ratio(average_return, std_dev, risk_free_rate=0.02 / 252):
    """
    Calculate the Sharpe ratio.

    Parameters:
        average_return (float): Average return.
        std_dev (float): Standard deviation of returns.
        risk_free_rate (float): Daily risk-free rate.

    Returns:
        float: Sharpe ratio.
    """
    return (average_return - risk_free_rate) / std_dev


def get_annualised_sharpe_ratio(sharpe_ratio):
    """
    Calculate the annualised Sharpe ratio.

    Parameters:
        sharpe_ratio (float): Sharpe ratio.

    Returns:
        float: Annualised Sharpe ratio.
    """
    return sharpe_ratio * (252**0.5)


def get_sortino_ratio(average_return, downside_deviation, risk_free_rate=0.02 / 252):
    """
    Calculate the Sortino ratio.

    Parameters:
        average_return (float): Average return.
        downside_deviation (float): Downside deviation of returns.
        risk_free_rate (float): Daily risk-free rate.

    Returns:
        float: Sortino ratio.
    """
    return (average_return - risk_free_rate) / downside_deviation


def get_annualised_sortino_ratio(sortino_ratio):
    """
    Calculate the annualised Sortino ratio.

    Parameters:
        sortino_ratio (float): Sortino ratio.

    Returns:
        float: Annualised Sortino ratio.
    """
    return sortino_ratio * (252**0.5)


def get_max_drawdown(equity):
    """
    Calculate the maximum drawdown from equity data.

    Parameters:
        equity (list): List of daily equity values.

    Returns:
        float: Maximum drawdown.
    """
    drawdowns = [
        (max(equity[: i + 1]) - equity[i]) / max(equity[: i + 1])
        for i in range(len(equity))
    ]
    return max(drawdowns)


def get_alpha(portfolio_returns, benchmark_returns, risk_free_rate=0.02 / 252):
    """
    Calculate the alpha of the portfolio.

    Parameters:
        portfolio_returns (list): List of portfolio daily returns.
        benchmark_returns (list): List of benchmark daily returns.
        risk_free_rate (float): Daily risk-free rate.

    Returns:
        float: Alpha value.
    """
    portfolio_excess = np.mean(portfolio_returns) - risk_free_rate
    benchmark_excess = np.mean(benchmark_returns) - risk_free_rate
    beta = np.cov(portfolio_returns, benchmark_returns)[0, 1] / np.var(
        benchmark_returns
    )
    return portfolio_excess - beta * benchmark_excess


def get_beta(portfolio_returns, benchmark_returns):
    """
    Calculate the beta of the portfolio.

    Parameters:
        portfolio_returns (list): List of portfolio daily returns.
        benchmark_returns (list): List of benchmark daily returns.

    Returns:
        float: Beta value.
    """
    return np.cov(portfolio_returns, benchmark_returns)[0, 1] / np.var(
        benchmark_returns
    )


# TODO unit test
def get_portfolio_and_benchmark_values():
    """
    Create a DataFrame with columns 'Benchmark' (S&P 500 prices) and 'Portfolio' (portfolio equity),
    aligned by date index (using the index from benchmark_df only).

    Returns:
        pd.DataFrame: DataFrame with 'Benchmark' and 'Portfolio' columns.
    """

    # Get S&P 500 prices and portfolio equity
    benchmark_df = get_sp500_prices("2025-04-08")
    # Defensive: handle empty or failed download from yfinance
    if benchmark_df is None or benchmark_df.empty:
        # Return empty DataFrame with correct columns and no rows
        return pd.DataFrame(columns=["Benchmark", "Portfolio"])

    portfolio_history = get_portfolio_history()
    equity = portfolio_history.equity

    # Use the only column in benchmark_df as Benchmark
    if isinstance(benchmark_df, pd.DataFrame) and benchmark_df.shape[1] == 1:
        benchmark_series = benchmark_df.iloc[:, 0]
    else:
        benchmark_series = benchmark_df.squeeze()
    benchmark_series.name = "Benchmark"

    # Align lengths: use the minimum length of benchmark and equity
    min_len = min(len(benchmark_series), len(equity))
    aligned_benchmark = benchmark_series.iloc[:min_len]
    aligned_equity = pd.Series(
        equity[:min_len], index=aligned_benchmark.index, name="Portfolio"
    )

    df = pd.DataFrame({"Benchmark": aligned_benchmark, "Portfolio": aligned_equity})

    return df


# TODO unit test
def get_portfolio_and_benchmark_returns():
    """
    Calculate the percentage change for both 'Benchmark' and 'Portfolio' columns
    using the formula: (Ending Price - Beginning Price) / Beginning Price * 100.

    Returns:
        pd.DataFrame: DataFrame with percentage changes, same index and columns.
    """
    df = get_portfolio_and_benchmark_values()
    pct_change_df = (df - df.iloc[0]) / df.iloc[0] * 100
    pct_change_df.columns = df.columns
    return pct_change_df


def calculate_performance_metrics():
    """
    Calculate all performance metrics and return them as a dictionary.

    Returns:
        dict: Dictionary containing all performance metrics.
    """
    portfolio_history = get_portfolio_history()
    equity = portfolio_history.equity

    average_return = get_average_return(equity)
    total_return = get_total_return(equity)
    cumulative_return = get_cumulative_return(equity)
    std_dev = get_std_dev(equity)
    sharpe_ratio = get_sharpe_ratio(average_return, std_dev)
    annual_sharpe_ratio = get_annualised_sharpe_ratio(sharpe_ratio)
    downside_returns = [
        r
        for r in [
            (equity[i] - equity[i - 1]) / equity[i - 1] for i in range(1, len(equity))
        ]
        if r < 0
    ]
    downside_deviation = np.std(downside_returns)
    sortino_ratio = get_sortino_ratio(average_return, downside_deviation)
    annual_sortino_ratio = get_annualised_sortino_ratio(sortino_ratio)
    max_drawdown = get_max_drawdown(equity)

    # Calculate daily returns for the S&P 500
    portfolio_vs_benchmark_df = get_portfolio_and_benchmark_returns()
    benchmark_returns = portfolio_vs_benchmark_df["Benchmark"]
    portfolio_returns = portfolio_vs_benchmark_df["Portfolio"]
    alpha = get_alpha(portfolio_returns, benchmark_returns)
    beta = get_beta(portfolio_returns, benchmark_returns)

    return {
        "average_return": average_return,
        "total_return": total_return,
        "cumulative_return": cumulative_return,
        "std_dev": std_dev,
        "sharpe_ratio": sharpe_ratio,
        "annual_sharpe_ratio": annual_sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "annual_sortino_ratio": annual_sortino_ratio,
        "max_drawdown": max_drawdown,
        "alpha": alpha,
        "beta": beta,
    }
