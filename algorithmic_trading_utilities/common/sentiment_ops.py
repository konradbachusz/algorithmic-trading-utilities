# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

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

print(analyze_sentiment("The stock market is performing exceptionally well today!"))