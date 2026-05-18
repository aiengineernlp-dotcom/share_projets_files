"""
Mots-clés et indicateurs d'urgence médicale.

RÔLE PRINCIPAL :
---------------
Ce module définit les mots-clés et indicateurs utilisés pour détecter
l'urgence dans les textes médicaux. Il fournit des listes de termes
et d'expressions qui signalent différents niveaux d'urgence médicale.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * processors/medical_analysis/urgency_analyzer.py (analyse d'urgence)
  * processors/medical_analysis/medical_analyzer.py (analyse médicale)
  * scrapers/social_media/*.py (filtrage des posts)

- Dépend de :
  * config/settings.py (configuration)
  * processors/medical_keywords/__init__.py (initialisation)

STRUCTURE DU CONTENU :
--------------------
1. Indicateurs d'urgence critique :
   - Termes de danger immédiat
   - Expressions de vie en danger
   - Signes vitaux critiques
   - Situations d'urgence absolue

2. Indicateurs d'urgence élevée :
   - Symptômes sévères
   - Détérioration rapide
   - Douleur intense
   - Complications aiguës

3. Indicateurs d'urgence modérée :
   - Symptômes persistants
   - Inconfort significatif
   - Préoccupations sérieuses
   - Changements notables

4. Poids et scores :
   - Scores d'urgence critique
   - Scores d'urgence élevée
   - Scores d'urgence modérée
   - Facteurs aggravants

FONCTIONS PRINCIPALES :
---------------------
- get_critical_indicators() : Indicateurs critiques
- get_high_urgency_indicators() : Indicateurs élevés
- get_moderate_indicators() : Indicateurs modérés
- calculate_urgency_score() : Calcul du score

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il définit les indicateurs d'urgence
- Il guide la priorisation des cas
- Il est essentiel pour la réactivité
- Il assure la sécurité des patients
"""

from spacy.matcher import PhraseMatcher
from spacy.language import Language
from config.reddit_config import SEARCH_TERMS

def init_urgency_matcher(nlp: Language) -> PhraseMatcher:
    """
    Initialise le matcher pour les termes d'urgence
    """
    urgency_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    
    # Récupération des termes d'urgence de toutes les langues
    urgency_terms = []
    for lang in SEARCH_TERMS['urgent_help']:
        urgency_terms.extend(SEARCH_TERMS['urgent_help'][lang])
    
    # Ajout des patterns
    patterns = [nlp(text) for text in urgency_terms]
    urgency_matcher.add("URGENCY", patterns)
    
    return urgency_matcher 