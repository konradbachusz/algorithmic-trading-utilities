"""
Module for managing stop loss operations.

This module provides functions to place trailing stop loss orders for positions
that do not already have them.
"""

from positions import get_positions_without_trailing_stop_loss
from orders import place_trailing_stop_order
from config import trailing_stop_loss_threshold


def place_trailing_stop_losses_funct(threshold=trailing_stop_loss_threshold):
    """
    Place trailing stop loss orders for positions without existing trailing stop losses.

    Parameters:
        threshold (float): The trailing stop loss threshold as a percentage (e.g., 0.1 for 10%).

    Returns:
        int: The total number of trailing stop loss orders placed.
    """
    trailing_stop_count = 0  # Counter for trailing stop loss orders
    try:
        positions_without_trailing_stop = get_positions_without_trailing_stop_loss()
        for position in positions_without_trailing_stop:
            if int(position["quantity"]) > 0:
                trail_percent = str(
                    int(threshold * 100)
                )  # Convert threshold to percentage
                print(
                    f"Placing trailing stop loss order for {position['symbol']} at {trail_percent}%"
                )
                try:
                    result = place_trailing_stop_order(
                        symbol=position["symbol"],
                        quantity=position["quantity"],
                        side=position["side"],
                        trail_percent=trail_percent,
                    )
                    if result:  # Check if the order was placed successfully
                        trailing_stop_count += 1
                except Exception as e:
                    print(f"Skipping {position['symbol']} due to an error: {e}")
                    continue  # Proceed to the next position

        print(f"Placed {trailing_stop_count} trailing stop loss orders.")
        return trailing_stop_count
    except Exception as e:
        print(f"Error while placing trailing stop loss orders: {e}")
