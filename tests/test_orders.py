import sys

sys.path.insert(1, "src")
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest,
)
from alpaca.common.exceptions import APIError
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
import pytest
from brokers.alpaca.orders import (
    get_orders,
    cancel_orders,
    place_order,
    get_current_trailing_stop_orders,
    place_trailing_stop_order,
    get_orders_to_cancel,
    get_orders_symbol_list,
    cancel_order_by_symbol,
)
from alpaca.trading.enums import OrderSide, TimeInForce


class TestPlaceOrder:

    # Successfully place a market order with valid parameters
    def test_place_market_order_success(self, mocker):

        # Arrange
        symbol = "AAPL"
        quantity = 10
        side = "buy"
        order_type = "MarketOrderRequest"  # Renamed 'type' to avoid shadowing built-in
        time_in_force = "gtc"

        mock_order = mocker.Mock()
        # Patch the trading_client used within the 'orders' module
        mock_submit = mocker.patch(
            "brokers.alpaca.orders.trading_client.submit_order", return_value=mock_order
        )

        # Act
        result = place_order(symbol, quantity, side, order_type, time_in_force)

        # Assert
        # Check that the patched method was called with the correct arguments
        mock_submit.assert_called_once()
        call_args = mock_submit.call_args[1][
            "order_data"
        ]  # Get the order_data keyword argument
        assert isinstance(call_args, MarketOrderRequest)
        assert call_args.symbol == symbol
        assert call_args.qty == quantity
        assert call_args.side == OrderSide(side)
        assert call_args.time_in_force == TimeInForce(time_in_force)
        assert result == mock_order

    # Attempt to place a market order with an invalid symbol
    def test_place_market_order_invalid_symbol(self, mocker):

        # Arrange
        symbol = "INVALID"
        quantity = 10
        side = "buy"
        order_type = "MarketOrderRequest"  # Renamed 'type' to avoid shadowing built-in
        time_in_force = "gtc"

        # Patch the trading_client used within the 'orders' module
        mock_submit = mocker.patch(
            "brokers.alpaca.orders.trading_client.submit_order",
            side_effect=APIError("Invalid symbol"),
        )

        # Act
        result = place_order(symbol, quantity, side, order_type, time_in_force)

        # Assert
        # Check that the patched method was called with the correct arguments
        mock_submit.assert_called_once()
        call_args = mock_submit.call_args[1][
            "order_data"
        ]  # Get the order_data keyword argument
        assert isinstance(call_args, MarketOrderRequest)
        assert call_args.symbol == symbol
        assert call_args.qty == quantity
        assert call_args.side == OrderSide(side)
        assert call_args.time_in_force == TimeInForce(time_in_force)
        assert result is None

    # Successfully place a limit order
    def test_place_limit_order_success(self, mocker):
        # Arrange
        symbol = "GOOG"
        quantity = 5
        side = "sell"
        order_type = "LimitOrderRequest"
        time_in_force = "day"
        limit_price = 2800.00

        mock_order = mocker.Mock()
        mock_submit = mocker.patch(
            "brokers.alpaca.orders.trading_client.submit_order", return_value=mock_order
        )

        # Act
        result = place_order(
            symbol, quantity, side, order_type, time_in_force, limit_price=limit_price
        )

        # Assert
        mock_submit.assert_called_once()
        call_args = mock_submit.call_args[1]["order_data"]
        assert isinstance(call_args, LimitOrderRequest)
        assert call_args.symbol == symbol
        assert call_args.qty == quantity
        assert call_args.side == OrderSide(side)
        assert call_args.time_in_force == TimeInForce(time_in_force)
        assert call_args.limit_price == limit_price
        assert result == mock_order

    # Successfully place a stop order (used for trailing stop in the code)
    def test_place_stop_order_success(self, mocker):
        # Arrange
        symbol = "MSFT"
        quantity = 20
        side = "sell"
        order_type = "TrailingStopLoss"  # This maps to StopOrderRequest in the function
        time_in_force = "gtc"  # Hardcoded in the function for this type
        stop_price = 295.50

        mock_order = mocker.Mock()
        mock_submit = mocker.patch(
            "brokers.alpaca.orders.trading_client.submit_order", return_value=mock_order
        )

        # Act
        result = place_order(
            symbol, quantity, side, order_type, time_in_force, stop_price=stop_price
        )

        # Assert
        mock_submit.assert_called_once()
        call_args = mock_submit.call_args[1]["order_data"]
        assert isinstance(call_args, StopOrderRequest)
        assert call_args.symbol == symbol
        assert call_args.qty == quantity
        assert call_args.side == OrderSide(side)
        assert call_args.time_in_force == TimeInForce(
            "gtc"
        )  # Check the hardcoded value
        assert call_args.stop_price == stop_price
        assert result == mock_order

    # Handle APIError for limit order
    def test_place_limit_order_api_error(self, mocker):
        # Arrange
        symbol = "GOOG"
        quantity = 5
        side = "sell"
        order_type = "LimitOrderRequest"
        time_in_force = "day"
        limit_price = 2800.00

        mock_submit = mocker.patch(
            "brokers.alpaca.orders.trading_client.submit_order",
            side_effect=APIError("Limit error"),
        )

        # Act
        result = place_order(
            symbol, quantity, side, order_type, time_in_force, limit_price=limit_price
        )

        # Assert
        mock_submit.assert_called_once()
        assert result is None

    # Handle APIError for stop order
    def test_place_stop_order_api_error(self, mocker):
        # Arrange
        symbol = "MSFT"
        quantity = 20
        side = "sell"
        order_type = "TrailingStopLoss"
        time_in_force = "gtc"
        stop_price = 295.50

        mock_submit = mocker.patch(
            "brokers.alpaca.orders.trading_client.submit_order",
            side_effect=APIError("Stop error"),
        )

        # Act
        result = place_order(
            symbol, quantity, side, order_type, time_in_force, stop_price=stop_price
        )

        # Assert
        mock_submit.assert_called_once()
        assert result is None


