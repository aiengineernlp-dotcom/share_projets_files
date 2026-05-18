"""
Module pour le suivi des métriques de performance du bot.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import json
from pathlib import Path

class PerformanceMetrics:
    """Gestionnaire des métriques de performance."""
    
    def __init__(self, metrics_file: str = "bot_metrics.json"):
        """
        Initialise le gestionnaire de métriques.
        
        Args:
            metrics_file: Chemin vers le fichier de métriques
        """
        self.logger = logging.getLogger(__name__)
        self.metrics_file = metrics_file
        self.metrics = self._load_metrics()
        
    def _load_metrics(self) -> Dict:
        """
        Charge les métriques depuis le fichier.
        
        Returns:
            Dict: Métriques chargées
        """
        try:
            if Path(self.metrics_file).exists():
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            return self._init_metrics()
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des métriques: {str(e)}")
            return self._init_metrics()
            
    def _init_metrics(self) -> Dict:
        """
        Initialise les métriques par défaut.
        
        Returns:
            Dict: Métriques initialisées
        """
        return {
            'detection_rate': {
                'total_posts': 0,
                'relevant_posts': 0,
                'rate': 0.0
            },
            'response_time': {
                'total_responses': 0,
                'total_time': 0,
                'average_time': 0.0
            },
            'engagement': {
                'total_responses': 0,
                'user_replies': 0,
                'conversation_length': 0,
                'rate': 0.0
            },
            'conversion': {
                'total_engagements': 0,
                'private_messages': 0,
                'rate': 0.0
            },
            'bot_detection': {
                'total_responses': 0,
                'reported_responses': 0,
                'rate': 0.0
            },
            'daily_stats': {
                'posts': 0,
                'responses': 0,
                'replies': 0,
                'private_messages': 0
            }
        }
        
    def save_metrics(self):
        """Sauvegarde les métriques dans le fichier."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=4)
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des métriques: {str(e)}")
            
    def update_detection_rate(self, total_posts: int, relevant_posts: int):
        """
        Met à jour le taux de détection.
        
        Args:
            total_posts: Nombre total de posts
            relevant_posts: Nombre de posts pertinents
        """
        self.metrics['detection_rate']['total_posts'] += total_posts
        self.metrics['detection_rate']['relevant_posts'] += relevant_posts
        if total_posts > 0:
            self.metrics['detection_rate']['rate'] = (
                self.metrics['detection_rate']['relevant_posts'] /
                self.metrics['detection_rate']['total_posts']
            )
        self.save_metrics()
        
    def update_response_time(self, response_time: float):
        """
        Met à jour le temps de réponse.
        
        Args:
            response_time: Temps de réponse en secondes
        """
        self.metrics['response_time']['total_responses'] += 1
        self.metrics['response_time']['total_time'] += response_time
        self.metrics['response_time']['average_time'] = (
            self.metrics['response_time']['total_time'] /
            self.metrics['response_time']['total_responses']
        )
        self.save_metrics()
        
    def update_engagement(self, user_replied: bool, conversation_length: int):
        """
        Met à jour les métriques d'engagement.
        
        Args:
            user_replied: Si l'utilisateur a répondu
            conversation_length: Longueur de la conversation
        """
        self.metrics['engagement']['total_responses'] += 1
        if user_replied:
            self.metrics['engagement']['user_replies'] += 1
        self.metrics['engagement']['conversation_length'] = (
            (self.metrics['engagement']['conversation_length'] * 
             (self.metrics['engagement']['total_responses'] - 1) +
             conversation_length) /
            self.metrics['engagement']['total_responses']
        )
        self.metrics['engagement']['rate'] = (
            self.metrics['engagement']['user_replies'] /
            self.metrics['engagement']['total_responses']
        )
        self.save_metrics()
        
    def update_conversion(self, sent_private_message: bool):
        """
        Met à jour les métriques de conversion.
        
        Args:
            sent_private_message: Si un message privé a été envoyé
        """
        self.metrics['conversion']['total_engagements'] += 1
        if sent_private_message:
            self.metrics['conversion']['private_messages'] += 1
        self.metrics['conversion']['rate'] = (
            self.metrics['conversion']['private_messages'] /
            self.metrics['conversion']['total_engagements']
        )
        self.save_metrics()
        
    def update_bot_detection(self, response_reported: bool):
        """
        Met à jour les métriques de détection de bot.
        
        Args:
            response_reported: Si la réponse a été signalée
        """
        self.metrics['bot_detection']['total_responses'] += 1
        if response_reported:
            self.metrics['bot_detection']['reported_responses'] += 1
        self.metrics['bot_detection']['rate'] = (
            self.metrics['bot_detection']['reported_responses'] /
            self.metrics['bot_detection']['total_responses']
        )
        self.save_metrics()
        
    def update_daily_stats(self, posts: int = 0, responses: int = 0, 
                          replies: int = 0, private_messages: int = 0):
        """
        Met à jour les statistiques quotidiennes.
        
        Args:
            posts: Nombre de posts détectés
            responses: Nombre de réponses envoyées
            replies: Nombre de réponses reçues
            private_messages: Nombre de messages privés envoyés
        """
        self.metrics['daily_stats']['posts'] += posts
        self.metrics['daily_stats']['responses'] += responses
        self.metrics['daily_stats']['replies'] += replies
        self.metrics['daily_stats']['private_messages'] += private_messages
        self.save_metrics()
        
    def get_metrics_summary(self) -> str:
        """
        Génère un résumé des métriques.
        
        Returns:
            str: Résumé des métriques
        """
        return f"""
Métriques de Performance :
------------------------
Taux de Détection : {self.metrics['detection_rate']['rate']:.2%}
Temps de Réponse Moyen : {self.metrics['response_time']['average_time']:.2f}s
Taux d'Engagement : {self.metrics['engagement']['rate']:.2%}
Longueur Moyenne des Conversations : {self.metrics['engagement']['conversation_length']:.2f}
Taux de Conversion MP : {self.metrics['conversion']['rate']:.2%}
Taux de Détection Bot : {self.metrics['bot_detection']['rate']:.2%}

Statistiques Quotidiennes :
-------------------------
Posts Détectés : {self.metrics['daily_stats']['posts']}
Réponses Envoyées : {self.metrics['daily_stats']['responses']}
Réponses Reçues : {self.metrics['daily_stats']['replies']}
Messages Privés : {self.metrics['daily_stats']['private_messages']}
""" 