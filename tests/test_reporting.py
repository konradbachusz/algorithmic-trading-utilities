import json
import sys

sys.path.insert(1, "algorithmic_trading_utilities")

from brokers.alpaca.performance_ops import (
    generate_strategy_report,
    generate_strategy_report_data,
    load_strategy_snapshot,
    normalize_snapshot,
)


class TestReportingHelpers:

    def test_load_strategy_snapshot(self, tmp_path):
        snapshot = {"strategy": "s1", "positions": []}
        path = tmp_path / "snap.json"
        path.write_text(json.dumps(snapshot), encoding="utf-8")

        loaded = load_strategy_snapshot(path)

        assert loaded["strategy"] == "s1"

    def test_normalize_snapshot_stringified_items(self):
        snapshot = {
            "positions": ["{'symbol': 'AAPL', 'market_value': '100.0'}"],
            "orders": ["{'status': 'new', 'symbol': 'AAPL'}"],
            "activities": ["{'activity_type': 'FILL', 'qty': '1', 'price': '10'}"],
            "balances": {"cash": "10"},
            "equity_performance": {},
        }

        normalized = normalize_snapshot(snapshot)

        assert normalized["positions"][0]["symbol"] == "AAPL"
        assert normalized["orders"][0]["status"] == "new"
        assert normalized["activities"][0]["activity_type"] == "FILL"


class TestGenerateReport:

    def test_generate_strategy_report_data(self, mocker):
        snapshot = {
            "strategy": "sentiment_analysis_v1",
            "timestamp": "2026-03-22T08:26:34.730669+00:00",
            "positions": [
                {
                    "symbol": "AAPL",
                    "side": "long",
                    "qty": "2",
                    "market_value": "200",
                    "unrealized_pl": "10",
                    "unrealized_plpc": "0.05",
                },
                {
                    "symbol": "MSFT",
                    "side": "short",
                    "qty": "1",
                    "market_value": "-100",
                    "unrealized_pl": "-5",
                    "unrealized_plpc": "-0.05",
                },
            ],
            "orders": [
                {
                    "status": "new",
                    "order_type": "trailing_stop",
                    "side": "sell",
                    "symbol": "AAPL",
                }
            ],
            "activities": [
                {
                    "activity_type": "FILL",
                    "qty": "2",
                    "price": "100",
                    "side": "buy",
                    "symbol": "AAPL",
                    "transaction_time": "2026-03-22T08:00:00Z",
                },
                {
                    "activity_type": "FEE",
                    "net_amount": "-0.01",
                    "created_at": "2026-03-22T08:01:00Z",
                },
            ],
            "balances": {
                "status": "ACTIVE",
                "currency": "USD",
                "equity": "1000",
                "cash": "800",
                "buying_power": "4000",
            },
            "equity_performance": {
                "timestamp": [1700000000, 1700086400],
                "equity": [1000, 1010],
            },
        }

        mocker.patch(
            "brokers.alpaca.performance_ops._compute_performance_metrics",
            return_value={
                "available": True,
                "reason": None,
                "metrics": {"total_return": 0.01, "sharpe_ratio": 1.2},
            },
        )

        report = generate_strategy_report_data(snapshot)

        assert report["strategy"] == "sentiment_analysis_v1"
        assert report["executive_summary"]["open_positions_count"] == 2
        assert report["executive_summary"]["gross_exposure"] == 300.0
        assert report["orders"]["total_orders"] == 1
        assert report["activities"]["total_activities"] == 2
        assert report["equity_performance"]["metrics_available"] is True

    def test_generate_strategy_report_writes_markdown_and_json(self, mocker, tmp_path):
        snapshot = {
            "strategy": "s1",
            "timestamp": "2026-03-22T00:00:00+00:00",
            "positions": [],
            "orders": [],
            "activities": [],
            "balances": {},
            "equity_performance": {},
        }
        snapshot_path = tmp_path / "s1_snapshot.json"
        snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

        mocker.patch(
            "brokers.alpaca.performance_ops._compute_performance_metrics",
            return_value={
                "available": False,
                "reason": "insufficient data",
                "metrics": {},
            },
        )

        md_path = generate_strategy_report(snapshot_path, format="md")
        json_path = generate_strategy_report(snapshot_path, format="json")

        assert md_path.exists()
        assert json_path.exists()

        md_text = md_path.read_text(encoding="utf-8")
        assert "# Strategy Report: s1" in md_text

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert payload["strategy"] == "s1"
