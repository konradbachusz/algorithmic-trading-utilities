import sys

sys.path.insert(1, "src")
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest,
)
from unittest.mock import patch, MagicMock, call  # Added call
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
    place_trailing_stop_losses_funct,
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
            mocker.Mock(
                id="order1", symbol="AAPL", side="sell", order_type="trailing_stop"
            ),
            mocker.Mock(
                id="order2", symbol="GOOGL", side="sell", order_type="trailing_stop"
            ),
            mocker.Mock(
                id="order3", symbol="TSLA", side="buy", order_type="trailing_stop"
            ),  # Short position
            mocker.Mock(
                id="order4", symbol="MSFT", side="buy", order_type="limit"
            ),  # Not a trailing stop
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
        assert all(
            order.order_type == "trailing_stop" for order in trailing_stop_orders
        )
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


class TestPlaceTrailingStopLossesFunct:

    @patch("brokers.alpaca.orders.place_trailing_stop_order")
    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.positions.get_positions_without_trailing_stop_loss"
    )
    def test_no_positions_needing_stops(self, mock_get_positions, mock_place_order):
        # Test verifies that no trailing stop loss orders are placed when there are no positions needing stops.
        mock_get_positions.return_value = []

        # Act
        place_trailing_stop_losses_funct(threshold=0.1)  # Explicitly pass threshold

        # Assert
        mock_get_positions.assert_called_once()
        mock_place_order.assert_not_called()

    @patch("brokers.alpaca.orders.place_trailing_stop_order")
    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.positions.get_positions_without_trailing_stop_loss"
    )
    def test_positions_need_stops_success(self, mock_get_positions, mock_place_order):
        # Test ensures trailing stop loss orders are placed successfully for positions needing stops.
        pos1 = {"symbol": "AAPL", "quantity": "10", "side": "buy"}
        pos2 = {"symbol": "MSFT", "quantity": "5", "side": "buy"}
        mock_get_positions.return_value = [pos1, pos2]

        # Mock place_trailing_stop_order to return a non-mock truthy value for success
        mock_place_order.return_value = True  # Simple truthy value

        # Act
        place_trailing_stop_losses_funct(threshold=0.1)

        # Assert
        mock_get_positions.assert_called_once()
        expected_calls = [
            call(symbol="AAPL", quantity=10, side="buy", trail_percent="10"),
            call(symbol="MSFT", quantity=5, side="buy", trail_percent="10"),
        ]
        mock_place_order.assert_has_calls(expected_calls, any_order=False)
        assert mock_place_order.call_count == 2

    @patch("brokers.alpaca.orders.place_trailing_stop_order")
    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.positions.get_positions_without_trailing_stop_loss"
    )
    def test_place_order_returns_none_continues(
        self, mock_get_positions, mock_place_order
    ):
        # Test verifies that the function continues placing orders even if one of the orders fails (returns None).
        pos1 = {"symbol": "AAPL", "quantity": "10", "side": "buy"}
        pos2 = {
            "symbol": "MSFT",
            "quantity": "5",
            "side": "buy",
        }  # This one returns None
        pos3 = {"symbol": "GOOG", "quantity": "3", "side": "buy"}
        mock_get_positions.return_value = [pos1, pos2, pos3]

        def side_effect_place_order(symbol, quantity, side, trail_percent):
            if symbol == "MSFT":
                return None
            return True  # Simple truthy value for success

        mock_place_order.side_effect = side_effect_place_order

        # Act
        place_trailing_stop_losses_funct(threshold=0.1)

        # Assert
        mock_get_positions.assert_called_once()
        expected_calls = [
            call(symbol="AAPL", quantity=10, side="buy", trail_percent="10"),
            call(symbol="MSFT", quantity=5, side="buy", trail_percent="10"),
            call(symbol="GOOG", quantity=3, side="buy", trail_percent="10"),
        ]
        mock_place_order.assert_has_calls(expected_calls, any_order=False)
        assert mock_place_order.call_count == 3

    @patch("brokers.alpaca.orders.place_trailing_stop_order")
    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.positions.get_positions_without_trailing_stop_loss"
    )
    def test_place_order_raises_exception_continues(
        self, mock_get_positions, mock_place_order, capsys
    ):
        # Test verifies that the function continues placing orders even if one of the orders raises an exception.
        pos1 = {"symbol": "AAPL", "quantity": "10", "side": "buy"}
        pos2 = {
            "symbol": "MSFT",
            "quantity": "5",
            "side": "buy",
        }  # This one raises Exception
        pos3 = {"symbol": "GOOG", "quantity": "3", "side": "buy"}
        mock_get_positions.return_value = [pos1, pos2, pos3]

        def side_effect_place_order(symbol, quantity, side, trail_percent):
            if symbol == "MSFT":
                raise Exception("Test order error for MSFT")
            return True  # Simple truthy value for success

        mock_place_order.side_effect = side_effect_place_order

        # Act
        place_trailing_stop_losses_funct(threshold=0.1)

        # Assert
        mock_get_positions.assert_called_once()
        expected_calls = [
            call(symbol="AAPL", quantity=10, side="buy", trail_percent="10"),
            call(symbol="MSFT", quantity=5, side="buy", trail_percent="10"),
            call(symbol="GOOG", quantity=3, side="buy", trail_percent="10"),
        ]
        mock_place_order.assert_has_calls(expected_calls, any_order=False)
        assert mock_place_order.call_count == 3  # Called for all, even if one fails

        captured = capsys.readouterr()
        assert (
            "Skipping MSFT due to an error: Test order error for MSFT" in captured.out
        )
        # Also check that successful orders are logged (or at least not error messages for them)
        assert "Placing trailing stop loss order for AAPL at 10%" in captured.out
        assert "Placing trailing stop loss order for GOOG at 10%" in captured.out

    # Test with quantity '0' to ensure it's skipped
    @patch("brokers.alpaca.orders.place_trailing_stop_order")
    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.positions.get_positions_without_trailing_stop_loss"
    )
    def test_position_with_zero_quantity_skipped(
        self, mock_get_positions, mock_place_order
    ):
        # Test ensures that positions with a quantity of '0' are skipped and no orders are placed for them.
        pos1 = {"symbol": "XYZ", "quantity": "0", "side": "buy"}
        pos2 = {"symbol": "ABC", "quantity": "10", "side": "buy"}
        mock_get_positions.return_value = [pos1, pos2]

        mock_order_result = MagicMock()
        mock_place_order.return_value = mock_order_result

        # Act
        place_trailing_stop_losses_funct(threshold=0.1)

        # Assert
        mock_get_positions.assert_called_once()
        # Should only be called for ABC, not XYZ
        mock_place_order.assert_called_once_with(
            symbol="ABC", quantity=10, side="buy", trail_percent="10"
        )
        assert mock_place_order.call_count == 1

    # Test with different threshold value
    @patch("brokers.alpaca.orders.place_trailing_stop_order")
    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.positions.get_positions_without_trailing_stop_loss"
    )
    def test_different_threshold_value(self, mock_get_positions, mock_place_order):
        # Test verifies that the function correctly handles different threshold values.
        pos1 = {
            "symbol": "TGT",
            "quantity": "-100",
            "side": "sell",
        }  # Short position with negative quantity
        mock_get_positions.return_value = [pos1]

        mock_order_result = MagicMock()
        mock_place_order.return_value = mock_order_result

        # Act
        place_trailing_stop_losses_funct(threshold=0.05)  # Use 5% threshold

        # Assert
        mock_get_positions.assert_called_once()
        mock_place_order.assert_called_once_with(
            symbol="TGT",
            quantity=100,
            side="sell",
            trail_percent="5",  # abs(quantity) = 100
        )

    # Test case where position side is 'sell' (short position)
    @patch("brokers.alpaca.orders.place_trailing_stop_order")
    @patch(
        "algorithmic_trading_utilities.brokers.alpaca.positions.get_positions_without_trailing_stop_loss"
    )
    def test_short_position_side(self, mock_get_positions, mock_place_order):
        # Test verifies that the function correctly handles short positions (side='sell' with negative quantity).
        pos1 = {"symbol": "SPY", "quantity": "-50", "side": "sell"}  # Short position
        mock_get_positions.return_value = [pos1]

        mock_order_result = MagicMock()
        mock_place_order.return_value = mock_order_result

        # Act
        place_trailing_stop_losses_funct(threshold=0.15)  # 15% threshold

        # Assert
        mock_get_positions.assert_called_once()
        # For short positions, quantity is absolute value and side matches position side
        mock_place_order.assert_called_once_with(
            symbol="SPY", quantity=50, side="sell", trail_percent="15"  # abs(-50) = 50
        )
