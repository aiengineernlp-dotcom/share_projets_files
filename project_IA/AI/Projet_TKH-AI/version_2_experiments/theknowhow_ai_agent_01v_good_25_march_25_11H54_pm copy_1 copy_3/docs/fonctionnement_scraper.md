# Documentation du Fonctionnement du Scraper Reddit

## ⚠️ Fichiers Critiques - Ne Pas Supprimer

### 1. Fichiers Principaux
- `reddit_scraper.py` : **CRITIQUE** - Ne pas supprimer
  - Raison : C'est le scraper principal qui gère la collecte des données Reddit
  - Interagit avec : Tous les autres modules
  - Dépendances : social_media_base.py, tous les modules NLP

- `social_media_base.py` : **CRITIQUE** - Ne pas supprimer
  - Raison : Classe de base pour tous les scrapers
  - Interagit avec : reddit_scraper.py, database.py
  - Dépendances : utils/nlp.py, storage/database.py

### 2. Modules NLP
- `nlp/keywords/` : **CRITIQUE** - Ne pas supprimer
  - Raison : Contient tous les mots-clés essentiels pour l'analyse
  - Fichiers critiques :
    - `medical_keywords.py` : Termes médicaux
    - `urgency_keywords.py` : Mots-clés d'urgence
    - `location_keywords.py` : Mots-clés de localisation
    - `syntax_keywords.py` : Mots-clés syntaxiques
  - Interagit avec : Tous les analyseurs

- `nlp/analysis/` : **CRITIQUE** - Ne pas supprimer
  - Raison : Contient les analyseurs essentiels
  - Fichiers critiques :
    - `medical_analyzer.py` : Analyse médicale
    - `text_analyzer.py` : Analyse de texte
    - `urgency_analyzer.py` : Analyse d'urgence
  - Interagit avec : reddit_scraper.py, keywords/

### 3. Processeurs
- `processors/` : **CRITIQUE** - Ne pas supprimer
  - Raison : Gère le traitement des données
  - Fichiers critiques :
    - `location_processor.py` : Traitement des localisations
    - `post_analyzer.py` : Analyse des posts
    - `scoring/thresholds.py` : Seuils de scoring
  - Interagit avec : reddit_scraper.py, nlp/analysis/

### 4. Stockage
- `storage/` : **CRITIQUE** - Ne pas supprimer
  - Raison : Gère le stockage des données
  - Fichiers critiques :
    - `database.py` : Gestion de la base de données
    - `data_manager.py` : Gestion des données brutes
  - Interagit avec : reddit_scraper.py, social_media_base.py

## 🔄 Flux de Données et Interactions

### 1. Collecte des Données
```
reddit_scraper.py
↓
social_media_base.py (héritage)
↓
collect_posts() → Récupère les posts Reddit
```

### 2. Traitement Initial
```
collect_posts()
↓
detect_language() (utils/nlp.py)
↓
detect_entities() (utils/nlp.py)
↓
evaluate_urgency() (nlp/keywords/urgency_keywords.py)
```

### 3. Analyse Approfondie
```
evaluate_urgency()
↓
location_processor.process() (processors/location_processor.py)
↓
medical_analyzer.analyze() (nlp/analysis/medical_analyzer.py)
↓
text_analyzer.analyze() (nlp/analysis/text_analyzer.py)
```

### 4. Stockage
```
Analyse Approfondie
↓
database_manager.save_post() (storage/database.py)
↓
data_manager.save_raw_data() (storage/data_manager.py)
```

## 🔗 Dépendances entre les Modules

### 1. Dépendances Directes
- `reddit_scraper.py` dépend de :
  - social_media_base.py
  - utils/nlp.py
  - processors/location_processor.py
  - storage/database.py
  - storage/data_manager.py

### 2. Dépendances Indirectes
- `social_media_base.py` dépend de :
  - utils/nlp.py
  - storage/database.py
  - storage/data_manager.py

### 3. Dépendances des Analyseurs
- `medical_analyzer.py` dépend de :
  - nlp/keywords/medical_keywords.py
  - nlp/model_manager.py
  - nlp/text_processor.py

## ⚠️ Points d'Attention

### 1. Ordre de Chargement
- Le modèle NLP doit être chargé avant toute analyse
- La base de données doit être initialisée avant le stockage
- Les mots-clés doivent être chargés avant l'analyse

### 2. Gestion des Erreurs
- Vérifier les connexions à la base de données
- Gérer les erreurs d'API Reddit
- Valider les données avant le stockage

### 3. Performance
- Limiter le nombre de requêtes Reddit
- Optimiser les analyses NLP
- Gérer la mémoire pour les grands volumes de données

## 🔧 Maintenance

### 1. Mises à Jour Recommandées
- Mots-clés médicaux
- Seuils de scoring
- Modèles NLP

### 2. Nettoyage
- Données brutes périodiques
- Logs
- Cache temporaire

### 3. Monitoring
- Taux de succès des requêtes
- Temps de traitement
- Utilisation mémoire 