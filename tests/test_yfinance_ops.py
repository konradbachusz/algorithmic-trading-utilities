import sys

sys.path.insert(1, "src")
from yfinance_ops import get_stock_gainers_table


class TestGetStockGainersTable:

    # returns DataFrame with correct columns
    def test_returns_dataframe_with_correct_columns(self, mocker):

        # Mock the Screener class and its method
        mock_screener = mocker.patch("yfinance_ops.Screener")
        mock_screener_instance = mock_screener.return_value
        mock_screener_instance.get_screeners.return_value = {
            "day_gainers": {
                "quotes": [
                    {
                        "exchange": "NYSE",
                        "symbol": "AAPL",
                        "shortName": "Apple Inc.",
                        "regularMarketChangePercent": 2.5,
                        "fiftyDayAverageChangePercent": 1.2,
                        "marketCap": 20000000000,
                    }
                ]
            }
        }

        result = get_stock_gainers_table()
        expected_columns = [
            "exchange",
            "symbol",
            "shortName",
            "regularMarketChangePercent",
            "fiftyDayAverageChangePercent",
        ]

        assert list(result.columns) == expected_columns

    # handles empty response from Yahoo Screener API
    def test_handles_empty_response_from_yahoo_screener_api(self, mocker):

        # Mock the Screener class and its method
        mock_screener = mocker.patch("yfinance_ops.Screener")
        mock_screener_instance = mock_screener.return_value
        mock_screener_instance.get_screeners.return_value = {
            "day_gainers": {"quotes": []}
        }

        result = get_stock_gainers_table()

        assert result.empty
