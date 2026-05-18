"""
Module de surveillance des performances du système.
"""
import logging
import time
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

import psutil
import numpy as np
import pandas as pd

from ..validation.validator import Validator

class PerformanceMonitor:
    """Classe pour la surveillance des performances du système."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialise le moniteur de performances.
        
        Args:
            log_dir (str): Répertoire pour les logs
        """
        self.logger = logging.getLogger(__name__)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_history = []
        self.validator = Validator()
        
    def record_metrics(self, metrics: Dict):
        """
        Enregistre des métriques de performance.
        
        Args:
            metrics (Dict): Métriques à enregistrer
        """
        try:
            # Ajout du timestamp
            metrics['timestamp'] = datetime.now().isoformat()
            
            # Ajout des métriques système
            metrics.update(self._get_system_metrics())
            
            # Sauvegarde des métriques
            self.metrics_history.append(metrics)
            self._save_metrics()
            
            self.logger.info(f"Métriques enregistrées: {metrics}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement des métriques: {str(e)}")
            
    def _get_system_metrics(self) -> Dict:
        """
        Récupère les métriques système.
        
        Returns:
            Dict: Métriques système
        """
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
        
    def _save_metrics(self):
        """Sauvegarde les métriques dans un fichier."""
        try:
            metrics_file = self.log_dir / 'metrics.json'
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des métriques: {str(e)}")
            
    def generate_report(self) -> str:
        """
        Génère un rapport de performance.
        
        Returns:
            str: Rapport formaté
        """
        if not self.metrics_history:
            return "Aucune métrique enregistrée."
            
        try:
            # Conversion en DataFrame pour l'analyse
            df = pd.DataFrame(self.metrics_history)
            
            # Calcul des statistiques
            stats = {
                'latence_moyenne': df.get('latence', pd.Series()).mean(),
                'precision_moyenne': df.get('precision', pd.Series()).mean(),
                'cpu_moyen': df['cpu_percent'].mean(),
                'memoire_moyenne': df['memory_percent'].mean()
            }
            
            # Formatage du rapport
            report = ["=== Rapport de Performance ==="]
            
            # Métriques de performance
            report.append("\nMétriques de Performance:")
            report.append(f"- Latence moyenne: {stats['latence_moyenne']:.2f}s")
            report.append(f"- Précision moyenne: {stats['precision_moyenne']:.2%}")
            
            # Métriques système
            report.append("\nMétriques Système:")
            report.append(f"- Utilisation CPU moyenne: {stats['cpu_moyen']:.1f}%")
            report.append(f"- Utilisation mémoire moyenne: {stats['memoire_moyenne']:.1f}%")
            
            # Tendances
            report.append("\nTendances:")
            for metric in ['latence', 'precision']:
                if metric in df:
                    trend = np.polyfit(range(len(df[metric])), df[metric], 1)[0]
                    direction = "augmente" if trend > 0 else "diminue"
                    report.append(f"- {metric.capitalize()} {direction}")
                    
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return "Erreur lors de la génération du rapport."
            
    def alert_if_needed(self, metrics: Dict) -> Optional[str]:
        """
        Vérifie si des alertes doivent être émises.
        
        Args:
            metrics (Dict): Métriques actuelles
            
        Returns:
            Optional[str]: Message d'alerte si nécessaire
        """
        alerts = []
        
        # Seuils d'alerte
        thresholds = {
            'cpu_percent': 90,
            'memory_percent': 85,
            'latence': 2.0,
            'precision': 0.7
        }
        
        # Vérification des seuils
        for metric, threshold in thresholds.items():
            if metric in metrics:
                value = metrics[metric]
                if metric in ['cpu_percent', 'memory_percent']:
                    if value > threshold:
                        alerts.append(f"Alerte: {metric} élevé ({value:.1f}%)")
                elif metric == 'latence':
                    if value > threshold:
                        alerts.append(f"Alerte: latence élevée ({value:.2f}s)")
                elif metric == 'precision':
                    if value < threshold:
                        alerts.append(f"Alerte: précision faible ({value:.2%})")
                        
        if alerts:
            alert_message = "\n".join(alerts)
            self.logger.warning(alert_message)
            return alert_message
            
        return None 