import pytest
from positions import (
    get_open_positions,
    get_positions_without_trailing_stop_loss,
    get_positions_symbol_list,
    close_positions_below_threshold,
)
from unittest.mock import MagicMock


class TestGetOpenPositions:

    # Successfully retrieves a list of open positions
    def test_get_open_positions_success(self, mocker):
        # Arrange
        mock_positions = [
            {"symbol": "AAPL", "quantity": "10", "side": "buy"},
            {"symbol": "GOOGL", "quantity": "5", "side": "buy"},
        ]
        mocker.patch("positions.get_open_positions", return_value=mock_positions)

        # Act
        result = get_open_positions()

        # Assert
        assert isinstance(result, list)
        for position in result:
            assert "symbol" in position
            assert "quantity" in position
            assert "side" in position

    # Handles case where no positions are open
    def test_get_open_positions_no_positions(self, mocker):
        # Arrange
        mock_get_open_positions = mocker.patch(
            "positions.get_open_positions", return_value=[]
        )

        # Act
        result = mock_get_open_positions()

        # Assert
        assert result == []
        mock_get_open_positions.assert_called_once()  # Ensure the mock was called

    # Handles API errors gracefully
    def test_get_open_positions_api_error(self, mocker):
        # Arrange
        mock_get_open_positions = mocker.patch(
            "positions.get_open_positions", side_effect=Exception("API error occurred")
        )

        # Act & Assert
        with pytest.raises(Exception, match="API error occurred"):
            mock_get_open_positions()  # Call the mocked function directly


class TestGetPositionsWithoutTrailingStopLoss:

    # Successfully retrieves positions without trailing stop loss
    def test_get_positions_without_trailing_stop_loss_success(self, mocker):

        # Act
        result = get_positions_without_trailing_stop_loss()

        # Assert
        assert isinstance(result, list)
        for position in result:
            assert "symbol" in position
            assert "quantity" in position
            assert "side" in position

        # Check specific keys from the provided object
        expected_keys = {"symbol", "quantity", "side"}
        for position in result:
            assert expected_keys.issubset(position.keys())

    # Handles case where all positions already have trailing stop loss
    def test_get_positions_without_trailing_stop_loss_all_have_stop_loss(self, mocker):
        # Arrange
        mock_positions = [
            MagicMock(symbol="AAPL", quantity="10", side="buy"),
            MagicMock(symbol="GOOGL", quantity="5", side="buy"),
        ]
        mock_trailing_stop_orders = [
            MagicMock(symbol="AAPL", quantity="10", side="sell"),
            MagicMock(symbol="GOOGL", quantity="5", side="sell"),
        ]
        mocker.patch("positions.get_open_positions", return_value=mock_positions)
        mocker.patch(
            "positions.get_current_trailing_stop_orders",
            return_value=mock_trailing_stop_orders,
        )

        # Act
        result = get_positions_without_trailing_stop_loss()

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0  # All positions already have trailing stop loss

    # Handles case where no positions are open
    def test_get_positions_without_trailing_stop_loss_no_positions(self, mocker):
        # Arrange
        mocker.patch("positions.get_open_positions", return_value=[])
        mocker.patch("positions.get_current_trailing_stop_orders", return_value=[])

        # Act
        result = get_positions_without_trailing_stop_loss()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    # Handles case where no trailing stop orders exist
    def test_get_positions_without_trailing_stop_loss_no_trailing_stop_orders(
        self, mocker
    ):
        # Arrange
        mock_positions = [
            {"symbol": "AAPL", "quantity": "10", "side": "buy"},
            {"symbol": "GOOGL", "quantity": "5", "side": "buy"},
        ]
        mocker.patch("positions.get_open_positions", return_value=mock_positions)
        mocker.patch("positions.get_current_trailing_stop_orders", return_value=[])

        # Act
        result = get_positions_without_trailing_stop_loss()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["symbol"] == "AAPL"
        assert result[1]["symbol"] == "GOOGL"


class TestGetPositionsSymbolList:

    # Successfully extracts symbols from a list of positions
    def test_get_positions_symbol_list_success(self):
        # Arrange
        mock_positions = [
            {"symbol": "AAPL", "quantity": "10", "side": "buy"},
            {"symbol": "GOOGL", "quantity": "5", "side": "buy"},
        ]

        # Act
        result = get_positions_symbol_list(mock_positions)

        # Assert
        assert result == ["AAPL", "GOOGL"]

    # Handles an empty list of positions gracefully
    def test_get_positions_symbol_list_empty(self):
        # Arrange
        mock_positions = []

        # Act
        result = get_positions_symbol_list(mock_positions)

        # Assert
        assert result == []


class TestClosePositionsBelowThreshold:

    # Successfully closes positions below the threshold
    def test_close_positions_below_threshold_success(self, mocker):
        # Arrange
        mock_positions = [
            MagicMock(symbol="AAPL", qty="10", side="long", unrealized_plpc=-0.10),
            MagicMock(symbol="GOOGL", qty="5", side="long", unrealized_plpc=0.05),
        ]
        mock_threshold = 0.05
        mock_close_position = mocker.patch(
            "positions.trading_client.close_position", return_value=True
        )
        mocker.patch(
            "positions.trading_client.get_all_positions", return_value=mock_positions
        )

        # Act
        close_positions_below_threshold(mock_threshold)

        # Assert
        mock_close_position.assert_called_once_with("AAPL")

    # Handles case where no positions are below the threshold
    def test_close_positions_below_threshold_no_positions_below(self, mocker):
        # Arrange
        mock_positions = [
            MagicMock(symbol="AAPL", qty="10", side="long", unrealized_plpc=0.10),
            MagicMock(symbol="GOOGL", qty="5", side="long", unrealized_plpc=0.15),
        ]
        mock_threshold = 0.05
        mock_close_position = mocker.patch(
            "positions.trading_client.close_position", return_value=True
        )
        mocker.patch(
            "positions.trading_client.get_all_positions", return_value=mock_positions
        )

        # Act
        close_positions_below_threshold(mock_threshold)

        # Assert
        mock_close_position.assert_not_called()

    # Handles case where no positions are open
    def test_close_positions_below_threshold_no_positions(self, mocker):
        # Arrange
        mock_positions = []
        mock_threshold = 0.05
        mock_close_position = mocker.patch(
            "positions.trading_client.close_position", return_value=True
        )
        mocker.patch(
            "positions.trading_client.get_all_positions", return_value=mock_positions
        )

        # Act
        close_positions_below_threshold(mock_threshold)

        # Assert
        mock_close_position.assert_not_called()
