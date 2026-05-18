import logging
from typing import Dict, List
import re
from praw.models import Submission

class PostAnalyzer:
    """Analyse les posts Reddit pour détecter les opportunités de second avis médical."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_post(self, post: Submission) -> Dict:
        """
        Analyse un post pour déterminer s'il nécessite un second avis.
        
        Args:
            post: Objet Submission de PRAW
            
        Returns:
            Dict: Résultats de l'analyse
        """
        analysis = {
            'needs_second_opinion': False,
            'confidence': 0.0,
            'keywords_found': [],
            'engagement_level': 'low'
        }
        
        # Analyse du texte
        text = f"{post.title} {post.selftext}".lower()
        
        # Détection des mots-clés de second avis
        second_opinion_keywords = [
            'second opinion', 'not sure', 'confused', 'wondering',
            'question', 'check', 'skeptical', 'need advice', 'looking for advice',
            'doubt', 'unsure', 'help needed', 'need help', 'advice needed'
        ]
        
        found_keywords = [kw for kw in second_opinion_keywords if kw in text]
        
        if found_keywords:
            analysis['keywords_found'] = found_keywords
            analysis['needs_second_opinion'] = True
            analysis['confidence'] = min(1.0, len(found_keywords) * 0.3)
            
        # Analyse de l'engagement
        upvotes = post.score
        comments = post.num_comments
        
        if upvotes >= 5 and comments >= 2:
            analysis['engagement_level'] = 'high'
            analysis['confidence'] = min(1.0, analysis['confidence'] + 0.2)
            
        return analysis 