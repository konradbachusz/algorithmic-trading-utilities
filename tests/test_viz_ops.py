import pandas as pd
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

    def test_create_all_plots(self, sample_data):
        pm, _, _ = sample_data
        viz = PerformanceViz(pm=pm)
        figs = viz.create_all_plots(show=False)
        assert isinstance(figs, list)
        assert all(f is not None for f in figs)
