"""Tests for market hours utility."""

import unittest
from unittest.mock import patch
from datetime import datetime, timezone

from algorithmic_trading_utilities.common.market_hours import is_market_hours


class TestIsMarketHours(unittest.TestCase):
    """Test NYSE market hours detection."""

    def test_true_during_session(self):
        """14:00 UTC = 10:00 ET should be market hours."""
        market_time = datetime(2026, 4, 5, 14, 0, tzinfo=timezone.utc)
        with patch(
            "algorithmic_trading_utilities.common.market_hours.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = market_time
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            self.assertTrue(is_market_hours())

    def test_false_before_open(self):
        """03:00 UTC = 23:00 ET should NOT be market hours."""
        off_time = datetime(2026, 4, 5, 3, 0, tzinfo=timezone.utc)
        with patch(
            "algorithmic_trading_utilities.common.market_hours.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = off_time
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            self.assertFalse(is_market_hours())

    def test_false_after_close(self):
        """21:00 UTC = 17:00 ET should NOT be market hours."""
        after_close = datetime(2026, 4, 5, 21, 0, tzinfo=timezone.utc)
        with patch(
            "algorithmic_trading_utilities.common.market_hours.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = after_close
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            self.assertFalse(is_market_hours())

    def test_true_at_open_boundary(self):
        """13:25 UTC = 09:25 ET should be market hours (open buffer)."""
        open_time = datetime(2026, 4, 5, 13, 25, tzinfo=timezone.utc)
        with patch(
            "algorithmic_trading_utilities.common.market_hours.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = open_time
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            self.assertTrue(is_market_hours())

    def test_true_at_close_boundary(self):
        """20:05 UTC = 16:05 ET should be market hours (close buffer)."""
        close_time = datetime(2026, 4, 5, 20, 5, tzinfo=timezone.utc)
        with patch(
            "algorithmic_trading_utilities.common.market_hours.datetime"
        ) as mock_dt:
            mock_dt.now.return_value = close_time
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            self.assertTrue(is_market_hours())


if __name__ == "__main__":
    unittest.main()