class TestGetOrders:

    # Retrieve a list of open orders successfully
    def test_retrieve_open_orders_successfully(self, mocker):

        mock_orders = [{"id": "order1"}, {"id": "order2"}]
        # Patch the trading_client used within the 'orders' module
        mock_get_orders = mocker.patch(
            "brokers.alpaca.orders.trading_client.get_orders", return_value=mock_orders
        )

        orders = get_orders()

        assert orders == mock_orders
        mock_get_orders.assert_called_once_with(
            filter=GetOrdersRequest(status=QueryOrderStatus.OPEN)
        )

    # Handle APIError exceptions gracefully
    def test_handle_api_error_exception(self, mocker):

        # Patch the trading_client used within the 'orders' module
        mock_get_orders = mocker.patch(
            "brokers.alpaca.orders.trading_client.get_orders",
            side_effect=APIError("API error occurred"),
        )

        # The get_orders function doesn't catch APIError, so it should propagate
        with pytest.raises(APIError, match="API error occurred"):
            get_orders()

        mock_get_orders.assert_called_once()


class TestCancelOrders:

    # Successfully cancel all open orders when there are open orders
    def test_cancel_all_open_orders_success(self, mocker):
        # Arrange
        mock_get_orders = mocker.patch(
            "brokers.alpaca.orders.trading_client.get_orders",
            side_effect=[
                [
                    mocker.Mock(id="order1", symbol="AAPL")
                ],  # First call returns an open order
                [],  # Second call returns no open orders
            ],
        )
        mock_cancel_order_by_id = mocker.patch(
            "brokers.alpaca.orders.trading_client.cancel_order_by_id"
        )

        # Mock send_email_notification to avoid actual email sending
        mock_send_email = mocker.patch("brokers.alpaca.orders.send_email_notification")

        # Act
        cancel_orders()

        # Assert
        assert mock_get_orders.call_count == 2  # Ensure it stops after no open orders
        mock_cancel_order_by_id.assert_called_once_with("order1")
        # Accept any call to send_email_notification with type="SUCCESS"
        found = False
        for call in mock_send_email.call_args_list:
            args, kwargs = call
            if "SUCCESS" in args or kwargs.get("type") == "SUCCESS":
                found = True
                break
        assert found, "send_email_notification was not called with type='SUCCESS'"

    # Handle API errors gracefully when the trading client fails to cancel orders
    def test_cancel_orders_api_error(self, mocker):
        # Arrange
        mock_get_orders = mocker.patch(
            "brokers.alpaca.orders.trading_client.get_orders",
            side_effect=[
                [
                    mocker.Mock(id="order1", symbol="AAPL")
                ],  # First call returns an open order
                [],  # Second call returns no open orders
            ],
        )
        mock_cancel_order_by_id = mocker.patch(
            "brokers.alpaca.orders.trading_client.cancel_order_by_id",
            side_effect=APIError("TEST API error"),
        )

        # Mock send_email_notification to avoid actual email sending
        mock_send_email = mocker.patch("brokers.alpaca.orders.send_email_notification")

        # Act & Assert
        with pytest.raises(APIError, match="TEST API error"):
            cancel_orders()
        assert mock_get_orders.call_count == 1  # Ensure it stops after the first error
        mock_cancel_order_by_id.assert_called_once_with("order1")
        # Accept any call to send_email_notification with type="FAILURE"
        found = False
        for call in mock_send_email.call_args_list:
            args, kwargs = call
            if "FAILURE" in args or kwargs.get("type") == "FAILURE":
                found = True
                break
        assert found, "send_email_notification was not called with type='FAILURE'"


