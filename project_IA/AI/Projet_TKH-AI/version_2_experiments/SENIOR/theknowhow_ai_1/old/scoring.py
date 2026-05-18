"""
Module de scoring pour l'analyse des posts médicaux.
"""

import logging
import spacy
from spacy.matcher import PhraseMatcher, Matcher
from textblob import TextBlob
from typing import Dict, Any, List
import re

# Configuration du logger
logger = logging.getLogger(__name__)

# Phrases pour l'analyse
SECOND_OPINION_PHRASES = [
    "second opinion",
    "another doctor",
    "different doctor",
    "get another opinion",
    "seek another opinion",
    "need another doctor", 
    "different medical opinion", 
    "conflicting diagnosis",
    "alternative medical opinion", 
    "disagree with doctor", 
    "doctor was wrong",
    "seeking medical confirmation", 
    "validate diagnosis", 
    "unsure about diagnosis",
    "medical misdiagnosis", 
    "doctor disagreement", 
    "medical consultation",
    "specialist opinion", 
    "medical expert opinion", 
    "contradicting medical advice",
    "questioning treatment", 
    "medical error", 
    "wrong treatment",
    "medical consultation advice", 
    "trust doctor opinion"
]

CONCERN_PHRASES = [
    "worried",
    "concerned",
    "afraid",
    "scared",
    "anxious",
    "nervous",
    "urgent",
    "emergency",
    "critical",
    "serious",
    "life-threatening",
    "severe",
    "intense",
    "extreme",
    "unbearable"
]

MEDICAL_PHRASES = [
    "symptoms",
    "diagnosis",
    "treatment",
    "prescription",
    "medication",
    "doctor",
    "hospital",
    "emergency",
    "pain",
    "chronic",
    "acute",
    "condition",
    "disease",
    "disorder",
    "syndrome",
    "infection",
    "inflammation",
    "surgery",
    "procedure",
    "specialist",
    "consultation"
]

class NLPProcessor:
    def __init__(self):
        """Initialise le processeur NLP avec le modèle spaCy."""
        self.nlp = None
        self.matchers = {}
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.matchers = self._init_matchers()
            logger.info("Modèle spaCy chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle spaCy: {e}")
            logger.warning("Utilisation du mode dégradé pour l'analyse NLP")
            # Ne pas lever d'exception, continuer en mode dégradé

    def _init_matchers(self) -> Dict[str, Any]:
        """Initialise les matchers SpaCy."""
        if not self.nlp:
            return {}

        # Créer les matchers de phrases
        second_opinion_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        concern_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        medical_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # Ajouter les patterns
        second_opinion_matcher.add("SECOND_OPINION", [self.nlp(text) for text in SECOND_OPINION_PHRASES])
        concern_matcher.add("CONCERN", [self.nlp(text) for text in CONCERN_PHRASES])
        medical_matcher.add("MEDICAL", [self.nlp(text) for text in MEDICAL_PHRASES])

        # Matcher pour structures syntaxiques spécifiques
        syntax_matcher = Matcher(self.nlp.vocab)
        syntax_matcher.add("SHOULD_I", [[{"LOWER": "should"}, {"LOWER": "i"}, {"POS": "VERB"}]])
        syntax_matcher.add("IS_THIS", [[{"LOWER": "is"}, {"LOWER": "this"}, {"POS": "ADJ"}]])
        syntax_matcher.add("COULD_THIS_BE", [[{"LOWER": "could"}, {"LOWER": "this"}, {"LOWER": "be"}, {"POS": "NOUN"}]])
        syntax_matcher.add("WHAT_DOES_MEAN", [[{"LOWER": "what"}, {"LOWER": "does"}, {"POS": "NOUN"}, {"LOWER": "mean"}]])

        return {
            "second_opinion_matcher": second_opinion_matcher,
            "concern_matcher": concern_matcher,
            "medical_matcher": medical_matcher,
            "syntax_matcher": syntax_matcher
        }

    def analyze_post(self, title: str, body: str = "") -> Dict[str, Any]:
        """Analyse complète d'un post pour déterminer s'il s'agit d'une demande de second avis."""
        if not self.nlp or not self.matchers:
            # Mode dégradé : analyse basique basée sur des mots-clés
            return self._analyze_post_basic(title, body)

        # Si spaCy est disponible, utiliser l'analyse complète
        full_text = f"{title} {body}"
        doc = self.nlp(full_text.lower())

        # Initialiser les scores
        scores = {
            "second_opinion_score": 0.0,
            "urgency_score": 0.0,
            "medical_relevance_score": 0.0,
            "sentiment_score": 0.0,
            "overall_score": 0.0,
            "category": "General Medical Question"
        }
        
        # Analyse des correspondances de phrases
        second_opinion_matches = self.matchers["second_opinion_matcher"](doc)
        concern_matches = self.matchers["concern_matcher"](doc)
        medical_matches = self.matchers["medical_matcher"](doc)
        syntax_matches = self.matchers["syntax_matcher"](doc)
        
        # Calcul du score de second avis
        scores["second_opinion_score"] = min(len(second_opinion_matches) * 0.5, 1.0)
        
        # Calcul du score d'urgence
        scores["urgency_score"] = min(len(concern_matches) * 0.3, 1.0)
        
        # Calcul du score de pertinence médicale
        scores["medical_relevance_score"] = min(len(medical_matches) * 0.2, 1.0)
        
        # Bonus pour les structures syntaxiques spécifiques
        if syntax_matches:
            scores["medical_relevance_score"] += 0.2
            
        # Analyse de sentiment
        blob = TextBlob(full_text)
        sentiment = blob.sentiment.polarity
        scores["sentiment_score"] = (sentiment + 1) / 2  # Normalisation entre 0 et 1
        
        # Calcul du score global
        scores["overall_score"] = (
            scores["second_opinion_score"] * 0.5 +
            scores["urgency_score"] * 0.3 +
            scores["medical_relevance_score"] * 0.2
        )
        
        # Classification en catégories de priorité
        if scores["overall_score"] >= 0.7:
            scores["category"] = "High Priority - Second Opinion"
        elif scores["overall_score"] >= 0.4:
            scores["category"] = "Medium Priority - Second Opinion"
        elif scores["overall_score"] >= 0.2:
            scores["category"] = "Low Priority - Second Opinion"
        else:
            scores["category"] = "General Medical Question"
            
        return scores
        
    def _analyze_post_basic(self, title: str, body: str = "") -> Dict[str, Any]:
        """Analyse basique basée sur des mots-clés pour le mode dégradé."""
        full_text = f"{title.lower()} {body.lower()}"
        
        # Initialiser les scores
        scores = {
            "second_opinion_score": 0.0,
            "urgency_score": 0.0,
            "medical_relevance_score": 0.0,
            "sentiment_score": 0.5,  # Valeur neutre par défaut
            "overall_score": 0.0,
            "category": "General Medical Question"
        }
        
        # Compter les occurrences de mots-clés
        second_opinion_count = 0
        for phrase in SECOND_OPINION_PHRASES:
            if phrase in full_text:
                second_opinion_count += 1
                
        concern_count = 0
        for phrase in CONCERN_PHRASES:
            if phrase in full_text:
                concern_count += 1
                
        medical_count = 0
        for phrase in MEDICAL_PHRASES:
            if phrase in full_text:
                medical_count += 1
        
        # Calcul des scores
        scores["second_opinion_score"] = min(second_opinion_count * 0.5, 1.0)
        scores["urgency_score"] = min(concern_count * 0.3, 1.0)
        scores["medical_relevance_score"] = min(medical_count * 0.2, 1.0)
        
        # Analyse de sentiment basique
        try:
            blob = TextBlob(full_text)
            sentiment = blob.sentiment.polarity
            scores["sentiment_score"] = (sentiment + 1) / 2  # Normalisation entre 0 et 1
        except:
            # En cas d'erreur, garder la valeur par défaut
            pass
        
        # Calcul du score global
        scores["overall_score"] = (
            scores["second_opinion_score"] * 0.5 +
            scores["urgency_score"] * 0.3 +
            scores["medical_relevance_score"] * 0.2
        )
        
        # Classification en catégories de priorité
        if scores["overall_score"] >= 0.7:
            scores["category"] = "High Priority - Second Opinion"
        elif scores["overall_score"] >= 0.4:
            scores["category"] = "Medium Priority - Second Opinion"
        elif scores["overall_score"] >= 0.2:
            scores["category"] = "Low Priority - Second Opinion"
        else:
            scores["category"] = "General Medical Question"
            
        return scores

