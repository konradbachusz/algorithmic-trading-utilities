# TODO fix to specific imports instead of *
from alpaca.data.live.stock import *
from alpaca.data.historical.stock import *
from alpaca.data.requests import *
from alpaca.data.timeframe import *
from alpaca.trading.client import *
from alpaca.trading.stream import *
from alpaca.trading.requests import *
from alpaca.trading.enums import *
from alpaca.common.exceptions import APIError
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
import time


# TODO research if there's a more elegant solution to this
# Try different import approaches for data modules
try:
    from common.email_ops import send_email_notification
except ImportError:
    from algorithmic_trading_utilities.common.email_ops import send_email_notification

try:
    from common.config import trading_client
except ImportError:
    from algorithmic_trading_utilities.common.config import trading_client

# Load environment variables from .env file
load_dotenv()

"""
Module for managing orders.

This module provides functions to place various types of orders, retrieve open orders,
cancel orders, and manage trailing stop orders.
"""


def place_order(
    symbol, quantity, side, type, time_in_force, stop_price=None, limit_price=None
):
    """
    Place an order based on the provided parameters.

    Parameters:
        symbol (str): The symbol of the asset to trade.
        quantity (int): The quantity of the asset to trade.
        side (str): The side of the order ('buy' or 'sell').
        type (str): The type of order ('MarketOrderRequest', 'LimitOrderRequest', or 'TrailingStopLoss').
        time_in_force (str): The duration for which the order will remain active.
        stop_price (float, optional): The stop price for stop orders.
        limit_price (float, optional): The limit price for limit orders.

    Returns:
        object: The submitted order if successful, None otherwise.
    """

    if type == "MarketOrderRequest":
        try:
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,  # Use 'qty' instead of 'quantity' as required by Alpaca
                side=OrderSide(side),  # Convert side to OrderSide enum
                time_in_force=TimeInForce(time_in_force),  # Convert to TimeInForce enum
            )

            market_order = trading_client.submit_order(order_data=market_order_data)
            return market_order
        except APIError as e:
            print(f"Error placing market order: {e}")
            return None
    elif type == "TrailingStopLoss":
        try:
            trailing_stop_order_data = StopOrderRequest(
                symbol=symbol,
                stop_price=stop_price,
                qty=quantity,
                side=OrderSide(side),
                time_in_force=TimeInForce("gtc"),
            )

            trailing_stop_order = trading_client.submit_order(
                order_data=trailing_stop_order_data
            )
            return trailing_stop_order
        except APIError as e:
            print(f"Error placing trailing stop order: {e}")
            return None
    elif type == "LimitOrderRequest":
        try:
            limit_order_data = LimitOrderRequest(
                symbol=symbol,
                limit_price=limit_price,
                qty=quantity,
                side=OrderSide(side),
                time_in_force=TimeInForce(time_in_force),
            )

            limit_order = trading_client.submit_order(order_data=limit_order_data)
            return limit_order
        except APIError as e:
            print(f"Error placing limit order: {e}")
            return None


def get_orders():
    """
    Retrieve all open orders.

    Returns:
        list: A list of open orders.
    """
    orders = trading_client.get_orders(
        filter=GetOrdersRequest(status=QueryOrderStatus.OPEN)
    )
    return orders


def get_current_trailing_stop_orders():
    """
    Retrieve active trailing stop orders for both long and short positions.

    Returns:
        list: A list of trailing stop orders with a status of OPEN (includes both BUY and SELL orders).
    """
    # Get all open orders and filter for trailing stop type
    # This includes both SELL trailing stops (for long positions) and BUY trailing stops (for short positions)
    all_open_orders = trading_client.get_orders(
        filter=GetOrdersRequest(status=QueryOrderStatus.OPEN)
    )

    # Filter for trailing stop orders only
    trailing_stop_orders = [
        order for order in all_open_orders if order.order_type == "trailing_stop"
    ]
    return trailing_stop_orders


def cancel_orders():
    """
    Cancel all open orders until no orders remain.

    Sends an email notification upon success or failure.

    Returns:
        int: The total number of orders canceled.
    """
    total_canceled_count = 0
    max_retries = 5
    delay = 1  # Initial delay in seconds
    subject = "Order Management"  # Email subject for notifications
    consecutive_no_cancellations = (
        0  # Counter for consecutive retries with no cancellations
    )

    try:
        print("Cancelling all orders")

        for attempt in range(max_retries):
            open_orders = trading_client.get_orders()  # Retrieve all open orders
            if not open_orders:
                print("No open orders remaining. Exiting.")
                break  # Exit loop if no open orders remain

            canceled_count = 0
            for order in open_orders:
                try:
                    trading_client.cancel_order_by_id(order.id)  # Cancel each order
                    print(f"Cancelled order: {order.id} for symbol: {order.symbol}")
                    canceled_count += 1
                except APIError as e:
                    if "order pending cancel" in str(e):
                        print(
                            f"Skipping order {order.id} as it is already pending cancel."
                        )
                    else:
                        print(f"Error while cancelling order {order.id}: {e}")
                        raise e  # Re-raise the exception for testing and debugging

            total_canceled_count += canceled_count
            print(
                f"Canceled {canceled_count} orders in this iteration. Retrying if necessary..."
            )

            if canceled_count == 0:
                consecutive_no_cancellations += 1
                print(
                    f"No orders canceled in this iteration. Consecutive no-cancellation attempts: {consecutive_no_cancellations}."
                )
                if consecutive_no_cancellations >= 2:
                    print(
                        "No orders left to cancel or all are pending cancel. Exiting gracefully."
                    )
                    break
            else:
                consecutive_no_cancellations = 0  # Reset counter if orders are canceled

            time.sleep(delay)
            delay *= 2  # Exponential backoff

        print("All orders processed.")
        notification = f"Total orders canceled: {total_canceled_count}"
        send_email_notification(subject, notification, type="SUCCESS")
    except Exception as e:
        notification = f"Error while cancelling orders: {e}"
        send_email_notification(subject, notification, type="FAILURE")
        print(notification)
        raise  # Re-raise the exception to allow proper testing

    return total_canceled_count


