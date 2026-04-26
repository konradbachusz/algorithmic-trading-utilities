import math
import pytest
import sys
import pandas as pd

sys.path.insert(1, "algorithmic_trading_utilities")
from algorithmic_trading_utilities.common.portfolio_ops import (
    PerformanceMetrics,
    fetch_normalized_benchmark,
)
import numpy as np


class TestFetchNormalizedBenchmark:
    def test_normalises_to_portfolio_start_value(self, mocker):
        """Benchmark first value should equal portfolio first value after rescale."""
        portfolio = pd.Series(
            [10000.0, 10500.0, 10300.0, 10800.0],
            index=pd.to_datetime(
                ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-06"]
            ),
        )
        sp500 = pd.Series(
            [5000.0, 5050.0, 5025.0, 5100.0],
            index=pd.to_datetime(
                ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-06"]
            ),
        )
        mocker.patch(
            "algorithmic_trading_utilities.common.portfolio_ops.get_sp500_prices",
            return_value=sp500,
        )

        p_aligned, b_aligned = fetch_normalized_benchmark(portfolio, "2025-01-01")

        assert b_aligned.iloc[0] == pytest.approx(p_aligned.iloc[0])
        # Benchmark mid-point should reflect S&P's relative move (5050/5000 * 10000)
        assert b_aligned.iloc[1] == pytest.approx(10100.0)

    def test_intersects_to_common_dates_only(self, mocker):
        """Dates present in only one of the two series are dropped from both."""
        portfolio = pd.Series(
            [100.0, 101.0, 102.0],
            index=pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
        )
        # Benchmark missing 2025-01-02, has extra 2025-01-04
        sp500 = pd.Series(
            [50.0, 51.0, 52.0],
            index=pd.to_datetime(["2025-01-01", "2025-01-03", "2025-01-04"]),
        )
        mocker.patch(
            "algorithmic_trading_utilities.common.portfolio_ops.get_sp500_prices",
            return_value=sp500,
        )

        p_aligned, b_aligned = fetch_normalized_benchmark(portfolio, "2025-01-01")

        assert list(p_aligned.index) == list(
            pd.to_datetime(["2025-01-01", "2025-01-03"])
        )
        assert list(b_aligned.index) == list(p_aligned.index)

    def test_passes_date_start_to_get_sp500_prices(self, mocker):
        """The date_start argument is forwarded as-is to ``get_sp500_prices``."""
        portfolio = pd.Series(
            [100.0],
            index=pd.to_datetime(["2025-04-08"]),
        )
        mock = mocker.patch(
            "algorithmic_trading_utilities.common.portfolio_ops.get_sp500_prices",
            return_value=pd.Series([50.0], index=pd.to_datetime(["2025-04-08"])),
        )

        fetch_normalized_benchmark(portfolio, "2025-04-08")

        mock.assert_called_once_with("2025-04-08")


class TestPerformanceMetrics:
    def setup_method(self):
        # Sample portfolio and benchmark equity as pandas Series
        self.index = pd.DatetimeIndex(["2025-01-01", "2025-01-02", "2025-01-03"])
        self.portfolio_equity = pd.Series([100, 105, 110], index=self.index)
        self.benchmark_equity = pd.Series([200, 210, 220], index=self.index)
        self.pm = PerformanceMetrics(
            portfolio_equity=self.portfolio_equity,
            benchmark_equity=self.benchmark_equity,
            risk_free_rate=0.02 / 252,
        )

    def test_average_return(self):
        result = self.pm.average_return()
        assert round(result, 4) == pytest.approx(0.04878, abs=1e-4)

    def test_total_return(self):
        result = self.pm.total_return()
        assert round(result, 4) == pytest.approx(0.10, rel=1e-4)

    def test_std_dev(self):
        result = self.pm.std_dev()
        assert round(result, 4) == pytest.approx(0.0017, rel=1e-2)

    def test_sharpe_ratio(self):
        result = self.pm.sharpe_ratio()
        expected = (
            self.pm.average_return() - self.pm.risk_free_rate
        ) / self.pm.std_dev()
        assert round(result, 4) == pytest.approx(expected, rel=1e-2)

    def test_annualised_sharpe(self):
        result = self.pm.annualised_sharpe()
        expected = self.pm.sharpe_ratio() * np.sqrt(252)
        assert round(result, 4) == pytest.approx(expected, rel=1e-2)

    def test_sortino_ratio(self):
        result = self.pm.sortino_ratio()
        downside_std = self.pm.downside_std()
        expected = (
            (self.pm.average_return() - self.pm.risk_free_rate) / downside_std
            if downside_std
            else np.nan
        )
        if math.isnan(expected):
            assert math.isnan(result)
        else:
            assert result == pytest.approx(expected, rel=1e-2)

    def test_max_drawdown(self):
        result = self.pm.max_drawdown()
        cum_max = np.maximum.accumulate(self.portfolio_equity)
        expected = np.max((cum_max - self.portfolio_equity) / cum_max)
        assert round(result, 6) == round(expected, 6)

    def test_drawdown_duration(self):
        result = self.pm.drawdown_duration()
        assert result == 0

    def test_return_distribution_stats_contains_skewness(self):
        stats = self.pm.return_distribution_stats(alpha=0.05)
        assert "skewness" in stats

    def test_return_distribution_stats_contains_kurtosis(self):
        stats = self.pm.return_distribution_stats(alpha=0.05)
        assert "kurtosis" in stats

    def test_return_distribution_stats_contains_VaR(self):
        stats = self.pm.return_distribution_stats(alpha=0.05)
        assert "VaR" in stats

    def test_return_distribution_stats_contains_CVaR(self):
        stats = self.pm.return_distribution_stats(alpha=0.05)
        assert "CVaR" in stats

    def test_alpha_beta_contains_alpha(self):
        ab = self.pm.alpha_beta()
        assert "alpha" in ab

    def test_alpha_beta_contains_beta(self):
        ab = self.pm.alpha_beta()
        assert "beta" in ab

    def test_alpha_beta_values_are_float(self):
        ab = self.pm.alpha_beta()
        assert isinstance(ab["alpha"], float)
        assert isinstance(ab["beta"], float)

    def test_calculate_benchmark_metrics_alpha(self):
        bm_metrics = self.pm.calculate_benchmark_metrics()
        assert bm_metrics["alpha"] == 0

    def test_calculate_benchmark_metrics_beta(self):
        bm_metrics = self.pm.calculate_benchmark_metrics()
        assert bm_metrics["beta"] == 1

    def test_calculate_all(self):
        metrics = self.pm.calculate_all()
        keys_expected = [
            "average_return",
            "total_return",
            "std_dev",
            "sharpe_ratio",
            "annualised_sharpe",
            "sortino_ratio",
            "annualised_sortino",
            "max_drawdown",
            "average_drawdown",
            "drawdown_duration",
            "skewness",
            "kurtosis",
            "VaR_5%",
            "CVaR_5%",
            "calmar_ratio",
            "alpha",
            "beta",
        ]
        for key in keys_expected:
            assert key in metrics

    def test_report_runs(self):
        # Just ensure report() runs without error
        try:
            self.pm.report()
        except Exception as e:
            pytest.fail(f"report() raised an exception: {e}")
