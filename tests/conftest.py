# TODO include variables like dummy emails etc
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_data():
    try:
        from algorithmic_trading_utilities.common.portfolio_ops import PerformanceMetrics
    except Exception as exc:
        pytest.skip(f"PerformanceMetrics unavailable: {exc}")

    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", periods=252)
    portfolio_returns = np.random.normal(0.0005, 0.01, len(dates))
    portfolio_equity = pd.Series(10000 * np.cumprod(1 + portfolio_returns), index=dates)

    benchmark_returns = np.random.normal(0.0003, 0.008, len(dates))
    benchmark_equity = pd.Series(10000 * np.cumprod(1 + benchmark_returns), index=dates)

    pm = PerformanceMetrics(portfolio_equity, benchmark_equity)
    return pm, portfolio_equity, benchmark_equity