class MedicalScorer:
    """Classe pour le scoring médical des posts et articles."""
    
    def __init__(self):
        """Initialise le scoreur médical."""
        self.nlp_processor = NLPProcessor()
        self.logger = logging.getLogger(__name__)
    
    def score_reddit_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score un post Reddit.
        
        Args:
            post (Dict[str, Any]): Post Reddit à scorer.
            
        Returns:
            Dict[str, Any]: Résultat du scoring.
        """
        title = post.get('title', '')
        content = post.get('content', '')
        
        # Analyser le post
        scores = self.nlp_processor.analyze_post(title, content)
        
        # Ajouter les métadonnées du post
        result = {
            'content_id': post.get('id', ''),
            'content_type': 'reddit_post',
            'title': title,
            'content_preview': content[:100] + '...' if len(content) > 100 else content,
            'author': post.get('author', ''),
            'subreddit': post.get('subreddit', ''),
            'url': post.get('permalink', ''),
            'created_at': post.get('created_utc', ''),
            'analyzed_at': post.get('collected_at', ''),
            **scores
        }
        
        self.logger.info(f"Post Reddit scoré: {title} - {scores['category']} ({scores['overall_score']:.2f})")
        return result
    
    def score_medical_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score un article médical.
        
        Args:
            article (Dict[str, Any]): Article médical à scorer.
            
        Returns:
            Dict[str, Any]: Résultat du scoring.
        """
        title = article.get('title', '')
        content = article.get('content', '')
        
        # Analyser l'article
        scores = self.nlp_processor.analyze_post(title, content)
        
        # Ajouter les métadonnées de l'article
        result = {
            'content_id': str(article.get('id', '')),
            'content_type': 'medical_article',
            'title': title,
            'content_preview': content[:100] + '...' if len(content) > 100 else content,
            'author': article.get('author', ''),
            'source': article.get('source', ''),
            'url': article.get('url', ''),
            'created_at': article.get('date', ''),
            'analyzed_at': article.get('collected_at', ''),
            **scores
        }
        
        self.logger.info(f"Article médical scoré: {title} - {scores['category']} ({scores['overall_score']:.2f})")
        return result
