from transformers import pipeline
from typing import Optional

class SentimentAnalyzer:
    def __init__(self):
        # Initialize the sentiment analysis pipeline
        self.analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def analyze(self, text: str) -> str:
        try:
            if not text.strip():
                return "NEUTRAL"
                
            result = self.analyzer(text[:512])  # Limit to 512 tokens
            return result[0]["label"]
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return "NEUTRAL"