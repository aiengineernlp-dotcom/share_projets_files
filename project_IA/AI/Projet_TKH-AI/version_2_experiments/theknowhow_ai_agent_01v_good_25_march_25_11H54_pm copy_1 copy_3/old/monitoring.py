"""Module de monitoring pour l'agent conversationnel médical.

Ce module fournit des fonctionnalités de monitoring pour suivre :
- Les performances de l'API
- L'utilisation des ressources
- Les erreurs et exceptions
- Les statistiques d'utilisation
"""

import time
import psutil
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class APIMetrics:
    """Métriques d'utilisation de l'API."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None

@dataclass
class SystemMetrics:
    """Métriques système."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0
    timestamp: datetime = datetime.now()

class MonitoringManager:
    """Gestionnaire de monitoring pour l'agent conversationnel."""
    
    def __init__(self):
        """Initialise le gestionnaire de monitoring."""
        self.api_metrics = APIMetrics()
        self.system_metrics = SystemMetrics()
        self.error_counts = defaultdict(int)
        self.response_times: List[float] = []
        self.start_time = datetime.now()
        
    def record_api_request(self, success: bool, tokens: int, response_time: float):
        """Enregistre une requête API.
        
        Args:
            success (bool): Si la requête a réussi
            tokens (int): Nombre de tokens utilisés
            response_time (float): Temps de réponse en secondes
        """
        self.api_metrics.total_requests += 1
        if success:
            self.api_metrics.successful_requests += 1
        else:
            self.api_metrics.failed_requests += 1
            
        self.api_metrics.total_tokens += tokens
        self.response_times.append(response_time)
        self.api_metrics.average_response_time = sum(self.response_times) / len(self.response_times)
        self.api_metrics.last_request_time = datetime.now()
        
    def record_error(self, error_type: str):
        """Enregistre une erreur.
        
        Args:
            error_type (str): Type d'erreur rencontrée
        """
        self.error_counts[error_type] += 1
        logger.error(f"Erreur de type {error_type} enregistrée")
        
    def update_system_metrics(self):
        """Met à jour les métriques système."""
        self.system_metrics.cpu_percent = psutil.cpu_percent()
        self.system_metrics.memory_percent = psutil.virtual_memory().percent
        self.system_metrics.disk_usage_percent = psutil.disk_usage('/').percent
        self.system_metrics.timestamp = datetime.now()
        
    def get_uptime(self) -> float:
        """Calcule le temps de fonctionnement en heures.
        
        Returns:
            float: Temps de fonctionnement en heures
        """
        return (datetime.now() - self.start_time).total_seconds() / 3600
        
    def get_metrics_summary(self) -> Dict:
        """Génère un résumé des métriques.
        
        Returns:
            Dict: Résumé des métriques
        """
        self.update_system_metrics()
        
        return {
            "api_metrics": {
                "total_requests": self.api_metrics.total_requests,
                "success_rate": (self.api_metrics.successful_requests / self.api_metrics.total_requests * 100) if self.api_metrics.total_requests > 0 else 0,
                "total_tokens": self.api_metrics.total_tokens,
                "average_response_time": self.api_metrics.average_response_time,
                "last_request_time": self.api_metrics.last_request_time.isoformat() if self.api_metrics.last_request_time else None
            },
            "system_metrics": {
                "cpu_percent": self.system_metrics.cpu_percent,
                "memory_percent": self.system_metrics.memory_percent,
                "disk_usage_percent": self.system_metrics.disk_usage_percent,
                "timestamp": self.system_metrics.timestamp.isoformat()
            },
            "error_counts": dict(self.error_counts),
            "uptime_hours": self.get_uptime()
        }

# Instance globale du gestionnaire de monitoring
monitoring_manager = MonitoringManager()

def monitor_api_call(func):
    """Décorateur pour monitorer les appels API.
    
    Args:
        func: Fonction à décorer
        
    Returns:
        Fonction décorée
    """
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            monitoring_manager.record_api_request(True, 0, response_time)  # Tokens à implémenter
            return result
        except Exception as e:
            response_time = time.time() - start_time
            monitoring_manager.record_api_request(False, 0, response_time)
            monitoring_manager.record_error(type(e).__name__)
            raise
    return wrapper 