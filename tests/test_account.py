import sys

sys.path.insert(1, "algorithmic_trading_utilities")

from brokers.alpaca.account import get_account, get_balances


class TestAccountHelpers:

    def test_get_account_delegates_to_trading_client(self, mocker):
        expected = mocker.Mock()
        mock_get = mocker.patch(
            "brokers.alpaca.account.trading_client.get_account", return_value=expected
        )

        result = get_account()

        assert result == expected
        mock_get.assert_called_once_with()

    def test_get_balances_extracts_common_fields(self, mocker):
        account = mocker.Mock(
            cash="1000",
            buying_power="2000",
            equity="1500",
            portfolio_value="1500",
            status="ACTIVE",
            currency="USD",
        )
        mocker.patch("brokers.alpaca.account.get_account", return_value=account)

        result = get_balances()

        assert result["cash"] == "1000"
        assert result["buying_power"] == "2000"
        assert result["equity"] == "1500"
        assert result["portfolio_value"] == "1500"
        assert result["status"] == "ACTIVE"
        assert result["currency"] == "USD"

    def test_get_balances_handles_dict_account(self, mocker):
        account = {
            "cash": "10",
            "buying_power": "20",
            "equity": "15",
            "portfolio_value": "15",
            "status": "ACTIVE",
        }
        mocker.patch("brokers.alpaca.account.get_account", return_value=account)

        result = get_balances()

        assert result["cash"] == "10"
        assert result["buying_power"] == "20"
        assert result["equity"] == "15"
        assert result["portfolio_value"] == "15"
        assert result["status"] == "ACTIVE"
