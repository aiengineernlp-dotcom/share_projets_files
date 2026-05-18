"""
Interface de base pour tous les processeurs NLP.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class BaseNLPProcessor(ABC):
    """Interface abstraite pour tous les processeurs de traitement du langage naturel."""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialise le processeur NLP avec la configuration spécifique au domaine.
        
        Args:
            config: Configuration du processeur
            
        Returns:
            bool: True si l'initialisation est réussie
        """
        pass
    
    @abstractmethod
    async def preprocess_text(self, text: str) -> str:
        """
        Prétraite le texte avant analyse.
        
        Args:
            text: Texte brut à prétraiter
            
        Returns:
            str: Texte prétraité
        """
        pass
    
    @abstractmethod
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrait les entités nommées du texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            List[Dict]: Liste des entités extraites avec leurs métadonnées
        """
        pass
    
    @abstractmethod
    async def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyse le sentiment du texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict: Scores de sentiment (positif, négatif, neutre)
        """
        pass
    
    @abstractmethod
    async def classify_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Classifie le texte selon les catégories du domaine.
        
        Args:
            text: Texte à classifier
            
        Returns:
            List[Dict]: Liste des classifications avec leurs scores
        """
        pass
    
    @abstractmethod
    async def extract_keywords(self, text: str, top_n: Optional[int] = 10) -> List[Dict[str, Any]]:
        """
        Extrait les mots-clés importants du texte.
        
        Args:
            text: Texte à analyser
            top_n: Nombre de mots-clés à extraire
            
        Returns:
            List[Dict]: Liste des mots-clés avec leurs scores
        """
        pass
    
    @abstractmethod
    async def get_domain_specific_insights(self, text: str) -> Dict[str, Any]:
        """
        Extrait des insights spécifiques au domaine.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict: Insights spécifiques au domaine
        """
        pass
    
    @abstractmethod
    async def validate_domain_relevance(self, text: str) -> Dict[str, float]:
        """
        Évalue la pertinence du texte pour le domaine.
        
        Args:
            text: Texte à évaluer
            
        Returns:
            Dict: Scores de pertinence pour différents aspects du domaine
        """
        pass 