"""
Tests for portfolio constraints.
"""

import unittest
from unittest.mock import patch, MagicMock

import algorithmic_trading_utilities.common.portfolio_constraints as portfolio_constraints
from algorithmic_trading_utilities.common.portfolio_constraints import (
    get_sector,
    check_sector_exposure,
    check_gross_exposure,
)


def _mock_yf_ticker(symbol):
    """Return a mock yfinance Ticker with realistic sector data."""
    sector_data = {
        "XOM": "Energy",
        "CVX": "Energy",
        "COP": "Energy",
        "OXY": "Energy",
        "DVN": "Energy",
        "BP": "Energy",
        "SHEL": "Energy",
        "VLO": "Energy",
        "AAPL": "Technology",
        "MSFT": "Technology",
        "NVDA": "Technology",
        "JPM": "Financial Services",
        "PFE": "Healthcare",
        "WMT": "Consumer Defensive",
    }
    mock_ticker = MagicMock()
    mock_ticker.info = {"sector": sector_data.get(symbol, None)}
    return mock_ticker


class TestGetSector(unittest.TestCase):
    """Test dynamic sector lookup via yfinance."""

    def setUp(self):
        """Clear the sector cache before each test."""
        portfolio_constraints._sector_cache.clear()

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_known_symbol(self, mock_ticker):
        """Known symbols should return their correct sector."""
        self.assertEqual(get_sector("AAPL"), "Technology")
        self.assertEqual(get_sector("XOM"), "Energy")
        self.assertEqual(get_sector("PFE"), "Healthcare")

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_unknown_symbol(self, mock_ticker):
        """Unknown symbols should return 'Unknown'."""
        self.assertEqual(get_sector("ZZZZ"), "Unknown")

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_cache_prevents_duplicate_api_calls(self, mock_ticker):
        """Second call for the same symbol should use cache, not call yfinance again."""
        get_sector("AAPL")
        get_sector("AAPL")
        # yf.Ticker should only be called once for AAPL
        aapl_calls = [c for c in mock_ticker.call_args_list if c[0][0] == "AAPL"]
        self.assertEqual(len(aapl_calls), 1)

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=Exception("API down"),
    )
    def test_api_failure_returns_unknown(self, mock_ticker):
        """If yfinance fails, return 'Unknown' without crashing."""
        self.assertEqual(get_sector("AAPL"), "Unknown")

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_energy_sector_coverage(self, mock_ticker):
        """Multiple energy symbols should all map to 'Energy'."""
        energy_symbols = ["XOM", "CVX", "COP", "OXY", "DVN", "BP", "SHEL", "VLO"]
        for sym in energy_symbols:
            self.assertEqual(get_sector(sym), "Energy", f"{sym} should be Energy")


