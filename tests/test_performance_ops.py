import json
import sys
from types import SimpleNamespace

import pandas as pd
import pytest

sys.path.insert(1, "algorithmic_trading_utilities")

from brokers.alpaca.performance_ops import (
    generate_performance_report,
    get_portfolio_equity_series,
    save_strategy_snapshot,
)


class TestSaveStrategySnapshot:

    def test_writes_snapshot_json(self, mocker, tmp_path):
        class RawEntity:
            def __init__(self, raw):
                self._raw = raw

        # Arrange
        mocker.patch(
            "brokers.alpaca.performance_ops.trading_client.get_all_positions",
            return_value=[{"symbol": "AAPL", "qty": "1"}],
        )

        mocker.patch(
            "brokers.alpaca.performance_ops.api.list_orders",
            return_value=[RawEntity({"id": "order1", "status": "new"})],
        )
        mocker.patch(
            "brokers.alpaca.performance_ops.get_activities",
            return_value=[RawEntity({"activity_type": "FILL", "symbol": "AAPL"})],
        )
        mocker.patch(
            "brokers.alpaca.performance_ops.get_balances",
            return_value={"cash": "100", "buying_power": "200"},
        )
        mock_get_ph = mocker.patch(
            "brokers.alpaca.performance_ops.api.get_portfolio_history",
            return_value={"equity": [100, 101]},
        )

        # Act
        out_path = save_strategy_snapshot(
            strategy_name="mean_reversion",
            output_dir=tmp_path,
            timeframe="1D",
            date_start="2025-01-01",
            date_end="2025-01-31",
        )

        # Assert
        assert out_path.exists()
        assert "mean_reversion_snapshot_" in out_path.name

        payload = json.loads(out_path.read_text(encoding="utf-8"))
        assert payload["strategy"] == "mean_reversion"
        assert "timestamp" in payload
        assert "positions" in payload
        assert "equity_performance" in payload
        assert "orders" in payload
        assert "activities" in payload
        assert "balances" in payload

        # Ensure orders/activities aren't empty dicts after serialization.
        assert payload["orders"][0]["id"] == "order1"
        assert payload["activities"][0]["activity_type"] == "FILL"

        mock_get_ph.assert_called_once_with(
            timeframe="1D", date_start="2025-01-01", date_end="2025-01-31"
        )

    def test_defaults_output_dir(self, mocker, tmp_path, monkeypatch):
        # Arrange: run in isolated cwd
        monkeypatch.chdir(tmp_path)

        mocker.patch(
            "brokers.alpaca.performance_ops.trading_client.get_all_positions",
            return_value=[],
        )
        mocker.patch("brokers.alpaca.performance_ops.api.list_orders", return_value=[])
        mocker.patch("brokers.alpaca.performance_ops.get_activities", return_value=[])
        mocker.patch("brokers.alpaca.performance_ops.get_balances", return_value={})
        mocker.patch(
            "brokers.alpaca.performance_ops.api.get_portfolio_history",
            return_value={},
        )

        # Act
        out_path = save_strategy_snapshot("test_strategy")

        # Assert
        assert out_path.exists()
        assert out_path.parent.name == "strategy_snapshots"


class TestGetPortfolioEquitySeries:
    def test_converts_alpaca_history_to_named_series(self, mocker):
        """Equity arrays + unix timestamps become a date-indexed Series named 'portfolio_equity'."""
        # Two arbitrary unix timestamps (2025-01-01, 2025-01-02 UTC).
        history = SimpleNamespace(
            equity=[10000.0, 10100.0],
            timestamp=[1735689600, 1735776000],
        )
        mocker.patch(
            "brokers.alpaca.performance_ops.get_portfolio_history",
            return_value=history,
        )

        series = get_portfolio_equity_series()

        assert isinstance(series, pd.Series)
        assert series.name == "portfolio_equity"
        assert list(series.values) == [10000.0, 10100.0]
        assert isinstance(series.index, pd.DatetimeIndex)
        assert len(series) == 2