def place_trailing_stop_order(symbol, quantity, side, trail_percent="10"):
    """
    Place a trailing stop order for both long and short positions.

    Parameters:
        symbol (str): The symbol of the asset to trade.
        quantity (int): The quantity of the asset to trade.
        side (str): The side of the initial order ('buy' or 'sell').
                   For long positions (buy), places a sell trailing stop.
                   For short positions (sell), places a buy trailing stop.
        trail_percent (str): The trailing percentage for the stop order.

    Returns:
        object: The response from submitting the trailing stop order, or None if an error occurs.
    """
    api_key = os.environ["PAPER_KEY"]
    secret_key = os.environ["PAPER_SECRET"]
    base_url = "https://paper-api.alpaca.markets"
    api = tradeapi.REST(key_id=api_key, secret_key=secret_key, base_url=base_url)
    try:
        # Determine the trailing stop side based on position type
        # Long position (buy): need sell trailing stop to close
        # Short position (sell): need buy trailing stop to close
        stop_side = "sell" if side.lower() == "buy" else "buy"

        # Submit trailing stop loss order
        trailing_stop_response = api.submit_order(
            symbol=symbol,
            qty=quantity,
            side=stop_side,  # Opposite of the initial order
            type="trailing_stop",
            time_in_force="gtc",
            trail_percent=trail_percent,
        )
        return trailing_stop_response
    except APIError as e:
        if "asset is not active" in str(e) or "asset DFS is not active" in str(e):
            print(f"Skipping {symbol} as the asset is not active: {e}")
            return None  # Proceed to the next order
        else:
            print(f"Error placing trailing stop order for {symbol}: {e}")
            return None


def place_trailing_stop_losses_funct(threshold):
    """
    Place trailing stop loss orders for positions without existing trailing stop losses.

    Parameters:
        threshold (float): The trailing stop loss threshold as a percentage (e.g., 0.1 for 10%).

    Returns:
        int: The total number of trailing stop loss orders placed.
    """
    # Import here to avoid circular dependency with positions.py
    from algorithmic_trading_utilities.brokers.alpaca.positions import (
        get_positions_without_trailing_stop_loss,
    )

    trailing_stop_count = 0  # Counter for trailing stop loss orders
    try:
        positions_without_trailing_stop = get_positions_without_trailing_stop_loss()
        print("positions_without_trailing_stop", positions_without_trailing_stop)
        print(len(positions_without_trailing_stop))
        for position in positions_without_trailing_stop:
            quantity_int = int(position["quantity"])
            if quantity_int != 0:  # Handle both positive and negative quantities
                trail_percent = str(
                    int(threshold * 100)
                )  # Convert threshold to percentage

                # Use absolute value for quantity to handle both long and short positions
                abs_quantity = abs(quantity_int)

                print(
                    f"Placing trailing stop loss order for {position['symbol']} at {trail_percent}%"
                )
                try:
                    result = place_trailing_stop_order(
                        symbol=position["symbol"],
                        quantity=abs_quantity,
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


def get_orders_to_cancel():
    """
    Identify orders that should be canceled.

    Compares all open orders to trailing stop orders and returns the IDs of orders
    that are not trailing stop orders.

    Returns:
        set: A set of order IDs to cancel.
    """
    order_ids = {order.id for order in get_orders()}
    trailing_stop_orders_ids = {
        order.id for order in get_current_trailing_stop_orders()
    }
    orders_to_cancel = order_ids - trailing_stop_orders_ids
    return orders_to_cancel


def get_orders_symbol_list(orders):
    """
    Extract symbols from a list of orders.

    Parameters:
        orders (list): A list of order objects.

    Returns:
        list: A list of symbols extracted from the orders.
    """
    order_symbols = []
    for order in orders:
        order_symbols.append(order.symbol)
    return order_symbols


def cancel_order_by_symbol(symbol):
    """
    Cancel the first open SELL order for a given symbol.

    Parameters:
        symbol (str): The symbol of the asset whose order needs to be canceled.

    Returns:
        str: The ID of the canceled order, or None if no order was found.
    """
    try:
        request_params = GetOrdersRequest(
            status=QueryOrderStatus.OPEN, side=OrderSide.SELL, symbols=[symbol]
        )
        orders = trading_client.get_orders(filter=request_params)

        if not orders:
            print(f"No open SELL orders found for symbol {symbol}.")
            return None

        order_to_swap = orders[0].id
        trading_client.cancel_order_by_id(order_to_swap)
        print(f"Order {order_to_swap} cancelled for symbol {symbol}.")
        return order_to_swap
    except Exception as e:
        print(f"Error cancelling order for symbol {symbol}: {e}")
        return None
