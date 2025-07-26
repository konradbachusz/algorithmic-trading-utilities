"""
Script to cancel all open orders.

This script cancels all open orders using the `cancel_orders` function from the `orders` module.
It can be run independently before executing the main trading script.
"""

from orders import cancel_orders

# This script cancels all open orders. It can be run before main.py
if __name__ == "__main__":
    canceled_count = cancel_orders()
    print(f"Total orders canceled: {canceled_count}")
