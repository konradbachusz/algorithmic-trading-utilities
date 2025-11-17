import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from algorithmic_trading_utilities.common.sentiment_ops import analyze_sentiment


class TestAnalyzeSentiment(unittest.TestCase):
    """Tests for the analyze_sentiment function."""

    @patch("algorithmic_trading_utilities.common.sentiment_ops.pipe")
    def test_analyze_sentiment_positive(self, mock_pipe):
        """Test sentiment analysis with positive sentiment text."""
        # Mock the pipeline output for positive sentiment
        mock_pipe.return_value = [{"label": "positive", "score": 0.95}]

        text = "The company reported record profits and strong growth this quarter."
        result = analyze_sentiment(text)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "positive")
        self.assertEqual(result[0]["score"], 0.95)
        mock_pipe.assert_called_once_with(text)

    @patch("algorithmic_trading_utilities.common.sentiment_ops.pipe")
    def test_analyze_sentiment_negative(self, mock_pipe):
        """Test sentiment analysis with negative sentiment text."""
        # Mock the pipeline output for negative sentiment
        mock_pipe.return_value = [{"label": "negative", "score": 0.88}]

        text = "The company faces bankruptcy and massive losses."
        result = analyze_sentiment(text)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "negative")
        self.assertEqual(result[0]["score"], 0.88)
        mock_pipe.assert_called_once_with(text)

    @patch("algorithmic_trading_utilities.common.sentiment_ops.pipe")
    def test_analyze_sentiment_neutral(self, mock_pipe):
        """Test sentiment analysis with neutral sentiment text."""
        # Mock the pipeline output for neutral sentiment
        mock_pipe.return_value = [{"label": "neutral", "score": 0.75}]

        text = "The company released its quarterly report."
        result = analyze_sentiment(text)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "neutral")
        self.assertEqual(result[0]["score"], 0.75)
        mock_pipe.assert_called_once_with(text)

    @patch("algorithmic_trading_utilities.common.sentiment_ops.pipe")
    def test_analyze_sentiment_empty_string(self, mock_pipe):
        """Test sentiment analysis with empty string."""
        # Mock the pipeline output
        mock_pipe.return_value = [{"label": "neutral", "score": 0.5}]

        text = ""
        result = analyze_sentiment(text)

        self.assertIsNotNone(result)
        mock_pipe.assert_called_once_with(text)

    @patch("algorithmic_trading_utilities.common.sentiment_ops.pipe")
    def test_analyze_sentiment_long_text(self, mock_pipe):
        """Test sentiment analysis with a longer text."""
        # Mock the pipeline output
        mock_pipe.return_value = [{"label": "positive", "score": 0.82}]

        text = """
        The financial markets showed strong performance today with major indices 
        reaching new highs. Investors are optimistic about the economic outlook 
        following positive earnings reports from several major corporations.
        """
        result = analyze_sentiment(text)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "positive")
        mock_pipe.assert_called_once_with(text)

    @patch("algorithmic_trading_utilities.common.sentiment_ops.pipe")
    def test_analyze_sentiment_returns_list_of_dicts(self, mock_pipe):
        """Test that analyze_sentiment returns a list of dict structures."""
        # Mock the pipeline output
        mock_pipe.return_value = [{"label": "positive", "score": 0.9}]

        text = "Great news for investors."
        result = analyze_sentiment(text)

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("label", result[0])
        self.assertIn("score", result[0])

    @patch("algorithmic_trading_utilities.common.sentiment_ops.pipe")
    def test_analyze_sentiment_special_characters(self, mock_pipe):
        """Test sentiment analysis with special characters."""
        # Mock the pipeline output
        mock_pipe.return_value = [{"label": "neutral", "score": 0.6}]

        text = "Stock price: $123.45 (+5.2%) 📈"
        result = analyze_sentiment(text)

        self.assertIsNotNone(result)
        mock_pipe.assert_called_once_with(text)

    @patch("algorithmic_trading_utilities.common.sentiment_ops.pipe")
    def test_analyze_sentiment_multiple_sentences(self, mock_pipe):
        """Test sentiment analysis with multiple sentences."""
        # Mock the pipeline output
        mock_pipe.return_value = [{"label": "positive", "score": 0.87}]

        text = "The stock is performing well. Analysts are bullish on future prospects."
        result = analyze_sentiment(text)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "positive")
        self.assertAlmostEqual(result[0]["score"], 0.87)
        mock_pipe.assert_called_once_with(text)

