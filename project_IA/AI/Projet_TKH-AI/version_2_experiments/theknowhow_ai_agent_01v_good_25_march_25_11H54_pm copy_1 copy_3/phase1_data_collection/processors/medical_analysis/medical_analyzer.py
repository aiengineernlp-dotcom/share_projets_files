"""
Analyseur de contenu médical pour la phase 1.

RÔLE PRINCIPAL :
---------------
Ce module implémente l'analyseur principal de contenu médical.
Il utilise des techniques de NLP pour identifier et analyser les éléments
médicaux dans les textes, calculer les scores de pertinence et catégoriser
les posts selon leur nature médicale.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * scrapers/social_media/reddit_scraper.py (analyse des posts)
  * scrapers/social_media/twitter_scraper.py (analyse des tweets)
  * processors/medical_analysis/urgency_analyzer.py (analyse d'urgence)

- Dépend de :
  * config/models.py (modèles de données)
  * nlp/language_detector.py (détection de langue)
  * config/medical_keywords.py (mots-clés médicaux)

STRUCTURE DU CONTENU :
--------------------
1. Imports et configuration :
   - spaCy pour le NLP
   - TextBlob pour l'analyse de sentiment
   - Modèles de données personnalisés

2. Classe MedicalAnalyzer :
   - Initialisation des modèles NLP
   - Chargement des mots-clés médicaux
   - Configuration des seuils

3. Méthodes d'analyse :
   - analyze_text() : Analyse principale
   - extract_medical_terms() : Extraction des termes
   - calculate_relevance() : Calcul de pertinence
   - categorize_content() : Catégorisation

4. Utilitaires :
   - preprocess_text() : Prétraitement
   - normalize_terms() : Normalisation
   - validate_results() : Validation

FONCTIONS PRINCIPALES :
---------------------
- analyze_medical_content() : Analyse complète
- extract_keywords() : Extraction des mots-clés
- calculate_scores() : Calcul des scores
- generate_report() : Génération de rapport

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il est le cœur de l'analyse médicale
- Il fournit les scores de pertinence
- Il assure la catégorisation des posts
- Il est utilisé par tous les scrapers
"""

from typing import Dict, List, Any
from spacy.language import Language
from spacy.tokens import Doc
from config.reddit_config import SEARCH_TERMS, CATEGORIZATION_THRESHOLDS, SCORE_WEIGHTS
from .urgency_analyzer import UrgencyAnalyzer

