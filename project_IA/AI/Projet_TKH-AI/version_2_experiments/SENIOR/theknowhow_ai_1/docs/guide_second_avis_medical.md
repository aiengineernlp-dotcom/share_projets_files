# Guide d'ajustement des paramètres pour les second avis médicaux

## 1. Paramètres principaux à modifier

### 1.1 Nombre de posts à collecter
Dans `config/reddit_config.py`, augmenter `POSTS_PER_SEARCH` :
```python
POSTS_PER_SEARCH = 100  # Augmenter de 25 à 100 pour plus de données
```

### 1.2 Seuils de catégorisation
Ajuster les seuils dans `CATEGORIZATION_THRESHOLDS` pour mieux identifier les second avis :
```python
CATEGORIZATION_THRESHOLDS = {
    'urgent_help': 0.6,      # Maintenir ce seuil
    'urgent_second_opinion': 0.45,  # Réduire de 0.7 à 0.45
    'priority_second_opinion': 0.35,  # Réduire de 0.5 à 0.35
    'standard_second_opinion': 0.25,  # Réduire de 0.3 à 0.25
    'quick_advice': 0.2      # Maintenir ce seuil
}
```

### 1.3 Poids des scores
Modifier les poids dans `SCORE_WEIGHTS` pour donner plus d'importance aux second avis :
```python
SCORE_WEIGHTS = {
    'medical_relevance': 0.4,    # Réduire de 0.5 à 0.4
    'urgency': 0.3,              # Maintenir
    'second_opinion': 0.3        # Augmenter de 0.2 à 0.3
}
```

## 2. Subreddits à ajouter

Ajouter ces subreddits spécialisés dans `MEDICAL_SUBREDDITS` :
```python
MEDICAL_SUBREDDITS = [
    # ... subreddits existants ...
    'SecondOpinion',           # Spécialisé dans les second avis
    'MedicalSecondOpinion',    # Second avis médicaux
    'DoctorAdvice',           # Conseils médicaux
    'MedicalAdvice',          # Avis médicaux
    'HealthAdvice',           # Conseils de santé
    'PatientAdvice',          # Conseils pour les patients
    'MedicalQuestions',       # Questions médicales
    'HealthQuestions',        # Questions de santé
    'PatientQuestions'        # Questions des patients
]
```

## 3. Termes de recherche à ajouter

### 3.1 Français
Ajouter ces termes dans `SEARCH_TERMS['second_opinion']['fr']` :
```python
'fr': [
    # ... termes existants ...
    "changement de médecin",
    "nouveau spécialiste",
    "avis divergent",
    "diagnostic différent",
    "traitement différent",
    "médecin ne prend pas au sérieux",
    "doute sur le traitement",
    "avis médical contradictoire",
    "besoin d'une confirmation",
    "médecin ne m'écoute pas",
    "avis médical alternatif"
]
```

### 3.2 Anglais
Ajouter ces termes dans `SEARCH_TERMS['second_opinion']['en']` :
```python
'en': [
    # ... termes existants ...
    "change doctor",
    "new specialist",
    "divergent opinion",
    "different diagnosis",
    "different treatment",
    "doctor not taking seriously",
    "doubt about treatment",
    "contradictory medical advice",
    "need verification",
    "doctor not listening",
    "alternative medical opinion"
]
```

### 3.3 Arabe
Ajouter ces termes dans `SEARCH_TERMS['second_opinion']['ar']` :
```python
'ar': [
    # ... termes existants ...
    "تغيير الطبيب",
    "أخصائي جديد",
    "رأي مختلف",
    "تشخيص مختلف",
    "علاج مختلف",
    "الطبيب لا يأخذ على محمل الجد",
    "شك في العلاج",
    "نصائح طبية متضاربة",
    "بحاجة للتأكيد",
    "الطبيب لا يستمع",
    "رأي طبي بديل"
]
```

## 4. Impact des modifications

Ces ajustements vont :
1. Augmenter le volume de données collectées (×4)
2. Faciliter la détection des demandes de second avis
3. Donner plus de poids aux indicateurs de second avis
4. Élargir la couverture des sources
5. Améliorer la détection des cas prioritaires

## 5. Recommandations d'utilisation

1. **Surveillance des résultats** :
   - Vérifier le nombre de posts collectés
   - Analyser la distribution des catégories
   - Valider la qualité des détections

2. **Ajustements fins** :
   - Modifier les seuils si trop/moins de posts sont détectés
   - Ajuster les poids selon les besoins
   - Ajouter/retirer des termes de recherche selon les résultats

3. **Maintenance** :
   - Vérifier régulièrement la validité des subreddits
   - Mettre à jour les termes de recherche
   - Surveiller les performances du scraper 