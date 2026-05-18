"""
Analyseur d'urgence médicale pour la phase 1.

RÔLE PRINCIPAL :
---------------
Ce module implémente l'analyseur d'urgence médicale.
Il évalue le niveau d'urgence des posts médicaux en utilisant des règles
prédéfinies et des indicateurs d'urgence, permettant une catégorisation
rapide des cas nécessitant une attention immédiate.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * medical_analyzer.py (analyse complète)
  * scrapers/social_media/*.py (évaluation d'urgence)

- Dépend de :
  * config/medical_keywords.py (mots-clés d'urgence)
  * config/models.py (modèles de données)

STRUCTURE DU CONTENU :
--------------------
1. Configuration :
   - Seuils d'urgence
   - Indicateurs critiques
   - Poids des facteurs

2. Classe UrgencyAnalyzer :
   - Initialisation des règles
   - Chargement des indicateurs
   - Configuration des seuils

3. Méthodes d'analyse :
   - analyze_urgency() : Analyse principale
   - check_critical_indicators() : Vérification des indicateurs
   - calculate_urgency_score() : Calcul du score
   - determine_priority() : Détermination de la priorité

4. Utilitaires :
   - preprocess_text() : Prétraitement
   - extract_indicators() : Extraction des indicateurs
   - validate_results() : Validation

FONCTIONS PRINCIPALES :
---------------------
- analyze_medical_urgency() : Analyse d'urgence
- identify_critical_cases() : Identification des cas critiques
- calculate_priority_score() : Calcul de priorité
- generate_urgency_report() : Génération de rapport

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il gère l'analyse d'urgence médicale
- Il identifie les cas critiques
- Il assure la priorisation des posts
- Il est essentiel pour la réactivité
"""

from typing import Dict, List, Any
from spacy.language import Language
from spacy.tokens import Doc
from ..medical_keywords import init_urgency_matcher

class UrgencyAnalyzer:
    def __init__(self, nlp: Language):
        self.nlp = nlp
        self.urgency_matcher = init_urgency_matcher(nlp)

    def analyze_urgency(self, text: str) -> Dict[str, Any]:
        """
        Analyse l'urgence d'un texte médical
        """
        doc = self.nlp(text)
        
        # Analyse des termes d'urgence
        urgency_matches = self.urgency_matcher(doc)
        
        # Calcul du score d'urgence
        urgency_score = len(urgency_matches) / max(len(doc), 1)
        
        # Classification du niveau d'urgence
        urgency_level = self._classify_urgency_level(urgency_score, urgency_matches)
        
        # Extraction des expressions d'urgence
        urgency_expressions = [
            doc[start:end].text
            for match_id, start, end in urgency_matches
        ]

        return {
            "urgency_matches": urgency_matches,
            "urgency_score": urgency_score,
            "urgency_level": urgency_level,
            "urgency_expressions": urgency_expressions
        }

    def _classify_urgency_level(self, score: float, matches: List[tuple]) -> str:
        """
        Classifie le niveau d'urgence basé sur le score et les matches
        """
        if score > 0.3:
            return "HIGH"
        elif score > 0.1:
            return "MEDIUM"
        else:
            return "LOW" 