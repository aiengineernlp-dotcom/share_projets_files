"""
Classe de base pour tous les scrapers.
Définit l'interface commune et les fonctionnalités partagées.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseScraper(ABC):
    """Classe abstraite de base pour tous les scrapers."""
    
    def __init__(self, source_name: str, source_type: str):
        """
        Initialise le scraper avec les configurations de base.
        
        Args:
            source_name: Nom de la source (ex: "reddit", "twitter")
            source_type: Type de source (ex: "social_media", "medical_forum")
        """
        self.source_name = source_name
        self.source_type = source_type
        
        # Configuration des chemins
        self.base_dir = Path("data")
        self.raw_data_dir = self.base_dir / "raw" / source_type / source_name
        self.processed_data_dir = self.base_dir / "processed" / source_type / source_name
        
        # Création des répertoires
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Métriques
        self.metrics = {
            "items_collected": 0,
            "items_processed": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }

    @abstractmethod
    async def connect(self) -> bool:
        """
        Établit la connexion avec la source de données.
        À implémenter dans les classes enfants.
        
        Returns:
            bool: True si la connexion est établie, False sinon
        """
        pass

    @abstractmethod
    async def fetch_data(self, *args, **kwargs) -> List[Dict]:
        """
        Récupère les données de la source.
        À implémenter dans les classes enfants.
        
        Returns:
            Liste de dictionnaires contenant les données
        """
        pass

    @abstractmethod
    async def process_data(self, data: List[Dict]) -> List[Dict]:
        """
        Traite les données récupérées.
        À implémenter dans les classes enfants.
        
        Args:
            data: Données brutes à traiter
            
        Returns:
            Données traitées
        """
        pass

    async def save_data(self, data: List[Dict], is_processed: bool = False) -> bool:
        """
        Sauvegarde les données dans un fichier JSON.
        
        Args:
            data: Données à sauvegarder
            is_processed: Si True, sauvegarde dans processed_data_dir, sinon dans raw_data_dir
            
        Returns:
            bool: True si la sauvegarde est réussie, False sinon
        """
        try:
            if not data:
                logger.warning("Aucune donnée à sauvegarder")
                return False
                
            # Génération du nom de fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_type = "processed" if is_processed else "raw"
            filename = f"{self.source_name}_{data_type}_{timestamp}.json"
            
            # Sélection du répertoire
            save_dir = self.processed_data_dir if is_processed else self.raw_data_dir
            filepath = save_dir / filename
            
            # Ajout de métadonnées
            data_with_meta = {
                "metadata": {
                    "source": self.source_name,
                    "type": self.source_type,
                    "timestamp": datetime.now().isoformat(),
                    "data_type": data_type,
                    "items_count": len(data)
                },
                "data": data
            }
            
            # Sauvegarde
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_with_meta, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Données sauvegardées dans {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données: {e}")
            return False

    def start_metrics(self) -> None:
        """Démarre le suivi des métriques."""
        self.metrics["start_time"] = datetime.now()
        self.metrics["items_collected"] = 0
        self.metrics["items_processed"] = 0
        self.metrics["errors"] = 0

    def end_metrics(self) -> Dict[str, Any]:
        """
        Termine le suivi des métriques et retourne les résultats.
        
        Returns:
            Dict contenant les métriques
        """
        self.metrics["end_time"] = datetime.now()
        duration = (self.metrics["end_time"] - self.metrics["start_time"]).total_seconds()
        
        return {
            **self.metrics,
            "duration_seconds": duration,
            "items_per_second": self.metrics["items_collected"] / duration if duration > 0 else 0
        }

    def increment_metric(self, metric_name: str, value: int = 1) -> None:
        """
        Incrémente une métrique.
        
        Args:
            metric_name: Nom de la métrique
            value: Valeur à ajouter
        """
        if metric_name in self.metrics:
            self.metrics[metric_name] += value

    @abstractmethod
    async def run(self, *args, **kwargs) -> None:
        """
        Exécute le processus complet de scraping.
        À implémenter dans les classes enfants.
        """
        pass 