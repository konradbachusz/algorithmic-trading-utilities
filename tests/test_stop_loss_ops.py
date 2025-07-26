import sys

sys.path.insert(1, "src")

from unittest.mock import patch, MagicMock, call  # Added call
from stop_loss_ops import place_trailing_stop_losses_funct


class TestPlaceTrailingStopLossesFunct:

    @patch("stop_loss_ops.place_trailing_stop_order")
    @patch("stop_loss_ops.get_positions_without_trailing_stop_loss")
    def test_no_positions_needing_stops(self, mock_get_positions, mock_place_order):
        # Test verifies that no trailing stop loss orders are placed when there are no positions needing stops.
        mock_get_positions.return_value = []

        # Act
        place_trailing_stop_losses_funct(threshold=0.1)  # Explicitly pass threshold

        # Assert
        mock_get_positions.assert_called_once()
        mock_place_order.assert_not_called()

    @patch("stop_loss_ops.place_trailing_stop_order")
    @patch("stop_loss_ops.get_positions_without_trailing_stop_loss")
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
            call(symbol="AAPL", quantity="10", side="buy", trail_percent="10"),
            call(symbol="MSFT", quantity="5", side="buy", trail_percent="10"),
        ]
        mock_place_order.assert_has_calls(expected_calls, any_order=False)
        assert mock_place_order.call_count == 2

    @patch("stop_loss_ops.place_trailing_stop_order")
    @patch("stop_loss_ops.get_positions_without_trailing_stop_loss")
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
            call(symbol="AAPL", quantity="10", side="buy", trail_percent="10"),
            call(symbol="MSFT", quantity="5", side="buy", trail_percent="10"),
            call(symbol="GOOG", quantity="3", side="buy", trail_percent="10"),
        ]
        mock_place_order.assert_has_calls(expected_calls, any_order=False)
        assert mock_place_order.call_count == 3

    @patch("stop_loss_ops.place_trailing_stop_order")
    @patch("stop_loss_ops.get_positions_without_trailing_stop_loss")
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
            call(symbol="AAPL", quantity="10", side="buy", trail_percent="10"),
            call(symbol="MSFT", quantity="5", side="buy", trail_percent="10"),
            call(symbol="GOOG", quantity="3", side="buy", trail_percent="10"),
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
    @patch("stop_loss_ops.place_trailing_stop_order")
    @patch("stop_loss_ops.get_positions_without_trailing_stop_loss")
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
            symbol="ABC", quantity="10", side="buy", trail_percent="10"
        )
        assert mock_place_order.call_count == 1

    # Test with different threshold value
    @patch("stop_loss_ops.place_trailing_stop_order")
    @patch("stop_loss_ops.get_positions_without_trailing_stop_loss")
    def test_different_threshold_value(self, mock_get_positions, mock_place_order):
        # Test verifies that the function correctly handles different threshold values.
        pos1 = {"symbol": "TGT", "quantity": "100", "side": "sell"}
        mock_get_positions.return_value = [pos1]

        mock_order_result = MagicMock()
        mock_place_order.return_value = mock_order_result

        # Act
        place_trailing_stop_losses_funct(threshold=0.05)  # Use 5% threshold

        # Assert
        mock_get_positions.assert_called_once()
        mock_place_order.assert_called_once_with(
            symbol="TGT", quantity="100", side="sell", trail_percent="5"
        )

    # Test case where position side is 'short' (maps to 'sell' for order placement, though function uses it directly)
    @patch("stop_loss_ops.place_trailing_stop_order")
    @patch("stop_loss_ops.get_positions_without_trailing_stop_loss")
    def test_short_position_side(self, mock_get_positions, mock_place_order):
        # Test verifies that the function correctly handles positions with a 'short' side.
        pos1 = {"symbol": "SPY", "quantity": "50", "side": "short"}  # 'short' side
        mock_get_positions.return_value = [pos1]

        mock_order_result = MagicMock()
        mock_place_order.return_value = mock_order_result

        # Act
        place_trailing_stop_losses_funct(threshold=0.15)  # 15% threshold

        # Assert
        mock_get_positions.assert_called_once()
        # The 'side' in place_trailing_stop_order is the position's side.
        # The place_trailing_stop_order function itself handles if it needs to be opposite for the actual TSL order type.
        mock_place_order.assert_called_once_with(
            symbol="SPY", quantity="50", side="short", trail_percent="15"
        )
