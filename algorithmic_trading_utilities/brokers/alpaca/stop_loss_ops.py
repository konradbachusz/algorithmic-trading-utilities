"""
Alpaca stop loss operations module.

This module provides functions to manage stop loss orders, including
trailing stops and threshold-based stop losses.
"""

from .client import trading_client
from .orders import place_trailing_stop_order
from .positions import get_all_positions


def place_trailing_stop_losses_funct(threshold=0.1):
    """
    Place trailing stop loss orders for all open positions.

    Parameters:
        threshold (float): The trailing stop percentage (default: 0.1 for 10%)

    Returns:
        int: Number of trailing stop orders placed
    """
    positions = get_all_positions()
    orders_placed = 0

    for position in positions:
        try:
            result = place_trailing_stop_order(
                symbol=position["symbol"],
                quantity=position["quantity"],
                side=position["side"],
                trail_percent=str(threshold * 100),
            )
            if result:
                orders_placed += 1
                print(f"Trailing stop placed for {position['symbol']}")
        except Exception as e:
            print(f"Failed to place trailing stop for {position['symbol']}: {e}")

    return orders_placed