class TestGeneratePerformanceReport:
    def test_orchestrates_snapshot_metrics_and_pdf(self, mocker, tmp_path):
        """End-to-end: snapshot, metrics and PDF are produced; benchmark is fetched."""
        snapshot_path = tmp_path / "test_snapshot_20260101_000000.json"
        snapshot_path.write_text("{}")

        mocker.patch(
            "brokers.alpaca.performance_ops.save_strategy_snapshot",
            return_value=snapshot_path,
        )

        portfolio = pd.Series(
            [10000.0, 10100.0, 10200.0],
            index=pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
            name="portfolio_equity",
        )
        mocker.patch(
            "brokers.alpaca.performance_ops.get_portfolio_equity_series",
            return_value=portfolio,
        )

        benchmark = pd.Series(
            [10000.0, 10050.0, 10100.0],
            index=portfolio.index,
            name="benchmark_equity",
        )
        # The orchestrator imports these symbols at call time inside the function,
        # so patch them at the source module.
        mocker.patch(
            "common.portfolio_ops.fetch_normalized_benchmark",
            return_value=(portfolio, benchmark),
        )

        # Stub PerformanceMetrics so we don't depend on real metric maths.
        class _PM:
            def __init__(self, *a, **kw):
                self.benchmark = benchmark
                self.portfolio = portfolio

            def calculate_all(self):
                return {"sharpe": 1.5, "max_drawdown": -0.1}

        mocker.patch(
            "common.portfolio_ops.PerformanceMetrics",
            _PM,
        )

        # Stub the viz layer entirely; we just need build_performance_figures to
        # return an empty list so the PDF writer has only the cover page.
        mocker.patch(
            "common.viz_ops.PerformanceViz",
            return_value=mocker.MagicMock(),
        )
        mocker.patch(
            "common.viz_ops.build_performance_figures",
            return_value=[],
        )

        snap, pdf, metrics = generate_performance_report(
            strategy_name="test",
            output_dir=tmp_path,
            date_start="2025-01-01",
            include_benchmark=True,
            show_plots=False,
        )

        assert snap == snapshot_path
        assert pdf == snapshot_path.with_name(snapshot_path.stem + "_report.pdf")
        assert pdf.exists()
        assert pdf.stat().st_size > 0
        assert metrics == {"sharpe": 1.5, "max_drawdown": -0.1}

    def test_skips_benchmark_when_disabled(self, mocker, tmp_path):
        """``include_benchmark=False`` bypasses the S&P fetch and passes None benchmark."""
        snapshot_path = tmp_path / "skip_snapshot_20260101_000000.json"
        snapshot_path.write_text("{}")
        mocker.patch(
            "brokers.alpaca.performance_ops.save_strategy_snapshot",
            return_value=snapshot_path,
        )

        portfolio = pd.Series(
            [100.0, 101.0, 102.0],
            index=pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
            name="portfolio_equity",
        )
        mocker.patch(
            "brokers.alpaca.performance_ops.get_portfolio_equity_series",
            return_value=portfolio,
        )

        fetch_mock = mocker.patch("common.portfolio_ops.fetch_normalized_benchmark")

        captured = {}

        class _PM:
            def __init__(self, portfolio_equity, benchmark_equity):
                captured["benchmark"] = benchmark_equity
                self.benchmark = benchmark_equity
                self.portfolio = portfolio_equity

            def calculate_all(self):
                return {}

        mocker.patch(
            "common.portfolio_ops.PerformanceMetrics",
            _PM,
        )
        mocker.patch(
            "common.viz_ops.PerformanceViz",
            return_value=mocker.MagicMock(),
        )
        mocker.patch(
            "common.viz_ops.build_performance_figures",
            return_value=[],
        )

        generate_performance_report(
            strategy_name="test",
            output_dir=tmp_path,
            include_benchmark=False,
        )

        fetch_mock.assert_not_called()
        assert captured["benchmark"] is None
