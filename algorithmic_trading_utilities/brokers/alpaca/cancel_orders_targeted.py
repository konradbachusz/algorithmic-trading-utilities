"""
Targeted order cancellation.

Only cancels orders for symbols that are about to receive new trades,
preserving existing protective stops on other positions.
"""

from algorithmic_trading_utilities.brokers.alpaca.orders import get_orders


def cancel_orders_for_symbols(symbols, trading_client):
    """Cancel open orders only for the specified symbols.

    Unlike blanket cancellation, this preserves trailing stop orders on
    positions not being re-entered, preventing the self-defeating pattern
    where protective stops are removed before new trades are placed.

    Args:
        symbols: List of ticker symbols to cancel orders for. If empty,
            no orders are cancelled.
        trading_client: Alpaca TradingClient instance used to cancel
            individual orders.

    Returns:
        The number of orders successfully cancelled.
    """
    if not symbols:
        return 0

    symbols_set = set(symbols)
    orders = get_orders()
    cancelled = 0

    for order in orders:
        if order.symbol in symbols_set:
            try:
                trading_client.cancel_order_by_id(order.id)
                print(
                    f"Cancelled {order.type} order for {order.symbol} (ID: {order.id})"
                )
                cancelled += 1
            except Exception as e:
                print(f"Failed to cancel order for {order.symbol}: {e}")

    return cancelled
