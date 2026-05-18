"""
Termes et concepts médicaux pour l'analyse de contenu.

RÔLE PRINCIPAL :
---------------
Ce module définit les termes et concepts médicaux utilisés pour
l'analyse de contenu médical. Il fournit une base de connaissances
structurée pour l'identification et la classification des éléments
médicaux dans les textes.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * processors/medical_analysis/medical_analyzer.py (analyse médicale)
  * processors/medical_analysis/urgency_analyzer.py (analyse d'urgence)
  * nlp/analysis/text_analyzer.py (analyse de texte)

- Dépend de :
  * config/settings.py (configuration)
  * processors/medical_keywords/__init__.py (initialisation)

STRUCTURE DU CONTENU :
--------------------
1. Termes médicaux de base :
   - Anatomie et physiologie
   - Pathologies et maladies
   - Symptômes et signes
   - Traitements et procédures

2. Concepts médicaux :
   - Diagnostics
   - Pronostics
   - Facteurs de risque
   - Complications

3. Terminologie spécialisée :
   - Termes techniques
   - Abréviations médicales
   - Noms de médicaments
   - Codes de classification

4. Relations sémantiques :
   - Synonymes médicaux
   - Termes associés
   - Hiérarchies conceptuelles
   - Mappings terminologiques

FONCTIONS PRINCIPALES :
---------------------
- get_medical_terms() : Termes médicaux
- get_medical_concepts() : Concepts médicaux
- get_specialized_terms() : Termes spécialisés
- get_semantic_relations() : Relations sémantiques

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il définit le vocabulaire médical
- Il structure les connaissances
- Il guide l'analyse de contenu
- Il assure la précision médicale
"""

from spacy.matcher import PhraseMatcher
from spacy.language import Language

def init_medical_matcher(nlp: Language) -> PhraseMatcher:
    """
    Initialise le matcher pour les termes médicaux généraux
    """
    medical_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    # Phrases médicales générales
    medical_phrases = [
        "symptoms", "diagnosis", "treatment", "medication", "doctor",
        "hospital", "clinic", "surgery", "medical", "health", "disease",
        "condition", "illness", "specialist", "prescription", "therapy",
        "pain", "chronic", "acute", "diagnosis"
    ]

    # Ajouter les patterns
    medical_matcher.add("MEDICAL", [nlp(text) for text in medical_phrases])

    return medical_matcher 