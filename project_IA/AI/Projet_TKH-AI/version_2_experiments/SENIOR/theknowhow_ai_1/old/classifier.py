"""Module de classification avancée pour la phase 3."""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AdvancedClassifier:
    """Classificateur avancé utilisant le machine learning."""
    
    def __init__(self):
        """Initialise le classificateur."""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='french'
        )
        logger.info("AdvancedClassifier initialisé")
    
    def train(self, texts: List[str], labels: List[str]):
        """Entraîne le modèle sur les données fournies.
        
        Args:
            texts (List[str]): Liste des textes à classifier
            labels (List[str]): Labels correspondants
        """
        try:
            # Vectorisation des textes
            X = self.vectorizer.fit_transform(texts)
            
            # Entraînement du modèle
            self.model.fit(X, labels)
            logger.info("Modèle entraîné avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement du modèle: {e}")
            raise
    
    def predict(self, text: str) -> str:
        """Prédit la catégorie d'un texte.
        
        Args:
            text (str): Texte à classifier
            
        Returns:
            str: Catégorie prédite
        """
        try:
            # Vectorisation du texte
            X = self.vectorizer.transform([text])
            
            # Prédiction
            prediction = self.model.predict(X)[0]
            return prediction
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            return "Non-Urgent"
    
    def predict_proba(self, text: str) -> np.ndarray:
        """Calcule les probabilités de chaque catégorie.
        
        Args:
            text (str): Texte à classifier
            
        Returns:
            np.ndarray: Probabilités pour chaque catégorie
        """
        try:
            # Vectorisation du texte
            X = self.vectorizer.transform([text])
            
            # Calcul des probabilités
            probabilities = self.model.predict_proba(X)[0]
            return probabilities
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des probabilités: {e}")
            return np.array([0.5, 0.5])
    
    def preprocess_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Prétraite les features pour la classification.
        
        Args:
            features (Dict[str, Any]): Features à prétraiter
            
        Returns:
            np.ndarray: Features prétraitées
        """
        try:
            # Extraction du texte
            text = features.get("text", "")
            
            # Vectorisation du texte
            text_vector = self.vectorizer.transform([text]).toarray()
            
            # Ajout des autres features
            other_features = np.array([
                features.get("score", 0.0),
                1 if features.get("category") == "Urgent" else 0
            ])
            
            # Concaténation des features
            return np.concatenate([text_vector[0], other_features])
            
        except Exception as e:
            logger.error(f"Erreur lors du prétraitement des features: {e}")
            return np.zeros(1002)  # 1000 features de texte + 2 autres features 