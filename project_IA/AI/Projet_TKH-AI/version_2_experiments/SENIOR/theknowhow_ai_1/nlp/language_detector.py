"""
Module de détection de langue pour les textes.
"""

import langdetect
from config.settings import logger

def detect_language(text: str) -> str:
    """
    Détecte la langue d'un texte donné.
    
    Args:
        text (str): Le texte à analyser
        
    Returns:
        str: Code de la langue détectée (ex: 'en', 'fr', etc.)
    """
    try:
        return langdetect.detect(text)
    except Exception as e:
        logger.error(f"Erreur lors de la détection de la langue: {e}")
        return "unknown" 