import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from get_data import get_last_price
from strategies.momentum_strategy import (
    get_momentum_trades_list,
)

# TODO import specific methods
from alpaca.data.live.stock import *
from alpaca.data.historical.stock import *
from alpaca.data.requests import *
from alpaca.data.timeframe import *
from alpaca.trading.client import *
from alpaca.trading.stream import *
from alpaca.trading.requests import *
from alpaca.trading.enums import *
from orders import get_orders, place_order
from math import floor
from config import loss_threshold
from email_ops import send_email_notification

subject = "Placed Trades"

try:
    # TODO add dynamic position sizing functionality
    portfolio_size = 100000
    risk_per_trade = 0.01
    trade_size = risk_per_trade * portfolio_size

    api_key = os.environ["PAPER_KEY"]
    secret_key = os.environ["PAPER_SECRET"]

    # setup clients
    trading_client = TradingClient(
        api_key=api_key, secret_key=secret_key, paper=True, url_override=None
    )

    stock_historical_data_client = StockHistoricalDataClient(api_key, secret_key)

    # Trading control parameters
    place_trades = True
    show_orders = False

    ############################
    ##### Execution Example ####
    ############################

    """
    Main script for a strategy.

    This script retrieves trade opportunities,
    places trades with an initial stop loss, and optionally displays open orders.
    """

    strategy = "momentum_strategy"

    trades_list = get_momentum_trades_list(trading_client)

    # Trade Execution
    if place_trades == True:
        """
        Execute trades.

        For each trade opportunity:
        - Calculate the quantity of assets to buy/sell based on the portfolio size and risk per trade.
        - Place the order with an initial stop loss.
        """
        trades_placed_count = 0  # Counter for trades placed
        try:
            for trade in trades_list:

                # TODO wrap the quantity calculation in some function
                last_price = get_last_price(
                    trade["symbol"], stock_historical_data_client
                )

                # Skip the step if the last price is none
                if last_price == None:
                    continue

                quantity = int(
                    floor(trade_size / last_price)
                )  # Round down the number of assets that can be bought #TODO fix to round down
                initial_stop_loss = round(
                    last_price - last_price * loss_threshold, 2
                )  # TODO pass from some config + investigate why the values are different

                place_order(
                    trade["symbol"],
                    quantity,
                    trade["side"],
                    trade["type"],
                    trade["time_in_force"],
                    stop_price=initial_stop_loss,
                )
                trades_placed_count += 1  # Increment the counter

            notification = (
                f"Trades Placed: {trades_placed_count}"  # TODO add a list of assets
            )
            send_email_notification(subject, notification, type="SUCCESS")
            print(notification)
        except Exception as e:
            notification = f"Error executing trades: {e}"
            send_email_notification(subject, notification, type="FAILURE")
            print(notification)

    ##################################
    ## Trading Operations Functions ##
    ##################################

    # Get all Open orders
    if show_orders == True:
        print(get_orders())

except Exception as e:
    # Send failure notification for any unhandled exception
    notification = f"Error in main execution: {e}"
    send_email_notification(subject, notification, type="FAILURE")
    print(notification)
