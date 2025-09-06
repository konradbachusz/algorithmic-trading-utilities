import math
import pytest
import sys

sys.path.insert(1, "algorithmic_trading_utilities")
import numpy as np
from algorithmic_trading_utilities.common.portfolio_ops import PerformanceMetrics


class TestPerformanceMetrics:
    def setup_method(self):
        # Sample portfolio and benchmark equity arrays
        self.portfolio_equity = np.array([100, 105, 110])
        self.benchmark_equity = np.array([200, 210, 220])
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
        assert round(result, 4) == pytest.approx(0.0012, rel=1e-2)

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
        assert isinstance(result, int)

    def test_return_distribution_stats(self):
        stats = self.pm.return_distribution_stats(alpha=0.05)
        assert "skewness" in stats
        assert "kurtosis" in stats
        assert "VaR" in stats
        assert "CVaR" in stats

    def test_alpha_beta(self):
        ab = self.pm.alpha_beta()
        assert "alpha" in ab
        assert "beta" in ab
        # Check types
        assert isinstance(ab["alpha"], float)
        assert isinstance(ab["beta"], float)

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

    def test_calculate_benchmark_metrics(self):
        bm_metrics = self.pm.calculate_benchmark_metrics()
        assert "alpha" in bm_metrics and bm_metrics["alpha"] == 0
        assert "beta" in bm_metrics and bm_metrics["beta"] == 1

    def test_report_runs(self):
        # Just ensure report() runs without error
        try:
            self.pm.report()
        except Exception as e:
            pytest.fail(f"report() raised an exception: {e}")
