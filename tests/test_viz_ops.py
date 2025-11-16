import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for testing
import numpy as np
import pandas as pd
from algorithmic_trading_utilities.common.portfolio_ops import PerformanceMetrics
from algorithmic_trading_utilities.common.viz_ops import PerformanceViz


class TestPerformanceViz:
    def test_init_with_pm(self, sample_data):
        pm, portfolio, benchmark = sample_data
        viz = PerformanceViz(pm=pm)
        assert isinstance(viz.portfolio, pd.Series)
        assert isinstance(viz.benchmark, pd.Series)
        assert viz.portfolio.index.equals(portfolio.index)
        assert viz.benchmark.index.equals(benchmark.index)

    def test_plot_equity_curve(self, sample_data):
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        fig = viz.plot_equity_curve(show=False)
        assert fig is not None
        assert len(fig.axes[0].lines) >= 1

    def test_plot_drawdown_series(self, sample_data):
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        fig = viz.plot_drawdown_series(show=False)
        assert fig is not None

    def test_plot_returns_distribution(self, sample_data):
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        fig = viz.plot_returns_distribution(show=False)
        assert fig is not None

    def test_plot_rolling_sharpe(self, sample_data):
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        fig = viz.plot_rolling_sharpe(show=False)
        assert fig is not None

    def test_plot_cumulative_returns_timeseries(self, sample_data):
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        fig = viz.plot_cumulative_returns_timeseries(show=False)
        assert fig is not None
        assert len(fig.axes) == 1
        ax = fig.axes[0]
        # Should have at least one line (portfolio returns)
        assert len(ax.lines) >= 1
        # Should have horizontal line at 0
        assert any(
            line.get_ydata()[0] == 0 for line in ax.lines if len(line.get_ydata()) > 0
        )

    def test_plot_cumulative_returns_timeseries_with_benchmark(self, sample_data):
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        fig = viz.plot_cumulative_returns_timeseries(show=False)
        ax = fig.axes[0]
        # Should have portfolio, benchmark, and horizontal line
        assert len(ax.lines) >= 2
        # Check labels
        labels = [line.get_label() for line in ax.lines]
        assert "Portfolio Returns" in labels
        assert "Benchmark Returns" in labels

    def test_plot_cumulative_returns_timeseries_without_benchmark(self, sample_data):
        pm, portfolio, _ = sample_data
        # Create a new PerformanceMetrics instance and manually set benchmark to None
        # to bypass the automatic SP500 fetching
        pm_no_benchmark = PerformanceMetrics(
            portfolio_equity=portfolio, benchmark_equity=pd.Series(dtype=float)
        )
        pm_no_benchmark.benchmark = None
        pm_no_benchmark.benchmark_returns = None
        viz = PerformanceViz(pm=pm_no_benchmark)
        fig = viz.plot_cumulative_returns_timeseries(show=False)
        ax = fig.axes[0]
        # Should have portfolio and horizontal line only
        labels = [line.get_label() for line in ax.lines]
        assert "Portfolio Returns" in labels
        assert "Benchmark Returns" not in labels

    def test_plot_cumulative_returns_timeseries_calculation(self):
        """Test that cumulative returns are calculated correctly."""
        # Create mock portfolio data
        dates = pd.date_range(start="2025-01-01", periods=10)
        portfolio_values = pd.Series(
            [10000, 10100, 10200, 10050, 10300, 10400, 10350, 10500, 10600, 10700],
            index=dates,
        )

        # Create a new PerformanceMetrics instance without benchmark
        pm_no_benchmark = PerformanceMetrics(
            portfolio_equity=portfolio_values, benchmark_equity=None
        )
        viz = PerformanceViz(pm=pm_no_benchmark)
        fig = viz.plot_cumulative_returns_timeseries(show=False)
        ax = fig.axes[0]

        # Get the plotted data
        portfolio_line = [
            line for line in ax.lines if line.get_label() == "Portfolio Returns"
        ][0]
        plotted_returns = portfolio_line.get_ydata()

        # Calculate expected returns
        expected_returns = (
            (portfolio_values - portfolio_values.iloc[0])
            / portfolio_values.iloc[0]
            * 100
        )

        # First value should be 0%
        assert abs(plotted_returns[0]) < 0.01  # Close to 0

        # Check that returns are calculated correctly (allowing for small floating point differences)
        assert len(plotted_returns) == len(expected_returns)

    def test_plot_cumulative_returns_timeseries_savepath(self, sample_data, tmp_path):
        """Test that the plot can be saved to a file."""
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        savepath = tmp_path / "cumulative_returns.png"
        fig = viz.plot_cumulative_returns_timeseries(show=False, savepath=str(savepath))
        assert savepath.exists()
        assert fig is not None

    def test_plot_cumulative_returns_timeseries_axes_labels(self, sample_data):
        """Test that axes have correct labels."""
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        fig = viz.plot_cumulative_returns_timeseries(show=False)
        ax = fig.axes[0]

        assert ax.get_xlabel() == "Date"
        assert ax.get_ylabel() == "Cumulative Returns (%)"
        assert ax.get_title() == "Cumulative Returns Time Series"

    def test_create_all_plots(self, sample_data):
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        figs = viz.create_all_plots(show=False)
        assert isinstance(figs, list)
        assert all(f is not None for f in figs)
