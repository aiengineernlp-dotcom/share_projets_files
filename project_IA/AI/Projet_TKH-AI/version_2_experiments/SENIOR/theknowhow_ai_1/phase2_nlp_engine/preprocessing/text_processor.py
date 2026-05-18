"""
Module de prétraitement du texte pour le moteur NLP.
Gère le nettoyage, la normalisation et la détection de langue.
"""

import re
import logging
from typing import Dict, List, Tuple
import langdetect
from langdetect import DetectorFactory
import unicodedata
import spacy
from pathlib import Path

class TextProcessor:
    """Classe pour le prétraitement du texte."""
    
    def __init__(self):
        """Initialise le processeur de texte."""
        self.logger = logging.getLogger(__name__)
        # Pour la cohérence des détections de langue
        DetectorFactory.seed = 0
        
        # Chargement des modèles spaCy
        try:
            self.nlp_fr = spacy.load("fr_core_news_sm")
            self.nlp_en = spacy.load("en_core_web_sm")
            self.nlp_ar = spacy.load("xx_ent_wiki_sm")  # Modèle multilingue pour l'arabe
        except OSError:
            self.logger.warning("Modèles spaCy non trouvés. Installation en cours...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "fr_core_news_sm"])
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            subprocess.run(["python", "-m", "spacy", "download", "xx_ent_wiki_sm"])
            self.nlp_fr = spacy.load("fr_core_news_sm")
            self.nlp_en = spacy.load("en_core_web_sm")
            self.nlp_ar = spacy.load("xx_ent_wiki_sm")
        
    def clean_text(self, text: str) -> str:
        """
        Nettoie le texte en supprimant les caractères spéciaux et en normalisant.
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        try:
            # Normalisation Unicode
            text = unicodedata.normalize('NFKD', text)
            
            # Suppression des caractères spéciaux
            text = re.sub(r'[^\w\s.,!?]', ' ', text)
            
            # Normalisation des espaces
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage du texte: {str(e)}")
            raise
            
    def detect_language(self, text: str) -> str:
        """
        Détecte la langue du texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Code de la langue détectée
        """
        try:
            return langdetect.detect(text)
        except Exception as e:
            self.logger.error(f"Erreur lors de la détection de la langue: {str(e)}")
            return "unknown"
            
    def tokenize(self, text: str, language: str) -> List[str]:
        """
        Tokenise le texte en utilisant spaCy.
        
        Args:
            text: Texte à tokeniser
            language: Langue du texte
            
        Returns:
            Liste des tokens
        """
        try:
            # Sélection du modèle spaCy selon la langue
            if language == "fr":
                nlp = self.nlp_fr
            elif language == "en":
                nlp = self.nlp_en
            else:
                nlp = self.nlp_ar
                
            # Tokenisation avec spaCy
            doc = nlp(text)
            return [token.text for token in doc]
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la tokenisation: {str(e)}")
            raise
            
    def process_text(self, text: str) -> Dict:
        """
        Traite le texte complet (nettoyage, détection de langue, tokenisation).
        
        Args:
            text: Texte à traiter
            
        Returns:
            Dictionnaire contenant les résultats du traitement
        """
        try:
            # Nettoyage du texte
            cleaned_text = self.clean_text(text)
            
            # Détection de la langue
            language = self.detect_language(cleaned_text)
            
            # Tokenisation
            tokens = self.tokenize(cleaned_text, language)
            
            return {
                "cleaned_text": cleaned_text,
                "language": language,
                "tokens": tokens,
                "token_count": len(tokens)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du texte: {str(e)}")
            raise 