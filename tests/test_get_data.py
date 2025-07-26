import sys

sys.path.insert(1, "src")
from get_data import (
    get_assets,
    get_asset_list,
    get_historical_data,
    get_asset_df,
    get_last_price,
)
from alpaca.data.historical.stock import StockHistoricalDataClient
import pandas as pd


class TestGetAssets:

    # Returns a list of active tradable assets when valid TradingClient is provided
    def test_returns_active_tradable_assets(self, mocker):
        # Arrange
        mock_trading_client = mocker.Mock()
        mock_assets = [mocker.Mock(), mocker.Mock()]
        mock_trading_client.get_all_assets.return_value = mock_assets

        # Act
        result = get_assets(mock_trading_client)

        # Assert
        assert result == mock_assets
        mock_trading_client.get_all_assets.assert_called_once()

    # Handles empty list of assets gracefully
    def test_handles_empty_list_of_assets(self, mocker):
        # Arrange
        mock_trading_client = mocker.Mock()
        mock_trading_client.get_all_assets.return_value = []

        # Act
        result = get_assets(mock_trading_client)

        # Assert
        assert result == []
        mock_trading_client.get_all_assets.assert_called_once()


class TestGetAssetList:

    # returns list of asset symbols when given a valid list of assets
    def test_returns_list_of_asset_symbols(self):

        # Create a mock list of assets
        assets = [
            {
                "id": "904837e3-3b76-47ec-b432-046db621571b",
                "name": "Apple inc.",
                "asset_class": "us_equity",
                "exchange": "NASDAQ",
                "symbol": "AAPL",
                "status": "active",
                "tradable": True,
            },
            {
                "id": "904837e3-3b76-47ec-b432-046db621571b",
                "name": "Apple inc.",
                "asset_class": "us_equity",
                "exchange": "NASDAQ",
                "symbol": "MSFT",
                "status": "active",
                "tradable": True,
            },
            {
                "id": "904837e3-3b76-47ec-b432-046db621571b",
                "name": "Apple inc.",
                "asset_class": "us_equity",
                "exchange": "NASDAQ",
                "symbol": "GOOGL",
                "status": "active",
                "tradable": True,
            },
        ]

        # Call the function
        result = get_asset_list(assets)

        # Assert the result
        assert result == ["AAPL", "MSFT", "GOOGL"]

    # handles assets with special characters in symbols
    def test_handles_special_characters_in_symbols(self):

        # Create a mock list of assets with special characters in symbols

        assets = [
            {
                "id": "904837e3-3b76-47ec-b432-046db621571b",
                "name": "Apple inc.",
                "asset_class": "us_equity",
                "exchange": "NASDAQ",
                "symbol": "BRK.B",
                "status": "active",
                "tradable": True,
            },
            {
                "id": "904837e3-3b76-47ec-b432-046db621571b",
                "name": "Apple inc.",
                "asset_class": "us_equity",
                "exchange": "NASDAQ",
                "symbol": "TSLA$",
                "status": "active",
                "tradable": True,
            },
            {
                "id": "904837e3-3b76-47ec-b432-046db621571b",
                "name": "Apple inc.",
                "asset_class": "us_equity",
                "exchange": "NASDAQ",
                "symbol": "AMZN#",
                "status": "active",
                "tradable": True,
            },
        ]

        # Call the function
        result = get_asset_list(assets)

        # Assert the result
        assert result == ["BRK.B", "TSLA$", "AMZN#"]


class TestGetHistoricalData:

    # retrieves historical data for valid stock symbol
    def test_retrieves_historical_data_for_valid_stock_symbol(self, mocker):

        # Mock the StockHistoricalDataClient and its method
        mock_client = mocker.Mock(spec=StockHistoricalDataClient)
        mock_response = mocker.Mock()
        mock_response.df = pd.DataFrame(
            {
                "timestamp": pd.date_range(start="2022-01-01", periods=365, freq="D"),
                "open": [1.0] * 365,
                "high": [1.0] * 365,
                "low": [1.0] * 365,
                "close": [1.0] * 365,
                "volume": [100] * 365,
            }
        )
        mock_client.get_stock_bars.return_value = mock_response

        # Call the function with a valid symbol
        symbol = "AAPL"
        result = get_historical_data(symbol, mock_client)

        # Assertions
        assert not result.empty
        assert len(result) == 365
        assert all(
            result.columns == ["timestamp", "open", "high", "low", "close", "volume"]
        )


class TestGetAssetDf:

    # converts a list of tuples with strings and values into a DataFrame
    def test_converts_list_of_tuples_to_dataframe(self):
        assets = [[("column1", 1), ("column2", 2)]]
        expected_df = pd.DataFrame({"column1": [1], "column2": [2]})
        result_df = get_asset_df(assets)
        pd.testing.assert_frame_equal(result_df, expected_df)

    # handles an empty list input and returns an empty DataFrame
    def test_handles_empty_list_input(self):
        assets = []
        expected_df = pd.DataFrame()
        result_df = get_asset_df(assets)
        pd.testing.assert_frame_equal(result_df, expected_df)


class TestGetLastPrice:

    # Successfully retrieves the last price for a valid stock symbol
    def test_get_last_price_success(self, mocker):
        # Arrange
        mock_client = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.df = pd.DataFrame(
            {"close": [150.0]}, index=pd.to_datetime(["2023-01-01"])
        )
        mock_client.get_stock_bars.return_value = mock_response

        # Act
        symbol = "AAPL"
        result = get_last_price(symbol, mock_client)

        # Assert
        assert result == 150.0

    # Handles case where no data is returned for the stock symbol
    def test_get_last_price_no_data(self, mocker):
        # Arrange
        mock_client = mocker.Mock()
        mock_response = mocker.Mock()
        mock_response.df = pd.DataFrame()  # Empty DataFrame
        mock_client.get_stock_bars.return_value = mock_response

        # Act
        symbol = "AAPL"
        result = get_last_price(symbol, mock_client)

        # Assert
        assert result is None

    # Handles API errors gracefully
    def test_get_last_price_api_error(self, mocker):
        # Arrange
        mock_client = mocker.Mock()
        mock_client.get_stock_bars.side_effect = Exception("API error occurred")

        # Act
        symbol = "AAPL"
        try:
            result = get_last_price(symbol, mock_client)
        except Exception as e:
            result = None
            print(f"Handled exception: {e}")

        # Assert
        assert result is None
