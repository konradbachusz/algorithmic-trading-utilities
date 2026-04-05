"""
Tests for adaptive trailing stop calculation.
"""

import unittest

from algorithmic_trading_utilities.common.trailing_stop_config import (
    calculate_trailing_stop_pct,
)


class TestCalculateTrailingStopPct(unittest.TestCase):
    """Test adaptive trailing stop percentage calculation."""

    def test_low_vol_stock_gets_tighter_stop(self):
        """Low volatility should produce a smaller trailing stop percentage."""
        # PFE-like: ATR ~$0.50, price ~$27
        pct = calculate_trailing_stop_pct(atr=0.50, last_price=27.0)
        self.assertLess(pct, 0.10)  # Should be less than the old flat 10%
        self.assertGreaterEqual(pct, 0.05)  # But at least 5%

    def test_high_vol_stock_gets_wider_stop(self):
        """High volatility should produce a larger trailing stop percentage."""
        # RIVN-like: ATR ~$1.20, price ~$15
        pct = calculate_trailing_stop_pct(atr=1.20, last_price=15.0)
        self.assertGreater(pct, 0.10)  # Should be more than 10%
        self.assertLessEqual(pct, 0.20)  # But capped at 20%

    def test_clamped_at_minimum(self):
        """Stop should never be below min_pct."""
        # Very low ATR relative to price
        pct = calculate_trailing_stop_pct(atr=0.01, last_price=500.0)
        self.assertEqual(pct, 0.05)

    def test_clamped_at_maximum(self):
        """Stop should never exceed max_pct."""
        # Very high ATR relative to price
        pct = calculate_trailing_stop_pct(atr=50.0, last_price=10.0)
        self.assertEqual(pct, 0.20)

    def test_fallback_on_zero_atr(self):
        """If ATR is 0 or None, return default 10%."""
        self.assertEqual(calculate_trailing_stop_pct(atr=0, last_price=100.0), 0.10)
        self.assertEqual(calculate_trailing_stop_pct(atr=None, last_price=100.0), 0.10)

    def test_fallback_on_zero_price(self):
        """If price is 0, return default 10%."""
        self.assertEqual(calculate_trailing_stop_pct(atr=5.0, last_price=0), 0.10)

    def test_fallback_on_negative_atr(self):
        """If ATR is negative, return default 10%."""
        self.assertEqual(calculate_trailing_stop_pct(atr=-1.0, last_price=100.0), 0.10)

    def test_real_snapshot_examples(self):
        """Verify with approximate ATRs for snapshot positions."""
        # CVX: price ~$201, ATR ~$4 -> expect ~5% (2.5*4/201 = 4.97%)
        cvx = calculate_trailing_stop_pct(atr=4.0, last_price=201.0)
        self.assertAlmostEqual(cvx, 0.05, places=2)

        # NCLH: price ~$19, ATR ~$1.5 -> expect ~19.7% (2.5*1.5/19 = 19.7%)
        nclh = calculate_trailing_stop_pct(atr=1.5, last_price=19.0)
        self.assertAlmostEqual(nclh, 0.1974, places=2)

        # NOK: price ~$8, ATR ~$0.20 -> expect 6.25% (2.5*0.2/8)
        nok = calculate_trailing_stop_pct(atr=0.20, last_price=8.0)
        self.assertAlmostEqual(nok, 0.0625, places=3)

    def test_custom_bounds(self):
        """Custom min/max bounds should be respected."""
        pct = calculate_trailing_stop_pct(
            atr=0.01, last_price=100.0, min_pct=0.03, max_pct=0.15
        )
        self.assertEqual(pct, 0.03)

        pct = calculate_trailing_stop_pct(
            atr=100.0, last_price=10.0, min_pct=0.03, max_pct=0.15
        )
        self.assertEqual(pct, 0.15)

    def test_custom_atr_multiplier(self):
        """Custom ATR multiplier should affect the result."""
        # With default 2.5x: 2.5 * 5.0 / 100.0 = 0.125
        default_pct = calculate_trailing_stop_pct(atr=5.0, last_price=100.0)
        self.assertAlmostEqual(default_pct, 0.125, places=3)

        # With 1.0x: 1.0 * 5.0 / 100.0 = 0.05
        lower_pct = calculate_trailing_stop_pct(
            atr=5.0, last_price=100.0, atr_multiplier=1.0
        )
        self.assertAlmostEqual(lower_pct, 0.05, places=3)


if __name__ == "__main__":
    unittest.main()
