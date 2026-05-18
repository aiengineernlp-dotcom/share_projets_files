"""
Mots-clés et indicateurs pour la détection de besoin de second avis.

RÔLE PRINCIPAL :
---------------
Ce module définit les mots-clés et indicateurs utilisés pour détecter
les situations nécessitant un second avis médical. Il identifie les
cas où une confirmation ou une opinion supplémentaire serait bénéfique.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * processors/medical_analysis/medical_analyzer.py (analyse médicale)
  * processors/medical_analysis/urgency_analyzer.py (analyse d'urgence)
  * scrapers/social_media/*.py (filtrage des posts)

- Dépend de :
  * config/settings.py (configuration)
  * processors/medical_keywords/__init__.py (initialisation)

STRUCTURE DU CONTENU :
--------------------
1. Indicateurs de complexité :
   - Cas complexes
   - Diagnostics incertains
   - Traitements multiples
   - Historique médical complexe

2. Indicateurs de doute :
   - Expressions d'incertitude
   - Questions sur le diagnostic
   - Préoccupations sur le traitement
   - Doutes sur les recommandations

3. Indicateurs de conflit :
   - Opinions divergentes
   - Recommandations contradictoires
   - Désaccords médicaux
   - Confusion dans les conseils

4. Poids et scores :
   - Score de complexité
   - Score d'incertitude
   - Score de conflit
   - Score global de second avis

FONCTIONS PRINCIPALES :
---------------------
- get_complexity_indicators() : Indicateurs de complexité
- get_uncertainty_indicators() : Indicateurs de doute
- get_conflict_indicators() : Indicateurs de conflit
- calculate_second_opinion_score() : Calcul du score

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il identifie les cas complexes
- Il détecte les besoins de confirmation
- Il améliore la qualité des soins
- Il réduit les erreurs médicales
"""

from spacy.matcher import PhraseMatcher
from spacy.language import Language

def init_second_opinion_matcher(nlp: Language) -> PhraseMatcher:
    """
    Initialise le matcher pour les termes liés à la recherche d'un second avis
    """
    second_opinion_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    # Phrases clés pour la recherche d'un second avis médical
    second_opinion_phrases = [
        "second opinion", "another doctor", "other doctor", "see specialist",
        "different doctor", "consult another", "another physician",
        "get checked again", "additional medical opinion", "different diagnosis",
        "need confirmation", "verify diagnosis", "doubt diagnosis",
        "unsure about treatment", "alternative treatment"
    ]

    # Ajouter les patterns
    second_opinion_matcher.add("SECOND_OPINION", [nlp(text) for text in second_opinion_phrases])

    return second_opinion_matcher 