class TestGetCurrentTrailingStopOrders:

    # Successfully retrieve active trailing stop orders including both long and short positions
    def test_get_current_trailing_stop_orders_success(self, mocker):
        # Arrange
        mock_all_orders = [
            mocker.Mock(id="order1", symbol="AAPL", side="sell", order_type="trailing_stop"),
            mocker.Mock(id="order2", symbol="GOOGL", side="sell", order_type="trailing_stop"),
            mocker.Mock(id="order3", symbol="TSLA", side="buy", order_type="trailing_stop"),  # Short position
            mocker.Mock(id="order4", symbol="MSFT", side="buy", order_type="limit"),  # Not a trailing stop
        ]
        mock_get_orders = mocker.patch(
            "brokers.alpaca.orders.trading_client.get_orders",
            return_value=mock_all_orders,
        )

        # Act
        trailing_stop_orders = get_current_trailing_stop_orders()

        # Assert
        # Should return only trailing stop orders (3 out of 4)
        assert len(trailing_stop_orders) == 3
        assert all(order.order_type == "trailing_stop" for order in trailing_stop_orders)
        mock_get_orders.assert_called_once_with(
            filter=GetOrdersRequest(status=QueryOrderStatus.OPEN)
        )

    # Handle APIError gracefully
    def test_get_current_trailing_stop_orders_api_error(self, mocker):
        # Arrange
        mock_get_orders = mocker.patch(
            "brokers.alpaca.orders.trading_client.get_orders",
            side_effect=APIError("API error occurred"),
        )

        # Act & Assert
        with pytest.raises(APIError, match="API error occurred"):
            get_current_trailing_stop_orders()
        mock_get_orders.assert_called_once_with(
            filter=GetOrdersRequest(status=QueryOrderStatus.OPEN)
        )


