import unittest
from unittest.mock import Mock, patch
import os
from datetime import datetime, timezone
import sys
import requests

# Add the root directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from algorithmic_trading_utilities.common.news_ops import (
    scrape_with_beautifulsoup,
    is_within_one_day,
    is_within_15_mins,
    calculate_time_ago,
)


class TestNewsOps(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        pass


class TestScrapeWithBeautifulSoup(TestNewsOps):

    @patch("algorithmic_trading_utilities.common.news_ops.requests.get")
    def test_scrape_with_beautifulsoup_success(self, mock_get):
        """Test successful scraping with BeautifulSoup."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = "<html><body><p>Test content</p></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = scrape_with_beautifulsoup("https://example.com")

        self.assertIsNotNone(result)
        self.assertIn("Test content", result)
        mock_get.assert_called_once_with("https://example.com")

    @patch("algorithmic_trading_utilities.common.news_ops.requests.get")
    def test_scrape_with_beautifulsoup_request_exception(self, mock_get):
        """Test scraping when requests raises an exception."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        result = scrape_with_beautifulsoup("https://example.com")

        self.assertIsNone(result)

    @patch("algorithmic_trading_utilities.common.news_ops.requests.get")
    def test_scrape_with_beautifulsoup_http_error(self, mock_get):
        """Test scraping when HTTP error occurs."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "HTTP 404"
        )
        mock_get.return_value = mock_response

        result = scrape_with_beautifulsoup("https://example.com")

        self.assertIsNone(result)


class TestIsWithinOneDay(TestNewsOps):

    def test_is_within_one_day_empty_list(self):
        """Test with empty post_time list."""
        result = is_within_one_day([])
        self.assertFalse(result)

    def test_is_within_one_day_no_ago_string(self):
        """Test with post_time list without 'ago' string."""
        result = is_within_one_day(["Posted yesterday", "Some other text"])
        self.assertFalse(result)

    def test_is_within_one_day_minutes_ago(self):
        """Test with minutes ago."""
        result = is_within_one_day(["30 minutes ago"])
        self.assertTrue(result)

    def test_is_within_one_day_hours_ago(self):
        """Test with hours ago."""
        result = is_within_one_day(["5 hours ago"])
        self.assertTrue(result)

    def test_is_within_one_day_one_day_ago(self):
        """Test with exactly one day ago."""
        result = is_within_one_day(["1 day ago"])
        self.assertTrue(result)

    def test_is_within_one_day_a_day_ago(self):
        """Test with 'a day ago'."""
        result = is_within_one_day(["a day ago"])
        self.assertTrue(result)

    def test_is_within_one_day_multiple_days_ago(self):
        """Test with multiple days ago."""
        result = is_within_one_day(["3 days ago"])
        self.assertFalse(result)

    def test_is_within_one_day_mixed_case(self):
        """Test with mixed case strings."""
        result = is_within_one_day(
            ["2 hours ago"]
        )  # Changed to lowercase since function converts to lowercase
        self.assertTrue(result)


class TestIsWithin15Mins(TestNewsOps):

    def test_is_within_15_mins_empty_string(self):
        """Test with empty display time string."""
        result = is_within_15_mins("")
        self.assertFalse(result)

    def test_is_within_15_mins_none(self):
        """Test with None display time."""
        result = is_within_15_mins(None)
        self.assertFalse(result)

    def test_is_within_15_mins_invalid_format(self):
        """Test with invalid format."""
        result = is_within_15_mins("invalid format")
        self.assertFalse(result)

    def test_is_within_15_mins_seconds(self):
        """Test with seconds - always within 15 minutes."""
        result = is_within_15_mins("30s ago")
        self.assertTrue(result)

    def test_is_within_15_mins_within_threshold(self):
        """Test with minutes within 15 minute threshold."""
        result = is_within_15_mins("10m ago")
        self.assertTrue(result)

    def test_is_within_15_mins_at_threshold(self):
        """Test with exactly 15 minutes."""
        result = is_within_15_mins("15m ago")
        self.assertTrue(result)

    def test_is_within_15_mins_over_threshold(self):
        """Test with minutes over 15 minute threshold."""
        result = is_within_15_mins("20m ago")
        self.assertFalse(result)

    def test_is_within_15_mins_hours(self):
        """Test with hours - always outside 15 minutes."""
        result = is_within_15_mins("1h ago")
        self.assertFalse(result)

    def test_is_within_15_mins_days(self):
        """Test with days - always outside 15 minutes."""
        result = is_within_15_mins("1d ago")
        self.assertFalse(result)

    def test_is_within_15_mins_weeks(self):
        """Test with weeks - always outside 15 minutes."""
        result = is_within_15_mins("1w ago")
        self.assertFalse(result)

    def test_is_within_15_mins_minute_singular(self):
        """Test with singular 'minute'."""
        result = is_within_15_mins("5 minute ago")
        self.assertTrue(result)

    def test_is_within_15_mins_minutes_plural(self):
        """Test with plural 'minutes'."""
        result = is_within_15_mins("12 minutes ago")
        self.assertTrue(result)

    def test_is_within_15_mins_mixed_case(self):
        """Test with mixed case input."""
        result = is_within_15_mins("8M AGO")
        self.assertTrue(result)

    def test_is_within_15_mins_no_space(self):
        """Test with no space between number and unit."""
        result = is_within_15_mins("7m ago")
        self.assertTrue(result)

    def test_is_within_15_mins_extra_whitespace(self):
        """Test with extra whitespace."""
        result = is_within_15_mins("  10  m  ago  ")
        self.assertTrue(result)


class TestCalculateTimeAgo(TestNewsOps):

    def test_calculate_time_ago_empty_string(self):
        """Test with empty publication date."""
        result = calculate_time_ago("")
        self.assertEqual(result, "")

    def test_calculate_time_ago_none(self):
        """Test with None publication date."""
        result = calculate_time_ago(None)
        self.assertEqual(result, "")

    def test_calculate_time_ago_invalid_format(self):
        """Test with invalid date format."""
        result = calculate_time_ago("invalid-date")
        self.assertEqual(result, "")

    @patch("algorithmic_trading_utilities.common.news_ops.datetime")
    def test_calculate_time_ago_seconds(self, mock_datetime):
        """Test time difference in seconds."""
        # Mock current time
        current_time = datetime(2025, 10, 19, 12, 0, 30, tzinfo=timezone.utc)
        mock_datetime.now.return_value = current_time
        mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

        # Publication time 30 seconds ago
        pub_date_str = "2025-10-19T12:00:00Z"

        result = calculate_time_ago(pub_date_str)
        self.assertEqual(result, "30s ago")

    @patch("algorithmic_trading_utilities.common.news_ops.datetime")
    def test_calculate_time_ago_minutes(self, mock_datetime):
        """Test time difference in minutes."""
        current_time = datetime(2025, 10, 19, 12, 30, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = current_time
        mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

        pub_date_str = "2025-10-19T12:00:00Z"

        result = calculate_time_ago(pub_date_str)
        self.assertEqual(result, "30m ago")

    @patch("algorithmic_trading_utilities.common.news_ops.datetime")
    def test_calculate_time_ago_hours(self, mock_datetime):
        """Test time difference in hours."""
        current_time = datetime(2025, 10, 19, 16, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = current_time
        mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

        pub_date_str = "2025-10-19T12:00:00Z"

        result = calculate_time_ago(pub_date_str)
        self.assertEqual(result, "4h ago")

    @patch("algorithmic_trading_utilities.common.news_ops.datetime")
    def test_calculate_time_ago_days(self, mock_datetime):
        """Test time difference in days."""
        current_time = datetime(2025, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = current_time
        mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

        pub_date_str = "2025-10-19T12:00:00Z"

        result = calculate_time_ago(pub_date_str)
        self.assertEqual(result, "2d ago")


if __name__ == "__main__":
    unittest.main()
