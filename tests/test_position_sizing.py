"""
Tests for ATR-based position sizing.
"""

import unittest
from unittest.mock import patch, MagicMock

from algorithmic_trading_utilities.common.position_sizing import (
    calculate_position_size,
    get_atr,
)


class TestGetATR(unittest.TestCase):
    """Test ATR calculation."""

    def test_atr_returns_positive_float(self):
        """ATR should return a positive float for valid data."""
        import pandas as pd

        mock_df = pd.DataFrame(
            {
                "high": [
                    102,
                    105,
                    103,
                    106,
                    104,
                    107,
                    105,
                    108,
                    106,
                    109,
                    107,
                    110,
                    108,
                    111,
                    109,
                ],
                "low": [
                    98,
                    101,
                    99,
                    102,
                    100,
                    103,
                    101,
                    104,
                    102,
                    105,
                    103,
                    106,
                    104,
                    107,
                    105,
                ],
                "close": [
                    100,
                    103,
                    101,
                    104,
                    102,
                    105,
                    103,
                    106,
                    104,
                    107,
                    105,
                    108,
                    106,
                    109,
                    107,
                ],
            }
        )

        mock_bars = MagicMock()
        mock_bars.df = mock_df
        mock_client_instance = MagicMock()
        mock_client_instance.get_stock_bars.return_value = mock_bars

        atr = get_atr("AAPL", mock_client_instance, period=14)

        self.assertIsNotNone(atr)
        self.assertGreater(atr, 0)

    def test_atr_returns_none_for_insufficient_data(self):
        """ATR should return None when not enough bars are available."""
        import pandas as pd

        mock_df = pd.DataFrame(
            {
                "high": [102, 105],
                "low": [98, 101],
                "close": [100, 103],
            }
        )

        mock_bars = MagicMock()
        mock_bars.df = mock_df
        mock_client_instance = MagicMock()
        mock_client_instance.get_stock_bars.return_value = mock_bars

        atr = get_atr("AAPL", mock_client_instance, period=14)

        self.assertIsNone(atr)

    def test_atr_handles_api_exception(self):
        """ATR should return None on API failure, not raise."""
        mock_client = MagicMock()
        mock_client.get_stock_bars.side_effect = Exception("API Error")

        atr = get_atr("INVALID", mock_client)

        self.assertIsNone(atr)


class TestCalculatePositionSize(unittest.TestCase):
    """Test the position sizing function."""

    @patch("algorithmic_trading_utilities.common.position_sizing.get_atr")
    def test_high_vol_stock_gets_fewer_shares(self, mock_atr):
        """A stock with high ATR should get fewer shares than a low ATR stock."""
        mock_client = MagicMock()

        # Low volatility stock: ATR = $2
        mock_atr.return_value = 2.0
        low_vol = calculate_position_size("PFE", 27.0, 30000.0, 0.01, mock_client)

        # High volatility stock: ATR = $10
        mock_atr.return_value = 10.0
        high_vol = calculate_position_size("RIVN", 15.0, 30000.0, 0.01, mock_client)

        self.assertGreater(low_vol["quantity"], high_vol["quantity"])

    @patch("algorithmic_trading_utilities.common.position_sizing.get_atr")
    def test_position_capped_at_max_pct(self, mock_atr):
        """Position notional should not exceed max_position_pct of equity."""
        mock_client = MagicMock()
        mock_atr.return_value = 0.10  # Very low ATR -> would want many shares

        result = calculate_position_size(
            "NOK", 8.0, 30000.0, 0.01, mock_client, max_position_pct=0.03
        )

        max_notional = 30000.0 * 0.03  # $900
        actual_notional = result["quantity"] * 8.0
        self.assertLessEqual(actual_notional, max_notional)

    @patch("algorithmic_trading_utilities.common.position_sizing.get_atr")
    def test_zero_quantity_for_expensive_stock(self, mock_atr):
        """If stock price > max_position_pct of equity, quantity should be 0."""
        mock_client = MagicMock()
        mock_atr.return_value = 50.0  # High ATR

        result = calculate_position_size(
            "BRK.A", 600000.0, 30000.0, 0.01, mock_client, max_position_pct=0.03
        )

        self.assertEqual(result["quantity"], 0)

    @patch("algorithmic_trading_utilities.common.position_sizing.get_atr")
    def test_fallback_when_atr_unavailable(self, mock_atr):
        """When ATR returns None, use fallback_risk_pct for stop distance."""
        mock_client = MagicMock()
        mock_atr.return_value = None

        result = calculate_position_size(
            "NEWIPO", 50.0, 30000.0, 0.01, mock_client, fallback_risk_pct=0.05
        )

        expected_stop = 50.0 * 0.05  # $2.50
        self.assertAlmostEqual(result["stop_distance"], expected_stop, places=2)
        self.assertGreater(result["quantity"], 0)

    @patch("algorithmic_trading_utilities.common.position_sizing.get_atr")
    def test_risk_dollars_equals_equity_times_risk_pct(self, mock_atr):
        """risk_dollars should always equal equity x risk_per_trade."""
        mock_client = MagicMock()
        mock_atr.return_value = 5.0

        result = calculate_position_size("AAPL", 250.0, 30000.0, 0.02, mock_client)

        self.assertEqual(result["risk_dollars"], 600.0)

    @patch("algorithmic_trading_utilities.common.position_sizing.get_atr")
    def test_minimum_one_share(self, mock_atr):
        """If calculation yields 0 shares but stock is affordable, buy at least 1."""
        mock_client = MagicMock()
        mock_atr.return_value = 500.0  # Huge ATR relative to risk

        result = calculate_position_size(
            "EXPENSIVE", 800.0, 30000.0, 0.01, mock_client, max_position_pct=0.03
        )

        # 800 < 30000 * 0.03 = 900, so 1 share should be bought
        self.assertEqual(result["quantity"], 1)

    @patch("algorithmic_trading_utilities.common.position_sizing.get_atr")
    def test_result_dict_has_required_keys(self, mock_atr):
        """Result should contain all expected keys."""
        mock_client = MagicMock()
        mock_atr.return_value = 3.0

        result = calculate_position_size("AAPL", 150.0, 30000.0, 0.01, mock_client)

        required_keys = ["quantity", "stop_distance", "atr", "risk_dollars", "notional"]
        for key in required_keys:
            self.assertIn(key, result)

    @patch("algorithmic_trading_utilities.common.position_sizing.get_atr")
    def test_notional_matches_quantity_times_price(self, mock_atr):
        """Notional should equal quantity * last_price."""
        mock_client = MagicMock()
        mock_atr.return_value = 2.0

        result = calculate_position_size("TEST", 50.0, 30000.0, 0.01, mock_client)

        self.assertAlmostEqual(result["notional"], result["quantity"] * 50.0, places=2)


if __name__ == "__main__":
    unittest.main()