class TestCheckSectorExposure(unittest.TestCase):
    """Test sector exposure limit checks."""

    def setUp(self):
        """Clear the sector cache before each test."""
        portfolio_constraints._sector_cache.clear()

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_within_limit(self, mock_ticker):
        """Trade allowed when sector exposure is within limit."""
        positions = [
            {"symbol": "XOM", "market_value": "1000"},
            {"symbol": "CVX", "market_value": "1000"},
        ]
        trade = {"symbol": "OXY", "notional": 500}

        allowed, msg = check_sector_exposure(positions, trade, equity=30000)
        self.assertTrue(allowed)

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_exceeds_limit(self, mock_ticker):
        """Trade blocked when sector exposure would exceed 30%."""
        positions = [
            {"symbol": "XOM", "market_value": "3000"},
            {"symbol": "CVX", "market_value": "3000"},
            {"symbol": "OXY", "market_value": "2500"},
        ]
        trade = {"symbol": "BP", "notional": 1000}

        allowed, msg = check_sector_exposure(positions, trade, equity=30000)
        # 3000+3000+2500+1000 = 9500 / 30000 = 31.7% > 30%
        self.assertFalse(allowed)
        self.assertIn("Energy", msg)

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_unknown_sector_always_allowed(self, mock_ticker):
        """Unknown sector symbols should always be allowed."""
        positions = []
        trade = {"symbol": "ZZZZ", "notional": 5000}

        allowed, _ = check_sector_exposure(positions, trade, equity=30000)
        self.assertTrue(allowed)

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_different_sectors_independent(self, mock_ticker):
        """Energy exposure shouldn't block a Technology trade."""
        positions = [
            {"symbol": "XOM", "market_value": "8000"},
        ]
        trade = {"symbol": "AAPL", "notional": 1000}

        allowed, _ = check_sector_exposure(positions, trade, equity=30000)
        self.assertTrue(allowed)

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_exactly_at_limit(self, mock_ticker):
        """Exposure exactly at the limit should be allowed (not strictly greater)."""
        positions = [{"symbol": "XOM", "market_value": "2000"}]
        trade = {"symbol": "CVX", "notional": 1000}

        allowed, _ = check_sector_exposure(positions, trade, equity=10000)
        self.assertTrue(allowed)

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_custom_max_sector_pct(self, mock_ticker):
        """Custom sector limit should be enforced."""
        positions = [{"symbol": "XOM", "market_value": "1500"}]
        trade = {"symbol": "CVX", "notional": 600}

        # 2100/10000 = 21% > 20%
        allowed, _ = check_sector_exposure(
            positions, trade, equity=10000, max_sector_pct=0.20
        )
        self.assertFalse(allowed)

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_empty_positions(self, mock_ticker):
        """With no existing positions, any trade should be allowed."""
        trade = {"symbol": "XOM", "notional": 2000}
        allowed, _ = check_sector_exposure([], trade, equity=30000)
        self.assertTrue(allowed)

    @patch(
        "algorithmic_trading_utilities.common.portfolio_constraints.yf.Ticker",
        side_effect=_mock_yf_ticker,
    )
    def test_zero_equity_does_not_crash(self, mock_ticker):
        """Zero equity edge case should not crash (division guarded to 0)."""
        trade = {"symbol": "XOM", "notional": 100}
        allowed, _ = check_sector_exposure([], trade, equity=0)
        self.assertTrue(allowed)


class TestCheckGrossExposure(unittest.TestCase):
    """Test gross exposure limit checks."""

    def test_within_limit(self):
        """Trade allowed when gross exposure is within 80%."""
        positions = [{"market_value": "10000"}, {"market_value": "-5000"}]
        allowed, _ = check_gross_exposure(positions, 3000, equity=30000)
        # (10000+5000+3000)/30000 = 60% < 80%
        self.assertTrue(allowed)

    def test_exceeds_limit(self):
        """Trade blocked when gross exposure would exceed 80%."""
        positions = [{"market_value": "15000"}, {"market_value": "-8000"}]
        allowed, _ = check_gross_exposure(positions, 3000, equity=30000)
        # (15000+8000+3000)/30000 = 86.7% > 80%
        self.assertFalse(allowed)

    def test_short_positions_counted_as_absolute(self):
        """Short positions should be counted by absolute market value."""
        positions = [{"market_value": "-10000"}]
        allowed, _ = check_gross_exposure(positions, 5000, equity=30000)
        # (10000+5000)/30000 = 50% < 80%
        self.assertTrue(allowed)

    def test_empty_positions(self):
        """With no positions, any reasonable trade should be allowed."""
        allowed, _ = check_gross_exposure([], 5000, equity=30000)
        # 5000/30000 = 16.7%
        self.assertTrue(allowed)

    def test_custom_max_gross_pct(self):
        """Custom gross limit should be enforced."""
        positions = [{"market_value": "4000"}]
        # (4000+2000)/10000 = 60% > 50%
        allowed, _ = check_gross_exposure(
            positions, 2000, equity=10000, max_gross_pct=0.50
        )
        self.assertFalse(allowed)


if __name__ == "__main__":
    unittest.main()
