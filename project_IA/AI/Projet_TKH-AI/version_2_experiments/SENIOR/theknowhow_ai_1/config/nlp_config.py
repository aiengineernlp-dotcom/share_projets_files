"""
Configuration du système NLP (Natural Language Processing).
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 39-45 : initialisation NLP)
"""

import spacy
from .settings import SPACY_MODEL
from .logging_config import logger

def load_nlp_model():
    """
    Charge le modèle spaCy.
    Returns:
        spacy.Language: Le modèle spaCy chargé
    """
    try:
        nlp = spacy.load(SPACY_MODEL)
        logger.info(f"Modèle NLP {SPACY_MODEL} chargé avec succès")
        return nlp
    except Exception as e:
        logger.error(f"Impossible de charger le modèle NLP {SPACY_MODEL}: {e}")
        return None

# Configuration des composants NLP
NLP_PIPELINE_CONFIG = {
    "tagger": True,
    "parser": True,
    "ner": True,
    "textcat": False,
    "sentiment": True
}

# Configuration des matchers
MATCHER_CONFIG = {
    "attr": "LOWER",
    "ignore_case": True,
    "merge_matches": True
}

# Seuils pour l'analyse
THRESHOLD_CONFIG = {
    "similarity": 0.85,
    "confidence": 0.75,
    "sentiment": 0.5
}

# Initialisation du modèle
nlp = load_nlp_model() 