class TestPlaceTrailingStopOrder:

    # Successfully place a trailing stop order
    def test_place_trailing_stop_order_success(self, mocker):
        # Arrange
        symbol = "AAPL"
        quantity = 10
        side = "buy"
        trail_percent = "5"

        mock_response = mocker.Mock()
        mock_submit_order = mocker.patch(
            "brokers.alpaca.orders.tradeapi.REST.submit_order",
            return_value=mock_response,
        )

        # Act
        result = place_trailing_stop_order(
            symbol=symbol, quantity=quantity, side=side, trail_percent=trail_percent
        )

        # Assert
        mock_submit_order.assert_called_once_with(
            symbol=symbol,
            qty=quantity,
            side="sell",  # Opposite of the initial order
            type="trailing_stop",
            time_in_force="gtc",
            trail_percent=trail_percent,
        )
        assert result == mock_response

    # Handle APIError when placing a trailing stop order
    def test_place_trailing_stop_order_api_error(self, mocker):
        # Arrange
        symbol = "AAPL"
        quantity = 10
        side = "buy"
        trail_percent = "5"

        mock_submit_order = mocker.patch(
            "brokers.alpaca.orders.tradeapi.REST.submit_order",
            side_effect=APIError("API error occurred"),
        )

        # Act
        result = place_trailing_stop_order(
            symbol=symbol, quantity=quantity, side=side, trail_percent=trail_percent
        )

        # Assert
        mock_submit_order.assert_called_once_with(
            symbol=symbol,
            qty=quantity,
            side="sell",  # Opposite of the initial order
            type="trailing_stop",
            time_in_force="gtc",
            trail_percent=trail_percent,
        )
        assert result is None

    # Successfully place a trailing stop order for short position
    def test_place_trailing_stop_order_short_position_success(self, mocker):
        # Arrange
        symbol = "AAPL"
        quantity = 10
        side = "sell"  # Short position
        trail_percent = "5"

        mock_response = mocker.Mock()
        mock_submit_order = mocker.patch(
            "brokers.alpaca.orders.tradeapi.REST.submit_order",
            return_value=mock_response,
        )

        # Act
        result = place_trailing_stop_order(
            symbol=symbol, quantity=quantity, side=side, trail_percent=trail_percent
        )

        # Assert
        mock_submit_order.assert_called_once_with(
            symbol=symbol,
            qty=quantity,
            side="buy",  # Buy trailing stop for short position
            type="trailing_stop",
            time_in_force="gtc",
            trail_percent=trail_percent,
        )
        assert result == mock_response


class TestGetOrdersToCancel:

    # Successfully identify orders to cancel when there are non-trailing stop orders
    def test_get_orders_to_cancel_success(self, mocker):
        # Arrange
        mock_open_orders = [
            mocker.Mock(id="order1", symbol="AAPL"),
            mocker.Mock(id="order2", symbol="GOOGL"),
        ]
        mock_trailing_stop_orders = [
            mocker.Mock(id="order1", symbol="AAPL")
        ]  # Only one trailing stop order

        mocker.patch("brokers.alpaca.orders.get_orders", return_value=mock_open_orders)
        mocker.patch(
            "brokers.alpaca.orders.get_current_trailing_stop_orders",
            return_value=mock_trailing_stop_orders,
        )

        # Act
        orders_to_cancel = get_orders_to_cancel()

        # Assert
        assert orders_to_cancel == {
            "order2"
        }  # Only non-trailing stop order should be returned

    # Handle case where all orders are trailing stop orders
    def test_get_orders_to_cancel_all_trailing_stop(self, mocker):
        # Arrange
        mock_open_orders = [
            mocker.Mock(id="order1", symbol="AAPL"),
            mocker.Mock(id="order2", symbol="GOOGL"),
        ]
        mock_trailing_stop_orders = (
            mock_open_orders  # All open orders are trailing stop orders
        )

        mocker.patch("brokers.alpaca.orders.get_orders", return_value=mock_open_orders)
        mocker.patch(
            "brokers.alpaca.orders.get_current_trailing_stop_orders",
            return_value=mock_trailing_stop_orders,
        )

        # Act
        orders_to_cancel = get_orders_to_cancel()

        # Assert
        assert orders_to_cancel == set()  # No orders to cancel

    # Handle case where there are no open orders
    def test_get_orders_to_cancel_no_open_orders(self, mocker):
        # Arrange
        mocker.patch("brokers.alpaca.orders.get_orders", return_value=[])
        mocker.patch(
            "brokers.alpaca.orders.get_current_trailing_stop_orders", return_value=[]
        )

        # Act
        orders_to_cancel = get_orders_to_cancel()

        # Assert
        assert orders_to_cancel == set()  # No orders to cancel

    # Handle case where there are no trailing stop orders
    def test_get_orders_to_cancel_no_trailing_stop_orders(self, mocker):
        # Arrange
        mock_open_orders = [
            mocker.Mock(id="order1", symbol="AAPL"),
            mocker.Mock(id="order2", symbol="GOOGL"),
        ]
        mocker.patch("brokers.alpaca.orders.get_orders", return_value=mock_open_orders)
        mocker.patch(
            "brokers.alpaca.orders.get_current_trailing_stop_orders", return_value=[]
        )

        # Act
        orders_to_cancel = get_orders_to_cancel()

        # Assert
        assert orders_to_cancel == {
            "order1",
            "order2",
        }  # All open orders should be canceled


