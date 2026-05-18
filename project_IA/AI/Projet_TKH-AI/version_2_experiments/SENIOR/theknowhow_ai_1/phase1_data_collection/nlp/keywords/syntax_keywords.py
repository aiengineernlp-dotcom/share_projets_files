"""
Mots-clés et patterns syntaxiques pour l'analyse de texte.

RÔLE PRINCIPAL :
---------------
Ce module définit les mots-clés et patterns syntaxiques utilisés
pour l'analyse de texte. Il fournit des listes de termes et de
patterns prédéfinis pour l'identification de structures syntaxiques
spécifiques dans les textes médicaux.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * nlp/analysis/text_analyzer.py (analyse de texte)
  * processors/medical_analysis/*.py (analyse médicale)
  * scrapers/social_media/*.py (filtrage des posts)

- Dépend de :
  * config/settings.py (configuration)
  * nlp/keywords/__init__.py (initialisation)

STRUCTURE DU CONTENU :
--------------------
1. Patterns syntaxiques :
   - Patterns de questions
   - Patterns de symptômes
   - Patterns de diagnostic
   - Patterns de traitement

2. Mots-clés :
   - Mots-clés de contexte
   - Mots-clés de modalité
   - Mots-clés de temporalité
   - Mots-clés de localisation

3. Expressions régulières :
   - Regex pour les dates
   - Regex pour les nombres
   - Regex pour les unités
   - Regex pour les mesures

4. Constantes :
   - Seuils de confiance
   - Poids des patterns
   - Priorités des termes

FONCTIONS PRINCIPALES :
---------------------
- get_patterns() : Obtient les patterns
- get_keywords() : Obtient les mots-clés
- get_regex() : Obtient les regex
- validate_pattern() : Valide un pattern

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il définit les patterns d'analyse
- Il fournit les mots-clés essentiels
- Il est utilisé par les analyseurs
- Il assure la qualité de l'analyse
"""

from spacy.matcher import Matcher
from spacy.language import Language

def init_syntax_matcher(nlp: Language) -> Matcher:
    """
    Initialise le matcher pour les structures syntaxiques génériques
    """
    syntax_matcher = Matcher(nlp.vocab)

    # Pattern pour "Should I + [verb]" questions
    syntax_matcher.add("SHOULD_I", [[{"LOWER": "should"}, {"LOWER": "i"}, {"POS": "VERB"}]])

    # Pattern pour "Is this + [adjective]" questions
    syntax_matcher.add("IS_THIS", [[{"LOWER": "is"}, {"LOWER": "this"}, {"POS": "ADJ"}]])

    # Pattern pour "Could this be + [noun]" questions
    syntax_matcher.add("COULD_THIS_BE", [
        [{"LOWER": "could"}, {"LOWER": "this"}, {"LOWER": "be"}, {"POS": "NOUN"}]
    ])

    # Pattern pour "What does + [noun] + mean" questions
    syntax_matcher.add("WHAT_DOES_MEAN", [
        [{"LOWER": "what"}, {"LOWER": "does"}, {"POS": "NOUN"}, {"LOWER": "mean"}]
    ])

    return syntax_matcher 