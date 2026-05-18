"""
Tests pour l'analyseur de sentiment multilingue.
"""

import pytest
import sys
import os

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from phase1_data_collection.nlp.sentiment_analyzer import SentimentAnalyzer

def test_french_sentiment():
    """Test l'analyse de sentiment en français."""
    analyzer = SentimentAnalyzer()
    
    # Test positif
    result = analyzer.analyze("Je suis très heureux et content aujourd'hui !")
    assert result["language"] == "fr"
    assert result["label"] == "positif"
    assert result["polarity"] > 0
    assert result["confidence"] > 0.5
    
    # Test négatif
    result = analyzer.analyze("Je suis triste et inquiet pour ma santé.")
    assert result["language"] == "fr"
    assert result["label"] == "négatif"
    assert result["polarity"] < 0
    assert result["confidence"] > 0.5
    
    # Test neutre
    result = analyzer.analyze("Le temps est nuageux aujourd'hui.")
    assert result["language"] == "fr"
    assert result["label"] == "neutre"
    assert abs(result["polarity"]) < 0.1

def test_english_sentiment():
    """Test l'analyse de sentiment en anglais."""
    analyzer = SentimentAnalyzer()
    
    # Test positif
    result = analyzer.analyze("I am very happy and satisfied today!")
    assert result["language"] == "en"
    assert result["label"] == "positive"
    assert result["polarity"] > 0
    assert result["confidence"] > 0.5
    
    # Test négatif
    result = analyzer.analyze("I am worried and anxious about my health.")
    assert result["language"] == "en"
    assert result["label"] == "negative"
    assert result["polarity"] < 0
    assert result["confidence"] > 0.5
    
    # Test neutre
    result = analyzer.analyze("The weather is cloudy today.")
    assert result["language"] == "en"
    assert result["label"] == "neutral"
    assert abs(result["polarity"]) < 0.1

def test_negation():
    """Test la détection des négations."""
    analyzer = SentimentAnalyzer()
    
    # Test négation en français
    result = analyzer.analyze("Je ne suis pas heureux du tout.")
    assert result["language"] == "fr"
    assert result["label"] == "négatif"
    
    # Test négation en anglais
    result = analyzer.analyze("I am not happy at all.")
    assert result["language"] == "en"
    assert result["label"] == "negative"

def test_subjectivity():
    """Test l'analyse de la subjectivité."""
    analyzer = SentimentAnalyzer()
    
    # Test subjectivité en français
    result = analyzer.analyze("Je pense que c'est une bonne idée.")
    assert result["language"] == "fr"
    assert result["subjectivity"] > 0.5
    
    # Test subjectivité en anglais
    result = analyzer.analyze("I believe this is a good idea.")
    assert result["language"] == "en"
    assert result["subjectivity"] > 0.5

def test_batch_analysis():
    """Test l'analyse par lots."""
    analyzer = SentimentAnalyzer()
    texts = [
        "Je suis très heureux !",
        "I am very happy!",
        "Je ne suis pas content.",
        "I am not satisfied."
    ]
    
    results = analyzer.analyze_batch(texts)
    assert len(results) == 4
    
    # Vérification des langues
    assert results[0]["language"] == "fr"
    assert results[1]["language"] == "en"
    assert results[2]["language"] == "fr"
    assert results[3]["language"] == "en" 