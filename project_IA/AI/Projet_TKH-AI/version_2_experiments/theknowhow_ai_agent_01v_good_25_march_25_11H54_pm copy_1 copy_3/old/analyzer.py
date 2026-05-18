"""
Module d'analyse des sentiments et de classification.
"""
import logging
from textblob import TextBlob
from typing import Dict, Any

class SentimentAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyse le sentiment d'un texte.
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }

    def classify_urgency(self, text: str) -> str:
        """
        Classifie l'urgence d'un post médical.
        """
        urgent_keywords = ["urgent", "emergency", "immediate", "asap", "help"]
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in urgent_keywords):
            return "URGENT"
        return "NON_URGENT" 