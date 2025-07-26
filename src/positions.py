from config import trading_client

# TODO import specific methods
from alpaca.trading.client import *
from orders import get_current_trailing_stop_orders, cancel_order_by_symbol


def get_open_positions():
    """
    Retrieve and return a list of open positions with their symbols, quantities, and corresponding buy/sell sides. Adjust the side mapping based on the position's side ('long' or 'short').

    Each position includes:
    - Symbol
    - Quantity
    - Side (buy/sell, mapped from long/short)

    Returns:
        list: A list of dictionaries representing open positions.
    """
    open_positions = trading_client.get_all_positions()

    positions_list = []
    for position in open_positions:
        positions_list.append(
            {"symbol": position.symbol, "quantity": position.qty, "side": position.side}
        )

        # change the mapping for the trailing stop loss
        if position.side == "long":
            positions_list[-1]["side"] = "buy"
        else:
            positions_list[-1]["side"] = "sell"

    return positions_list


def get_positions_without_trailing_stop_loss():
    """
    Identify positions without trailing stop loss orders.

    Compares open positions to the list of trailing stop loss orders and
    returns positions that are not associated with any trailing stop loss orders.

    Returns:
        list: A list of dictionaries representing positions without trailing stop loss orders.
    """
    open_positions = get_open_positions()
    trailing_stop_orders = get_current_trailing_stop_orders()
    positions_without_trailing_stop_loss = []
    for position in open_positions:
        found = False
        for order in trailing_stop_orders:
            if position["symbol"] == order.symbol and position["quantity"] == order.qty:
                found = True
                break
        if not found:
            positions_without_trailing_stop_loss.append(position)
    return positions_without_trailing_stop_loss


def get_positions_symbol_list(positions):
    """
    Extract symbols from a list of positions.

    Parameters:
        positions (list): A list of position objects.

    Returns:
        list: A list of symbols extracted from the positions.
    """
    position_symbols = []
    for position in positions:
        position_symbols.append(position["symbol"])
    return position_symbols


def close_positions_below_threshold(threshold):
    """
    Close positions with unrealized P/L below the specified threshold.

    Parameters:
        threshold (float): The P/L percentage threshold (e.g., 0.05 for 5%).

    Returns:
        int: The total number of positions closed.
    """
    # Change the sign of the threshold to be negative
    threshold = -abs(threshold)
    closed_positions_count = 0  # Counter for closed positions
    try:
        open_positions = (
            trading_client.get_all_positions()
        )  # Retrieve all open positions

        for position in open_positions:
            # Check the unrealized P/L percentage (unrealized_plpc is a float between 0 and 1)
            unrealized_plpc = float(position.unrealized_plpc)

            if unrealized_plpc <= threshold:
                symbol = position.symbol
                print(
                    f"Closing position for {symbol} with unrealized P/L: {unrealized_plpc * 100:.2f}%"
                )
                try:
                    trading_client.close_position(symbol)
                    print(f"Position for {symbol} closed.")
                except Exception as close_error:
                    print(f"Failed to close position for {symbol}: {close_error}")
                    try:
                        cancel_order_by_symbol(symbol)
                        print(f"Canceled trailing order for {symbol} as fallback.")
                        trading_client.close_position(symbol)
                        print(f"Position for {symbol} closed.")
                    except Exception as cancel_error:
                        print(f"Failed to cancel order for {symbol}: {cancel_error}")
                closed_positions_count += 1

        print(f"Total positions closed: {closed_positions_count}")
        return closed_positions_count
    except Exception as e:
        print(f"Error while closing positions: {e}")
