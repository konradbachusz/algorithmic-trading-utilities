import json
import sys

sys.path.insert(1, "algorithmic_trading_utilities")

from brokers.alpaca.performance_ops import save_strategy_snapshot


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
