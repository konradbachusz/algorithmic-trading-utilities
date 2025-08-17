import sys

sys.path.insert(1, "algorithmic_trading_utilities")
from data.yfinance_ops import get_sp500_prices
import pandas as pd
from unittest.mock import patch


class TestGetSp500Prices:

    # returns DataFrame with S&P 500 prices for valid date range
    def test_returns_dataframe_with_sp500_prices(self, mocker):
        # Mock the yfinance.download function
        mock_download = mocker.patch("data.yfinance_ops.yfinance.download")
        mock_data = pd.Series([100.0, 101.0, 102.0], name="Close")
        mock_download.return_value = {"Close": mock_data}

        result = get_sp500_prices("2023-01-01")

        assert isinstance(result, pd.Series)
        assert len(result) == 3
        mock_download.assert_called_once()

    # handles empty response gracefully
    def test_handles_empty_response(self, mocker):
        # Mock the yfinance.download function to return empty data
        mock_download = mocker.patch("data.yfinance_ops.yfinance.download")
        mock_data = pd.Series([], name="Close")
        mock_download.return_value = {"Close": mock_data}

        result = get_sp500_prices("2023-01-01")

        assert isinstance(result, pd.Series)
        assert len(result) == 0
