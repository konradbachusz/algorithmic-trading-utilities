# TODO include variables like dummy emails etc
import numpy as np
import pandas as pd
import pytest

from algorithmic_trading_utilities.common.portfolio_ops import PerformanceMetrics


@pytest.fixture
def sample_data():
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", periods=252)
    portfolio_returns = np.random.normal(0.0005, 0.01, len(dates))
    portfolio_equity = pd.Series(10000 * np.cumprod(1 + portfolio_returns), index=dates)

    benchmark_returns = np.random.normal(0.0003, 0.008, len(dates))
    benchmark_equity = pd.Series(10000 * np.cumprod(1 + benchmark_returns), index=dates)

    pm = PerformanceMetrics(portfolio_equity, benchmark_equity)
    return pm, portfolio_equity, benchmark_equity
