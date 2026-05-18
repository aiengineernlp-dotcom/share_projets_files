# Guide d'utilisation et de configuration du Reddit Scraper

## 1. Vue d'ensemble

Le scraper Reddit est conçu pour être facilement adaptable à différents domaines d'intérêt. La configuration se fait principalement dans le fichier `config/reddit_config.py`.

## 2. Structure de la configuration

### 2.1 Liste des subreddits
```python
MEDICAL_SUBREDDITS = [
    'medical', 'AskDocs', 'Health',
    # ... autres subreddits ...
]
```
Cette liste définit les subreddits à scraper. Adaptez-la selon votre domaine.

### 2.2 Termes de recherche
```python
SEARCH_TERMS = {
    'category_1': {
        'fr': ['terme1', 'terme2'],
        'en': ['term1', 'term2'],
        'ar': ['مصطلح1', 'مصطلح2']
    },
    # ... autres catégories ...
}
```

## 3. Exemple de modification : Du médical vers l'immobilier

### 3.1 Configuration originale (Médical)
```python
# Subreddits médicaux
MEDICAL_SUBREDDITS = [
    'medical', 'AskDocs', 'Health'
]

# Termes médicaux
SEARCH_TERMS = {
    'urgent_help': {
        'fr': ["urgence médicale", "aide urgente"],
        'en': ["emergency", "urgent help"],
        'ar': ["حالة طارئة", "مساعدة عاجلة"]
    }
}
```

### 3.2 Configuration modifiée (Immobilier)
```python
# Subreddits immobiliers
MEDICAL_SUBREDDITS = [
    'RealEstate', 'realestateinvesting', 'FirstTimeHomeBuyer'
]

# Termes immobiliers
SEARCH_TERMS = {
    'investment_advice': {
        'fr': ["conseil investissement", "achat immobilier"],
        'en': ["investment advice", "property investment"],
        'ar': ["نصائح استثمارية", "استثمار عقاري"]
    }
}
```

## 4. Adaptation des catégories et seuils

### 4.1 Modification des seuils
```python
CATEGORIZATION_THRESHOLDS = {
    'hot_deal': 0.8,           # Était 'urgent_help'
    'good_investment': 0.7,    # Était 'urgent_second_opinion'
    'potential_deal': 0.5,     # Était 'priority_second_opinion'
    'standard_listing': 0.3    # Était 'standard_second_opinion'
}
```

### 4.2 Adaptation des poids
```python
SCORE_WEIGHTS = {
    'market_relevance': 0.2,    # Était 'medical_relevance'
    'urgency': 0.3,            # Pour les offres à durée limitée
    'investment_potential': 0.5 # Était 'second_opinion'
}
```

## 5. Processus de modification

1. **Identifier le nouveau domaine** et ses subreddits pertinents
2. **Définir les catégories** appropriées pour ce domaine
3. **Créer les mots-clés** pour chaque catégorie dans chaque langue
4. **Ajuster les seuils** selon l'importance relative des catégories
5. **Modifier les poids** pour refléter les priorités du nouveau domaine

## 6. Test et validation

Pour tester la nouvelle configuration :
```python
PYTHONPATH=$PYTHONPATH:. python phase1_data_collection/scrapers/social_media/reddit_scraper.py
```

Observez les résultats dans les logs pour vérifier que :
- Les bons subreddits sont scrapés
- Les posts pertinents sont trouvés
- La catégorisation est logique

## 7. Conseils

- Gardez les mots-clés spécifiques au domaine
- Testez différents seuils de catégorisation
- Ajustez les poids selon l'importance relative des facteurs
- Maintenez la cohérence des catégories
- Vérifiez la pertinence des résultats

## 8. Structure des résultats

Les posts collectés seront stockés dans la base de données avec :
- Le texte du post
- La langue détectée
- La catégorie attribuée
- Le score calculé
- Les métadonnées (date, auteur, subreddit, etc.) 