class MedicalAnalyzer:
    def __init__(self, nlp):
        self.nlp = nlp
        self.urgency_analyzer = UrgencyAnalyzer(nlp)
        
        # Termes médicaux spécifiques pour améliorer la détection
        self.medical_conditions = [
            "headache", "migraine", "tension headache", "cluster headache",
            "chronic pain", "arthritis", "diabetes", "hypertension",
            "depression", "anxiety", "asthma", "allergies",
            "back pain", "neck pain", "joint pain", "fatigue",
            "insomnia", "dizziness", "nausea", "vertigo"
        ]
        
        # Ajout des termes au pipeline NLP
        ruler = self.nlp.get_pipe("entity_ruler") if "entity_ruler" in self.nlp.pipe_names else self.nlp.add_pipe("entity_ruler")
        patterns = [{"label": "MEDICAL_CONDITION", "pattern": condition} for condition in self.medical_conditions]
        ruler.add_patterns(patterns)
        
        # Initialisation des autres composants
        self.medical_terms = set(self._prepare_medical_terms())
        self.second_opinion_terms = set(self._prepare_second_opinion_terms())

    def _prepare_medical_terms(self):
        """Prépare la liste des termes médicaux pour l'analyse"""
        return [
            *self.medical_conditions,  # Inclure les conditions médicales
            "doctor", "physician", "specialist", "clinic", "hospital",
            "symptoms", "diagnosis", "treatment", "medication", "prescription",
            "test", "scan", "x-ray", "mri", "blood test",
            "chronic", "acute", "severe", "mild", "moderate"
        ]

    def _prepare_second_opinion_terms(self):
        """Prépare la liste des termes liés aux demandes de second avis"""
        return [
            "second opinion", "another opinion", "different doctor",
            "other specialist", "conflicting", "disagree", "not convinced",
            "uncertain", "unsure", "confused", "stumped", "different diagnosis",
            "seek advice", "consult another", "get another opinion",
            "different perspective", "alternative opinion", "medical opinion",
            "expert opinion", "specialist opinion", "professional opinion"
        ]

    def _prepare_terms(self, category: str) -> List[str]:
        """Prépare la liste des termes pour une catégorie donnée"""
        terms = []
        for lang in SEARCH_TERMS[category]:
            terms.extend([term.lower() for term in SEARCH_TERMS[category][lang]])
        return terms

    def analyze_medical_text(self, text: str) -> Dict[str, Any]:
        """Analyse un texte médical et retourne les informations pertinentes"""
        text = text.lower()
        doc = self.nlp(text)
        
        # Calcul des scores basé sur la présence des termes
        medical_matches = sum(1 for term in self.medical_terms if term in text)
        second_opinion_matches = sum(1 for term in self.second_opinion_terms if term in text)
        
        # Analyse de l'urgence
        urgency_analysis = self.urgency_analyzer.analyze_urgency(text)
        
        # Fonction sigmoïde pour normaliser les scores
        def sigmoid(x): return 1 / (1 + 2.71828 ** (-x))
        
        # Facteur de longueur du texte (bonus pour les textes plus détaillés)
        text_length_factor = min(1.0, len(text.split()) / 100)  # Normalisé sur 100 mots
        
        # Bonus pour la présence de diagnostics spécifiques
        diagnostic_entities = [ent.text for ent in doc.ents if ent.label_ in ["DISEASE", "MEDICAL_CONDITION"]]
        diagnostic_bonus = min(0.2, len(diagnostic_entities) * 0.05)  # Maximum 0.2 bonus
        
        # Nouveau : Bonus pour les mentions de multiples médecins/opinions
        multiple_doctors = sum(1 for term in ["doctors", "specialists", "physicians", "opinions", "diagnoses"] if term in text)
        doctor_bonus = min(0.15, multiple_doctors * 0.05)  # Maximum 0.15 bonus
        
        # Nouveau : Bonus pour les expressions de doute/conflit
        doubt_expressions = ["disagree", "conflict", "differ", "unsure", "uncertain", "not convinced", "stumped", "confused"]
        doubt_matches = sum(1 for term in doubt_expressions if term in text)
        doubt_bonus = min(0.15, doubt_matches * 0.05)  # Maximum 0.15 bonus
        
        # Score médical de base
        medical_score = sigmoid(medical_matches * 2.0) * SCORE_WEIGHTS['medical_relevance']
        
        # Score de second avis amélioré avec nouveaux facteurs
        base_second_opinion_score = sigmoid(second_opinion_matches * 3.0)
        second_opinion_score = (base_second_opinion_score + diagnostic_bonus + doctor_bonus + doubt_bonus) * text_length_factor * SCORE_WEIGHTS['second_opinion']
        
        # Score d'urgence
        urgency_score = sigmoid(len(urgency_analysis['urgency_expressions']) * 2.0) * SCORE_WEIGHTS['urgency']
        
        # Détermination de la catégorie
        category = self._determine_category(urgency_score, second_opinion_score)
        
        # Extraction des entités médicales
        medical_entities = [
            {"text": ent.text, "label": ent.label_}
            for ent in doc.ents
            if ent.label_ in ["DISEASE", "DRUG", "BODY_PART", "MEDICAL_CONDITION"]
        ]
        
        return {
            "medical_score": medical_score,
            "urgency_score": urgency_score,
            "second_opinion_score": second_opinion_score,
            "category": category,
            "medical_entities": medical_entities,
            "urgency_analysis": urgency_analysis,
            "matches": {
                "medical": medical_matches,
                "urgency": len(urgency_analysis['urgency_expressions']),
                "second_opinion": second_opinion_matches,
                "multiple_doctors": multiple_doctors,
                "doubt_expressions": doubt_matches
            },
            "diagnostic_entities": diagnostic_entities,
            "text_length_factor": text_length_factor,
            "diagnostic_bonus": diagnostic_bonus,
            "doctor_bonus": doctor_bonus,
            "doubt_bonus": doubt_bonus
        }

    def _determine_category(self, urgency_score: float, second_opinion_score: float) -> str:
        """Détermine la catégorie du post basée sur les seuils de configuration"""
        if urgency_score >= CATEGORIZATION_THRESHOLDS['urgent_help']:
            return "Medical Emergency"
        elif second_opinion_score >= CATEGORIZATION_THRESHOLDS['urgent_second_opinion']:
            return "Urgent Second Opinion"
        elif second_opinion_score >= CATEGORIZATION_THRESHOLDS['priority_second_opinion']:
            return "Priority Second Opinion"
        elif second_opinion_score >= CATEGORIZATION_THRESHOLDS['standard_second_opinion']:
            return "Standard Second Opinion"
        else:
            return "Quick Consultation Recommended" 