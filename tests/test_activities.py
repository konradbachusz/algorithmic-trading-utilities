import sys

sys.path.insert(1, "algorithmic_trading_utilities")

from brokers.alpaca.activities import get_activities


class TestGetActivities:

    def test_returns_activities(self, mocker):
        # Arrange
        expected = [mocker.Mock(), mocker.Mock()]
        mock_get = mocker.patch(
            "brokers.alpaca.activities.api.get_activities", return_value=expected
        )

        # Act
        result = get_activities()

        # Assert
        assert result == expected
        mock_get.assert_called_once_with(
            activity_types=None,
            until=None,
            after=None,
            direction=None,
            date=None,
            page_size=None,
            page_token=None,
        )

    def test_passes_filters_through(self, mocker):
        # Arrange
        mock_get = mocker.patch("brokers.alpaca.activities.api.get_activities")

        # Act
        get_activities(
            activity_types=["FILL", "DIV"],
            after="2025-01-01T00:00:00Z",
            until="2025-01-31T00:00:00Z",
            direction="asc",
            page_size=50,
            page_token="abc",
        )

        # Assert
        mock_get.assert_called_once_with(
            activity_types=["FILL", "DIV"],
            until="2025-01-31T00:00:00Z",
            after="2025-01-01T00:00:00Z",
            direction="asc",
            date=None,
            page_size=50,
            page_token="abc",
        )
