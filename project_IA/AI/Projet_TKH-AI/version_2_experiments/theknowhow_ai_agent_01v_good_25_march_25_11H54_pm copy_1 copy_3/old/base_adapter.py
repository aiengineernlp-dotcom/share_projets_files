"""
Interface de base pour tous les adaptateurs de données.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class BaseAdapter(ABC):
    """Interface abstraite pour tous les adaptateurs de données."""
    
    @abstractmethod
    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """
        Établit la connexion avec la source de données.
        
        Args:
            credentials: Dictionnaire contenant les informations d'authentification
            
        Returns:
            bool: True si la connexion est établie avec succès
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Ferme la connexion avec la source de données.
        
        Returns:
            bool: True si la déconnexion est réussie
        """
        pass
    
    @abstractmethod
    async def fetch_data(self, query: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Récupère les données depuis la source.
        
        Args:
            query: Paramètres de recherche
            limit: Nombre maximum d'éléments à récupérer
            
        Returns:
            List[Dict]: Liste des données récupérées
        """
        pass
    
    @abstractmethod
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Valide les données récupérées selon les règles du domaine.
        
        Args:
            data: Données à valider
            
        Returns:
            bool: True si les données sont valides
        """
        pass
    
    @abstractmethod
    async def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforme les données dans le format standard du système.
        
        Args:
            data: Données à transformer
            
        Returns:
            Dict: Données transformées
        """
        pass
    
    @abstractmethod
    async def get_source_metadata(self) -> Dict[str, Any]:
        """
        Récupère les métadonnées de la source.
        
        Returns:
            Dict: Métadonnées de la source
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé de la connexion.
        
        Returns:
            Dict: État de santé de l'adaptateur
        """
        pass 