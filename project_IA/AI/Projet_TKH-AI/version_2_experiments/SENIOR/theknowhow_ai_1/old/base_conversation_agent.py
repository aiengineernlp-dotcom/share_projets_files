"""
Interface de base pour tous les agents conversationnels.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class BaseConversationAgent(ABC):
    """Interface abstraite pour tous les agents conversationnels."""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialise l'agent avec la configuration spécifique au domaine.
        
        Args:
            config: Configuration de l'agent
            
        Returns:
            bool: True si l'initialisation est réussie
        """
        pass
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite un message entrant et génère une réponse.
        
        Args:
            message: Message de l'utilisateur
            context: Contexte de la conversation
            
        Returns:
            Dict: Réponse générée avec métadonnées
        """
        pass
    
    @abstractmethod
    async def generate_response(self, intent: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Génère une réponse basée sur l'intention détectée.
        
        Args:
            intent: Intention détectée
            context: Contexte de la conversation
            
        Returns:
            str: Réponse générée
        """
        pass
    
    @abstractmethod
    async def update_context(self, current_context: Dict[str, Any], new_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour le contexte de la conversation.
        
        Args:
            current_context: Contexte actuel
            new_info: Nouvelles informations
            
        Returns:
            Dict: Contexte mis à jour
        """
        pass
    
    @abstractmethod
    async def handle_domain_specific_intent(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gère les intentions spécifiques au domaine.
        
        Args:
            intent: Type d'intention
            params: Paramètres de l'intention
            
        Returns:
            Dict: Résultat du traitement
        """
        pass
    
    @abstractmethod
    async def validate_response(self, response: str, context: Dict[str, Any]) -> bool:
        """
        Valide la réponse avant envoi.
        
        Args:
            response: Réponse à valider
            context: Contexte de la conversation
            
        Returns:
            bool: True si la réponse est valide
        """
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gère les erreurs pendant la conversation.
        
        Args:
            error: Erreur survenue
            context: Contexte de la conversation
            
        Returns:
            Dict: Réponse d'erreur appropriée
        """
        pass
    
    @abstractmethod
    async def log_interaction(self, interaction: Dict[str, Any]) -> bool:
        """
        Enregistre une interaction pour analyse.
        
        Args:
            interaction: Détails de l'interaction
            
        Returns:
            bool: True si l'enregistrement est réussi
        """
        pass 