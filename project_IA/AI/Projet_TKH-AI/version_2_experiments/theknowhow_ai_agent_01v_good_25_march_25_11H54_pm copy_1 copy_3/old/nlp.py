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
    "seek another opinion"
]

CONCERN_PHRASES = [
    "worried",
    "concerned",
    "afraid",
    "scared",
    "anxious",
    "nervous"
]

MEDICAL_PHRASES = [
    "symptoms",
    "diagnosis",
    "treatment",
    "prescription",
    "medication",
    "doctor",
    "hospital",
    "emergency"
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

    def _default_analysis(self):
        """Retourne une analyse par défaut en cas d'erreur."""
        return {
            "second_opinion_score": 0.0,
            "urgency_score": 0.0,
            "medical_relevance_score": 0.0,
            "sentiment_score": 0.5,
            "overall_score": 0.0,
            "category": "General Medical Question"
        }

class EntityExtractor:
    def __init__(self):
        """Initialise l'extracteur d'entités."""
        self.nlp = spacy.load("en_core_web_sm")
        self.locations = [
            "Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain",
            "Émirats Arabes Unis", "UAE", "United Arab Emirates"
        ]
        self.dates = {
            "aujourd'hui", "demain", "hier", "semaine", "mois", "année",
            "matin", "soir", "midi", "nuit", "jour", "heure"
        }
        self.duration_pattern = re.compile(r'\d+\s+(semaine|mois|année|jour|heure|minute|seconde)s?')
        self.symptoms = MEDICAL_PHRASES

    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extrait les entités du texte."""
        entities = {
            "locations": [],
            "dates": [],
            "symptoms": []
        }
        
        # Extraire les locations
        for location in self.locations:
            if location.lower() in text.lower():
                entities["locations"].append(location)
        
        # Extraire les dates
        for date in self.dates:
            if date.lower() in text.lower():
                entities["dates"].append(date)
        
        # Extraire les symptômes
        for symptom in self.symptoms:
            if symptom.lower() in text.lower():
                entities["symptoms"].append(symptom)
        
        return entities

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrait les entités médicales du texte."""
        doc = self.nlp(text)
        entities = {
            "conditions": [],
            "medications": [],
            "symptoms": [],
            "locations": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                entities["conditions"].append(ent.text)
            elif ent.label_ == "CHEMICAL":
                entities["medications"].append(ent.text)
            elif ent.label_ == "GPE":
                entities["locations"].append(ent.text)
                
        return entities 