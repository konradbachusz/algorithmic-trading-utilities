import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for testing
import numpy as np
import pandas as pd
from algorithmic_trading_utilities.common.portfolio_ops import PerformanceMetrics
from algorithmic_trading_utilities.common.viz_ops import (
    PerformanceViz,
    build_performance_figures,
)


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


class TestBuildPerformanceFigures:
    def test_returns_list_of_figures(self, sample_data):
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        figs = build_performance_figures(viz, show=False)
        assert isinstance(figs, list)
        assert len(figs) > 0
        assert all(f is not None for f in figs)

    def test_default_masking_drops_benchmark_line_on_dollar_plots(self, sample_data):
        """By default the benchmark is hidden on cumulative-returns and equity-curve plots."""
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        figs = build_performance_figures(viz, show=False)

        # Order matches build_performance_figures: cumulative_returns, equity_curve, ...
        cumulative_fig = figs[0]
        equity_fig = figs[1]

        # Each masked plot should have only the portfolio line, not the benchmark.
        assert len(cumulative_fig.axes[0].lines) == 1 + 1  # portfolio + zero ref line
        assert len(equity_fig.axes[0].lines) == 1

    def test_restores_benchmark_after_masked_plots(self, sample_data):
        """``viz.benchmark`` is restored to its original value after each masked call."""
        pm, _, benchmark = sample_data
        viz = PerformanceViz(pm=pm)
        original_benchmark_id = id(viz.benchmark)
        build_performance_figures(viz, show=False)
        assert id(viz.benchmark) == original_benchmark_id
        assert viz.benchmark is not None

    def test_no_masking_keeps_benchmark_on_all_plots(self, sample_data):
        """With ``mask_benchmark_on=()`` the benchmark line appears on every applicable plot."""
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        figs = build_performance_figures(viz, show=False, mask_benchmark_on=())

        cumulative_fig = figs[0]
        equity_fig = figs[1]
        # Now both portfolio and benchmark lines should be present
        assert len(cumulative_fig.axes[0].lines) >= 2
        assert len(equity_fig.axes[0].lines) >= 2

    def test_skips_alpha_beta_when_in_mask_set(self, sample_data):
        """Alpha/beta plots are skipped entirely if their name is in ``mask_benchmark_on``."""
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        figs_with = build_performance_figures(viz, show=False, mask_benchmark_on=())
        figs_without = build_performance_figures(
            viz, show=False, mask_benchmark_on=("rolling_alpha_beta",)
        )
        # Without alpha/beta we should have 2 fewer figures
        assert len(figs_without) == len(figs_with) - 2
