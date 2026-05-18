# Analyse du Langage Naturel Médical

Ce document explique comment notre système analyse et classifie les textes médicaux en langage naturel.

## 1. Détection de la Langue

Le système commence par détecter la langue du texte en utilisant TextBlob :

```python
def detect_language(self, text: str) -> str:
    try:
        blob = TextBlob(text)
        detected_lang = blob.detect_language()
        return detected_lang if detected_lang in self.nlp_models else NLP_CONFIG['default']
    except:
        return NLP_CONFIG['default']
```

Cette fonction permet de :
- Détecter automatiquement la langue du texte
- Sélectionner le modèle NLP approprié pour l'analyse

## 2. Analyse du Texte Médical

L'analyse se fait dans la classe `MedicalAnalyzer` en plusieurs étapes :

```python
def analyze_medical_text(self, text: str) -> Dict[str, Any]:
    text = text.lower()
    doc = self.nlp(text)
    
    # Calcul des correspondances avec les termes médicaux
    medical_matches = sum(1 for term in self.medical_terms if term in text)
    second_opinion_matches = sum(1 for term in self.second_opinion_terms if term in text)
    
    # Analyse de l'urgence
    urgency_analysis = self.urgency_analyzer.analyze_urgency(text)
```

## 3. Calcul des Scores

Les scores sont calculés en utilisant une fonction sigmoïde pour normaliser les résultats :

```python
def sigmoid(x): return 1 / (1 + 2.71828 ** (-x))

# Les scores sont calculés avec une fonction sigmoïde pour normaliser
medical_score = sigmoid(medical_matches * 2.0) * SCORE_WEIGHTS['medical_relevance']
second_opinion_score = sigmoid(second_opinion_matches * 2.0) * SCORE_WEIGHTS['second_opinion']
urgency_score = sigmoid(len(urgency_analysis['urgency_expressions']) * 2.0) * SCORE_WEIGHTS['urgency']
```

### Exemples d'Analyse

1. **"UPDATE to: My dad probably has cancer..."**
   - Score de second opinion élevé (0.44)
   - Détection des mots clés : "cancer", "update"
   - La présence de "probably" suggère un besoin de confirmation
   - La demande de mise à jour indique un suivi médical

2. **"Mystery illness with white matter lesions..."**
   - Score d'urgence élevé (0.26)
   - "Mystery illness" indique une situation non diagnostiquée
   - "white matter lesions" est reconnu comme condition médicale sérieuse
   - Combinaison de termes suggérant une urgence médicale

3. **"Complex and my GP is stumped"**
   - Score de pertinence médicale élevé (0.19)
   - "Complex" indique une situation médicale compliquée
   - "GP is stumped" suggère une situation médicale difficile
   - Les termes indiquent un besoin d'expertise médicale approfondie

## 4. Classification Finale

La classification est basée sur des seuils prédéfinis :

```python
def _determine_category(self, urgency_score: float, second_opinion_score: float) -> str:
    if urgency_score >= CATEGORIZATION_THRESHOLDS['urgent_help']:
        return "Medical Emergency"
    elif second_opinion_score >= CATEGORIZATION_THRESHOLDS['urgent_second_opinion']:
        return "Urgent Second Opinion"
    elif second_opinion_score >= CATEGORIZATION_THRESHOLDS['standard_second_opinion']:
        return "Standard Second Opinion"
    else:
        return "Quick Consultation Recommended"
```

## Résumé de l'Approche

Notre système combine plusieurs techniques :
1. Analyse linguistique (détection de langue, analyse syntaxique)
2. Reconnaissance de termes médicaux spécifiques
3. Pondération des scores selon l'importance des termes
4. Normalisation des scores avec une fonction sigmoïde
5. Classification basée sur des seuils prédéfinis

Cette approche permet une analyse nuancée des textes médicaux en tenant compte :
- Du contexte médical
- De l'urgence de la situation
- Du besoin de second avis
- De la complexité du cas 