class TestGetOrdersSymbolList:

    # Successfully extracts symbols from a list of orders
    def test_get_orders_symbol_list_success(self, mocker):
        # Arrange
        mock_orders = [
            mocker.Mock(symbol="AAPL"),
            mocker.Mock(symbol="GOOGL"),
            mocker.Mock(symbol="MSFT"),
        ]

        # Act
        result = get_orders_symbol_list(mock_orders)

        # Assert
        assert result == ["AAPL", "GOOGL", "MSFT"]

    # Handles an empty list of orders gracefully
    def test_get_orders_symbol_list_empty(self):
        # Arrange
        mock_orders = []

        # Act
        result = get_orders_symbol_list(mock_orders)

        # Assert
        assert result == []

    # Handles orders with missing 'symbol' attribute
    def test_get_orders_symbol_list_missing_symbol(self, mocker):
        # Arrange
        mock_orders = [
            mocker.Mock(symbol="AAPL"),
            mocker.Mock(symbol="MSFT"),
        ]

        # Act
        result = get_orders_symbol_list(mock_orders)

        # Assert
        assert result == ["AAPL", "MSFT"]


class TestCancelOrderBySymbol:

    # Successfully cancel an order by symbol
    def test_cancel_order_by_symbol_success(self, mocker):
        # Arrange
        symbol = "AAPL"
        mock_order = mocker.Mock(id="order1", symbol=symbol)
        mock_get_orders = mocker.patch(
            "brokers.alpaca.orders.trading_client.get_orders", return_value=[mock_order]
        )
        mock_cancel_order_by_id = mocker.patch(
            "brokers.alpaca.orders.trading_client.cancel_order_by_id"
        )

        # Act
        result = cancel_order_by_symbol(symbol)

        # Assert
        mock_get_orders.assert_called_once_with(
            filter=mocker.ANY  # Ensure the filter is passed
        )
        mock_cancel_order_by_id.assert_called_once_with("order1")
        assert result == "order1"

    # Handle case where no orders are found for the symbol
    def test_cancel_order_by_symbol_no_orders(self, mocker):
        # Arrange
        symbol = "AAPL"
        mocker.patch("brokers.alpaca.orders.trading_client.get_orders", return_value=[])

        # Act
        result = cancel_order_by_symbol(symbol)

        # Assert
        assert result is None

    # Handle APIError when attempting to cancel an order
    def test_cancel_order_by_symbol_api_error(self, mocker):
        # Arrange
        symbol = "AAPL"
        mock_order = mocker.Mock(id="order1", symbol=symbol)
        mocker.patch(
            "brokers.alpaca.orders.trading_client.get_orders", return_value=[mock_order]
        )
        mock_cancel_order_by_id = mocker.patch(
            "brokers.alpaca.orders.trading_client.cancel_order_by_id",
            side_effect=APIError("API error occurred"),
        )

        # Act
        result = cancel_order_by_symbol(symbol)

        # Assert
        mock_cancel_order_by_id.assert_called_once_with("order1")
        assert result is None
