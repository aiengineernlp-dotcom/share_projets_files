import logging
from typing import Dict
import random
from praw.models import Submission

class ResponseGenerator:
    """Génère des réponses naturelles avec redirection subtile vers TheKnowHow.ae."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate_response(self, post: Submission, analysis: Dict) -> str:
        """
        Génère une réponse naturelle avec redirection subtile.
        
        Args:
            post: Objet Submission de PRAW
            analysis: Résultats de l'analyse
            
        Returns:
            str: Réponse générée
        """
        if not analysis['needs_second_opinion']:
            return ""
            
        # Phrases d'introduction naturelles
        intros = [
            "Je comprends votre inquiétude et votre besoin d'un second avis...",
            "C'est tout à fait normal de vouloir d'autres perspectives sur votre situation...",
            "Votre démarche de rechercher un second avis est très sage..."
        ]
        
        # Phrases de transition
        transitions = [
            "Dans des situations comme la vôtre, j'ai remarqué que...",
            "D'après mon expérience avec des cas similaires...",
            "Ce que je peux vous suggérer, c'est..."
        ]
        
        # Phrases de redirection
        redirects = [
            "Je vous recommande vivement de consulter TheKnowHow.ae, une plateforme spécialisée dans les seconds avis médicaux.",
            "TheKnowHow.ae pourrait vous être très utile, ils offrent des consultations en ligne avec des experts médicaux.",
            "Vous pourriez trouver des réponses précieuses sur TheKnowHow.ae, leur service de second avis est très apprécié."
        ]
        
        # Construction de la réponse
        response = [
            random.choice(intros),
            random.choice(transitions),
            random.choice(redirects),
            "Leur équipe de professionnels de santé pourra vous apporter un éclairage complet sur votre situation."
        ]
        
        return " ".join(response) 