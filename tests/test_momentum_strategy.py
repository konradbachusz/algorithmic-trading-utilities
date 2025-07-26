import pandas as pd
import sys
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# Load environment variables from .env file
load_dotenv()

sys.path.insert(1, "src")
from strategies.momentum_strategy import get_tradable_gainers, get_momentum_trades_list

api_key = os.environ["PAPER_KEY"]
secret_key = os.environ["PAPER_SECRET"]

# setup clients
trading_client = TradingClient(
    api_key=api_key, secret_key=secret_key, paper=True, url_override=None
)


class TestGetTradableGainers:

    # Correctly merges dataframes when both have matching symbols and exchanges
    def test_correct_merge_with_matching_symbols_and_exchanges(self):
        assets_data = {
            "symbol": ["AAPL", "GOOGL"],
            "name": ["Apple Inc.", "Alphabet Inc."],
            "exchange": ["NASDAQ", "NASDAQ"],
        }
        gainers_data = {
            "symbol": ["AAPL", "GOOGL"],
            "shortName": ["Apple", "Google"],
            "exchange": ["NMS", "NMS"],
        }
        assets_df = pd.DataFrame(assets_data)
        gainers_df = pd.DataFrame(gainers_data)

        result_df = get_tradable_gainers(assets_df, gainers_df)

        expected_data = {
            "symbol": ["AAPL", "GOOGL"],
            "exchange": ["NASDAQ", "NASDAQ"],
            "shortName": ["Apple", "Google"],
            "name": ["Apple Inc.", "Alphabet Inc."],
        }
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result_df, expected_df)

    # Handles empty dataframes without errors
    def test_handles_empty_dataframes(self):
        assets_df = pd.DataFrame(columns=["symbol", "name", "exchange"])
        gainers_df = pd.DataFrame(columns=["symbol", "shortName", "exchange"])

        result_df = get_tradable_gainers(assets_df, gainers_df)

        expected_df = pd.DataFrame(columns=["symbol", "exchange", "shortName", "name"])

        pd.testing.assert_frame_equal(result_df, expected_df)


class TestGetMomentumTradesList:

    # Returns a list of momentum trades for valid trading client and check if the right keys are there
    def test_returns_momentum_trades_for_valid_client(self, mocker):
        # Mocking the get_stock_gainers_table function
        mock_gainers_data = pd.DataFrame(
            {
                "exchange": ["NASDAQ", "NASDAQ"],
                "symbol": ["AAPL", "GOOGL"],
                "shortName": ["Apple", "Google"],
                "regularMarketChangePercent": [1.5, 2.3],
                "fiftyDayAverageChangePercent": [0.8, 1.2],
            }
        )
        mocker.patch(
            "strategies.momentum_strategy.get_stock_gainers_table",
            return_value=mock_gainers_data,
        )

        # Mocking get_assets and get_asset_df
        mock_assets_data = pd.DataFrame(
            {
                "symbol": ["AAPL", "GOOGL", "MSFT"],
                "name": ["Apple Inc.", "Alphabet Inc.", "Microsoft Corp."],
                "exchange": ["NASDAQ", "NASDAQ", "NASDAQ"],
            }
        )
        mocker.patch(
            "strategies.momentum_strategy.get_assets", return_value=mock_assets_data
        )
        mocker.patch(
            "strategies.momentum_strategy.get_asset_df", return_value=mock_assets_data
        )

        # Mocking get_orders_symbol_list and get_positions_symbol_list
        mocker.patch(
            "strategies.momentum_strategy.get_orders_symbol_list", return_value=[]
        )
        mocker.patch(
            "strategies.momentum_strategy.get_positions_symbol_list", return_value=[]
        )

        # Act
        trades_list = get_momentum_trades_list(trading_client)

        # Assert
        expected_keys = ["symbol", "notional", "side", "type", "time_in_force"]
        trades_list_keys = list(trades_list[0].keys())
        assert trades_list_keys == expected_keys
