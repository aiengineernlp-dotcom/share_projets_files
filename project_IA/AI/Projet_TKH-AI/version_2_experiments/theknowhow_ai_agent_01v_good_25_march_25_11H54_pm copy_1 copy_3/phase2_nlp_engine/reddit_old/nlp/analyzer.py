"""
Analyseur de contenu pour les posts et réponses Reddit.
"""
import logging
from typing import Dict, List, Tuple
import re
from datetime import datetime

class PostAnalyzer:
    """Analyseur de contenu pour les posts et réponses Reddit."""
    
    def __init__(self, config: dict):
        """
        Initialise l'analyseur de posts.
        
        Args:
            config: Configuration du bot
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def analyze_post(self, post: Dict) -> Dict:
        """
        Analyse un post pour déterminer sa pertinence et ses caractéristiques.
        
        Args:
            post: Post à analyser
            
        Returns:
            Dict: Résultats de l'analyse
        """
        try:
            # Concaténation du titre et du contenu
            content = f"{post['title']} {post['content']}".lower()
            
            # Analyse des caractéristiques
            analysis = {
                'has_medical_keywords': self._has_medical_keywords(content),
                'needs_second_opinion': self._needs_second_opinion(content),
                'has_questions': self._has_questions(content),
                'is_engaged': self._is_engaged(content),
                'topic': self._identify_topic(content),
                'urgency_level': self._determine_urgency(content),
                'sentiment': self._analyze_sentiment(content)
            }
            
            # Calcul du score de pertinence
            analysis['relevance_score'] = self._calculate_relevance_score(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse du post {post['id']}: {str(e)}")
            return {
                'has_medical_keywords': False,
                'needs_second_opinion': False,
                'has_questions': False,
                'is_engaged': False,
                'topic': 'unknown',
                'urgency_level': 'low',
                'sentiment': 'neutral',
                'relevance_score': 0
            }
            
    def _has_medical_keywords(self, content: str) -> bool:
        """
        Vérifie la présence de mots-clés médicaux.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            bool: True si des mots-clés médicaux sont présents
        """
        return any(
            keyword in content 
            for keyword in self.config['nlp']['medical_keywords']
        )
        
    def _needs_second_opinion(self, content: str) -> bool:
        """
        Vérifie si le post demande un second avis.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            bool: True si un second avis est demandé
        """
        return any(
            indicator in content 
            for indicator in self.config['nlp']['second_opinion_indicators']
        )
        
    def _has_questions(self, content: str) -> bool:
        """
        Vérifie la présence de questions.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            bool: True si des questions sont présentes
        """
        return (
            '?' in content or
            any(q in content for q in ['que faire', 'que penser', 'comment', 'pourquoi'])
        )
        
    def _is_engaged(self, content: str) -> bool:
        """
        Vérifie le niveau d'engagement du post.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            bool: True si le post montre un bon niveau d'engagement
        """
        word_count = len(content.split())
        return (
            word_count > 50 or
            'détail' in content or
            'explication' in content or
            'symptôme' in content or
            'histoire' in content
        )
        
    def _identify_topic(self, content: str) -> str:
        """
        Identifie le sujet principal du post.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            str: Sujet identifié
        """
        topics = {
            'vaccination': ['vaccin', 'vaccination', 'injection'],
            'symptômes': ['symptôme', 'douleur', 'fièvre', 'fatigue'],
            'diagnostic': ['diagnostic', 'maladie', 'infection'],
            'traitement': ['traitement', 'médicament', 'thérapie'],
            'prévention': ['prévention', 'précaution', 'éviter'],
            'général': ['santé', 'médical', 'médecin']
        }
        
        for topic, keywords in topics.items():
            if any(keyword in content for keyword in keywords):
                return topic
                
        return 'unknown'
        
    def _determine_urgency(self, content: str) -> str:
        """
        Détermine le niveau d'urgence du post.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            str: Niveau d'urgence ('high', 'medium', 'low')
        """
        urgent_keywords = ['urgence', 'urgent', 'immédiat', 'maintenant', 'aujourd\'hui']
        moderate_keywords = ['bientôt', 'prochain', 'semaine', 'mois']
        
        if any(keyword in content for keyword in urgent_keywords):
            return 'high'
        elif any(keyword in content for keyword in moderate_keywords):
            return 'medium'
        return 'low'
        
    def _analyze_sentiment(self, content: str) -> str:
        """
        Analyse le sentiment du post.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            str: Sentiment ('positive', 'negative', 'neutral')
        """
        positive_words = ['merci', 'aide', 'soulagement', 'mieux', 'bien']
        negative_words = ['inquiet', 'peur', 'désespéré', 'mal', 'souffrance']
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'
        
    def _calculate_relevance_score(self, analysis: Dict) -> float:
        """
        Calcule un score de pertinence pour le post.
        
        Args:
            analysis: Résultats de l'analyse
            
        Returns:
            float: Score de pertinence (0-1)
        """
        score = 0.0
        
        # Points de base
        if analysis['has_medical_keywords']:
            score += 0.3
            
        if analysis['needs_second_opinion']:
            score += 0.4
            
        if analysis['has_questions']:
            score += 0.2
            
        if analysis['is_engaged']:
            score += 0.2
            
        # Bonus pour l'urgence
        if analysis['urgency_level'] == 'high':
            score += 0.2
        elif analysis['urgency_level'] == 'medium':
            score += 0.1
            
        # Bonus pour le sentiment négatif (besoin d'aide)
        if analysis['sentiment'] == 'negative':
            score += 0.1
            
        return min(1.0, score) 