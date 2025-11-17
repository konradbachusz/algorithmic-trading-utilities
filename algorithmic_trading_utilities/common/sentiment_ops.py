# Use a pipeline as a high-level helper
from transformers import pipeline
import json
import os
import glob
import sys

sys.path.insert(1, "algorithmic_trading_utilities")

try:
    from common.config import sentiment_model
except ImportError:
    from algorithmic_trading_utilities.common.config import sentiment_model

pipe = pipeline(
    "text-classification",
    model=sentiment_model,
)


def analyze_sentiment(text):
    """
    Analyzes the sentiment of the given text using a pre-trained model.

    Args:
        text (str): The text to analyze.

    Returns:
        dict: The sentiment analysis results.
    """
    result = pipe(text)
    return result
