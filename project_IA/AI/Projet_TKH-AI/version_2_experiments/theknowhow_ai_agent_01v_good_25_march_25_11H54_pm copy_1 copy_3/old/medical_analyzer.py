"""
Module d'analyse des données médicales.
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
from textblob import TextBlob
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

class MedicalAnalyzer:
    """Classe pour l'analyse des données médicales."""
    
    def __init__(self):
        """Initialise l'analyseur médical."""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Mots-clés d'urgence avec leurs poids
        self.urgency_keywords = {
            'emergency': 1.0,
            'urgent': 1.0,
            'immediately': 0.9,
            'severe': 0.8,
            'acute': 0.8,
            'critical': 0.8,
            'life-threatening': 1.0,
            'bleeding': 0.7,
            'chest pain': 0.9,
            'difficulty breathing': 0.9,
            'unconscious': 1.0,
            'stroke': 1.0,
            'heart attack': 1.0
        }
        
    def analyze_post(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse complète d'un post médical.
        
        Args:
            processed_data: Données prétraitées du post
            
        Returns:
            Données enrichies avec l'analyse
        """
        analyzed_data = processed_data.copy()
        
        # Analyse du sentiment
        sentiment_scores = self._analyze_sentiment(
            processed_data['processed_title'],
            processed_data['processed_content']
        )
        analyzed_data['sentiment'] = sentiment_scores
        
        # Calcul du score d'urgence
        urgency_score = self._calculate_urgency_score(
            processed_data['processed_title'],
            processed_data['processed_content'],
            processed_data['medical_entities']
        )
        analyzed_data['urgency_score'] = urgency_score
        
        # Calcul du score de pertinence
        relevance_score = self._calculate_relevance_score(processed_data)
        analyzed_data['relevance_score'] = relevance_score
        
        # Extraction des symptômes principaux
        symptoms = self._extract_main_symptoms(processed_data['medical_entities'])
        analyzed_data['symptoms'] = symptoms
        
        # Catégorisation médicale
        category = self._categorize_post(processed_data)
        analyzed_data['medical_category'] = category
        
        # Ajout des métadonnées d'analyse
        analyzed_data['analysis_metadata'] = {
            'analyzed_at': datetime.utcnow().timestamp(),
            'version': '1.0',
            'scores': {
                'urgency': urgency_score,
                'relevance': relevance_score,
                'sentiment': sentiment_scores['compound']
            }
        }
        
        return analyzed_data
        
    def _analyze_sentiment(self, title: str, content: str) -> Dict[str, float]:
        """Analyse le sentiment du texte."""
        # Combine titre et contenu avec plus de poids pour le titre
        full_text = f"{title} {title} {content}"
        blob = TextBlob(full_text)
        
        # Calcul des scores de sentiment
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Score composé personnalisé
        compound = (polarity + 1) * (1 - subjectivity)
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'compound': compound
        }
        
    def _calculate_urgency_score(
        self,
        title: str,
        content: str,
        entities: Dict[str, List[Dict[str, str]]]
    ) -> float:
        """Calcule le score d'urgence."""
        score = 0.0
        text = f"{title.lower()} {content.lower()}"
        
        # Score basé sur les mots-clés d'urgence
        for keyword, weight in self.urgency_keywords.items():
            if keyword in text:
                score += weight
                
        # Bonus pour les mots-clés dans le titre
        for keyword in self.urgency_keywords:
            if keyword in title.lower():
                score += 0.5
                
        # Score basé sur les entités médicales
        for location in ['title', 'content']:
            for entity in entities[location]:
                if entity['label'] in {'SYMPTOM', 'DISEASE'}:
                    score += 0.3
                    
        # Normalisation entre 0 et 1
        return min(score / 10.0, 1.0)
        
    def _calculate_relevance_score(self, data: Dict[str, Any]) -> float:
        """Calcule le score de pertinence."""
        score = 0.0
        
        # Score basé sur l'engagement
        engagement_score = min((data['score'] + data['num_comments']) / 100.0, 1.0)
        score += engagement_score * 0.3
        
        # Score basé sur les entités médicales
        num_entities = data['preprocessing_metadata']['num_entities']
        entities_score = min(num_entities / 10.0, 1.0)
        score += entities_score * 0.3
        
        # Score basé sur la longueur et la qualité du contenu
        num_tokens = data['preprocessing_metadata']['num_tokens']
        content_score = min(num_tokens / 200.0, 1.0)
        score += content_score * 0.2
        
        # Score basé sur l'urgence
        urgency_score = self._calculate_urgency_score(
            data['processed_title'],
            data['processed_content'],
            data['medical_entities']
        )
        score += urgency_score * 0.2
        
        return score
        
    def _extract_main_symptoms(self, entities: Dict[str, List[Dict[str, str]]]) -> List[str]:
        """Extrait les principaux symptômes mentionnés."""
        symptoms = []
        
        for location in ['title', 'content']:
            for entity in entities[location]:
                if entity['label'] == 'SYMPTOM':
                    symptoms.append(entity['text'])
                    
        # Suppression des doublons tout en préservant l'ordre
        return list(dict.fromkeys(symptoms))
        
    def _categorize_post(self, data: Dict[str, Any]) -> str:
        """Catégorise le post dans une spécialité médicale."""
        # Combine le titre et le contenu
        text = f"{data['processed_title']} {data['processed_content']}"
        
        # Dictionnaire des spécialités avec leurs mots-clés
        specialties = {
            'cardiology': ['heart', 'chest pain', 'blood pressure', 'cardiac'],
            'neurology': ['headache', 'migraine', 'brain', 'neurological'],
            'dermatology': ['skin', 'rash', 'acne', 'dermatitis'],
            'gastroenterology': ['stomach', 'digestive', 'bowel', 'liver'],
            'orthopedics': ['bone', 'joint', 'muscle', 'back pain'],
            'general': []  # Catégorie par défaut
        }
        
        # Compte les occurrences de mots-clés pour chaque spécialité
        scores = {specialty: 0 for specialty in specialties}
        
        for specialty, keywords in specialties.items():
            for keyword in keywords:
                if keyword in text.lower():
                    scores[specialty] += 1
                    
        # Retourne la spécialité avec le score le plus élevé
        max_score = max(scores.values())
        if max_score == 0:
            return 'general'
            
        return max(scores.items(), key=lambda x: x[1])[0] 