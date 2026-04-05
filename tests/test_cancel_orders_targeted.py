"""
Tests for targeted order cancellation.
"""

import unittest
from unittest.mock import patch, MagicMock

from algorithmic_trading_utilities.brokers.alpaca.cancel_orders_targeted import (
    cancel_orders_for_symbols,
)


class TestTargetedCancellation(unittest.TestCase):
    """Test targeted order cancellation."""

    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.cancel_orders_targeted.get_orders"
    )
    def test_only_specified_symbols_cancelled(self, mock_get_orders):
        """Should only cancel orders for the given symbols, not all orders."""
        mock_order_aapl = MagicMock(symbol="AAPL", id="order-1", type="trailing_stop")
        mock_order_nvda = MagicMock(symbol="NVDA", id="order-2", type="trailing_stop")
        mock_order_xom = MagicMock(symbol="XOM", id="order-3", type="trailing_stop")
        mock_get_orders.return_value = [
            mock_order_aapl,
            mock_order_nvda,
            mock_order_xom,
        ]

        mock_client = MagicMock()

        count = cancel_orders_for_symbols(["AAPL"], mock_client)

        self.assertEqual(count, 1)
        mock_client.cancel_order_by_id.assert_called_once_with("order-1")

    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.cancel_orders_targeted.get_orders"
    )
    def test_empty_symbols_cancels_nothing(self, mock_get_orders):
        """Empty symbol list should cancel zero orders."""
        mock_client = MagicMock()
        count = cancel_orders_for_symbols([], mock_client)

        self.assertEqual(count, 0)
        mock_get_orders.assert_not_called()

    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.cancel_orders_targeted.get_orders"
    )
    def test_multiple_symbols_cancelled(self, mock_get_orders):
        """Should cancel orders for multiple specified symbols."""
        mock_order_aapl = MagicMock(symbol="AAPL", id="order-1", type="market")
        mock_order_nvda = MagicMock(symbol="NVDA", id="order-2", type="trailing_stop")
        mock_order_xom = MagicMock(symbol="XOM", id="order-3", type="trailing_stop")
        mock_get_orders.return_value = [
            mock_order_aapl,
            mock_order_nvda,
            mock_order_xom,
        ]

        mock_client = MagicMock()

        count = cancel_orders_for_symbols(["AAPL", "XOM"], mock_client)

        self.assertEqual(count, 2)

    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.cancel_orders_targeted.get_orders"
    )
    def test_no_matching_orders(self, mock_get_orders):
        """If no orders match the symbols, cancel count should be 0."""
        mock_order = MagicMock(symbol="TSLA", id="order-1", type="market")
        mock_get_orders.return_value = [mock_order]

        mock_client = MagicMock()

        count = cancel_orders_for_symbols(["AAPL"], mock_client)

        self.assertEqual(count, 0)
        mock_client.cancel_order_by_id.assert_not_called()

    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.cancel_orders_targeted.get_orders"
    )
    def test_handles_cancel_failure_gracefully(self, mock_get_orders):
        """Should handle individual cancel failures without crashing."""
        mock_order = MagicMock(symbol="AAPL", id="order-1", type="market")
        mock_get_orders.return_value = [mock_order]

        mock_client = MagicMock()
        mock_client.cancel_order_by_id.side_effect = Exception("API Error")

        count = cancel_orders_for_symbols(["AAPL"], mock_client)

        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
