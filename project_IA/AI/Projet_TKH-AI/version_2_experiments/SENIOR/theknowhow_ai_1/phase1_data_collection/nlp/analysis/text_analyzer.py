"""
Analyseur de texte pour le traitement du langage naturel.

RÔLE PRINCIPAL :
---------------
Ce module implémente l'analyseur de texte principal pour le traitement
du langage naturel. Il fournit des fonctionnalités d'analyse de texte
avancées pour l'extraction d'informations, la classification et l'analyse
de sentiment.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * processors/medical_analysis/medical_analyzer.py (analyse médicale)
  * processors/medical_analysis/urgency_analyzer.py (analyse d'urgence)
  * scrapers/social_media/*.py (analyse des posts)

- Dépend de :
  * nlp/keywords/*.py (mots-clés et patterns)
  * config/models.py (modèles de données)

STRUCTURE DU CONTENU :
--------------------
1. Imports et configuration :
   - spaCy pour le NLP
   - TextBlob pour l'analyse de sentiment
   - NLTK pour le traitement de texte

2. Classe TextAnalyzer :
   - Initialisation des modèles NLP
   - Chargement des ressources
   - Configuration des pipelines

3. Méthodes d'analyse :
   - analyze_text() : Analyse complète
   - extract_entities() : Extraction d'entités
   - analyze_sentiment() : Analyse de sentiment
   - classify_text() : Classification

4. Utilitaires :
   - preprocess_text() : Prétraitement
   - tokenize_text() : Tokenisation
   - normalize_text() : Normalisation

FONCTIONS PRINCIPALES :
---------------------
- analyze() : Analyse principale
- extract() : Extraction d'informations
- classify() : Classification de texte
- summarize() : Résumé de texte

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il est le cœur du traitement NLP
- Il fournit les analyses de base
- Il est utilisé par tous les analyseurs
- Il assure la cohérence des analyses
"""

import spacy
from textblob import TextBlob
import nltk
from typing import Dict, List, Optional
from datetime import datetime

class TextAnalyzer:
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialise l'analyseur de texte avec le modèle spécifié.
        
        Args:
            model_name (str): Nom du modèle spaCy à charger
        """
        self.nlp = spacy.load(model_name)
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('wordnet')

    def analyze_text(self, text: str) -> Dict:
        """
        Analyse complète d'un texte.
        
        Args:
            text (str): Texte à analyser
            
        Returns:
            Dict: Résultats de l'analyse
        """
        doc = self.nlp(text)
        return {
            'entities': self._extract_entities(doc),
            'sentiment': self._analyze_sentiment(text),
            'tokens': self._tokenize_text(text),
            'processed_text': self._preprocess_text(text)
        }

    def _extract_entities(self, doc) -> List[Dict]:
        """
        Extrait les entités nommées du texte.
        
        Args:
            doc: Document spaCy
            
        Returns:
            List[Dict]: Liste des entités extraites
        """
        return [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

    def _analyze_sentiment(self, text: str) -> Dict:
        """
        Analyse le sentiment d'un texte.
        
        Args:
            text (str): Texte à analyser
            
        Returns:
            Dict: Scores de sentiment
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }

    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenise un texte.
        
        Args:
            text (str): Texte à tokeniser
            
        Returns:
            List[str]: Liste des tokens
        """
        return nltk.word_tokenize(text)

    def _preprocess_text(self, text: str) -> str:
        """
        Prétraite un texte.
        
        Args:
            text (str): Texte à prétraiter
            
        Returns:
            str: Texte prétraité
        """
        # TODO: Implémenter le prétraitement
        return text.lower().strip() 