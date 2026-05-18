# ==============================================
# DOCUMENTATION PRINCIPALE
# ==============================================
#
# RÔLE PRINCIPAL :
# --------------
# Ce fichier README.md est le point d'entrée principal de la documentation du projet.
# Il fournit :
# - Une vue d'ensemble du projet
# - Les instructions d'installation
# - La structure du projet
# - Les composants principaux
#
# RELATIONS AVEC LES AUTRES FICHIERS :
# ---------------------------------
# - ARCHITECTURE.md : Documentation technique détaillée
# - docs/* : Documentation complémentaire
# - config/* : Fichiers de configuration
# - src/* : Code source
#
# STRUCTURE DU CONTENU :
# --------------------
# Le document est organisé en sections :
# 1. Titre et Description
# 2. Structure du Projet
#    - Arborescence des dossiers
#    - Description des composants
# 3. Composants Principaux
#    - NLP
#    - Processors
#    - Scrapers
#    - Storage
#    - Configuration
#    - Tests
# 4. Installation
#    - Prérequis
#    - Étapes d'installation
#    - Configuration
#
# IMPORTANCE ET SUPPRESSION :
# -------------------------
# Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
# - Il est le premier point de contact avec le projet
# - Il guide les nouveaux développeurs
# - Il est affiché sur GitHub/GitLab
# - Il contient les informations essentielles
#
# NOTE DE MAINTENANCE :
# -------------------
# - Maintenir à jour avec les changements du projet
# - Vérifier la cohérence avec le code
# - Ajouter les nouvelles fonctionnalités
# - Mettre à jour les instructions d'installation
#
# ==============================================

# Phase 1 - Collecte de Données

Ce projet fait partie d'un système plus large de traitement et d'analyse de données médicales. La phase 1 se concentre sur la collecte et le traitement initial des données.

## 📁 Structure du Projet

```
phase1_data_collection/
├── nlp/                          # Traitement du langage naturel
│   ├── keywords/                 # Mots-clés et patterns
│   │   ├── __init__.py
│   │   ├── medical_terms.py      # Termes médicaux
│   │   ├── medical_keywords.py   # Mots-clés médicaux
│   │   ├── location_keywords.py  # Mots-clés géographiques
│   │   ├── locations.py         # Gestion des localisations
│   │   ├── urgency.py          # Définitions d'urgence
│   │   ├── urgency_keywords.py # Mots-clés d'urgence
│   │   ├── syntax.py           # Patterns syntaxiques
│   │   └── syntax_keywords.py  # Mots-clés syntaxiques
│   │
│   ├── analysis/                # Analyseurs spécialisés
│   │   ├── __init__.py
│   │   ├── urgency_analyzer.py  # Analyse d'urgence
│   │   ├── syntax_analyzer.py   # Analyse syntaxique
│   │   ├── location_analyzer.py # Analyse de localisation
│   │   ├── medical_analyzer.py  # Analyse médicale
│   │   └── text_analyzer.py     # Analyse textuelle
│   │
│   ├── __init__.py
│   ├── text_processor.py        # Processeur de texte principal
│   ├── sentiment_analyzer.py    # Analyse de sentiment
│   ├── model_manager.py        # Gestion des modèles NLP
│   ├── matchers.py            # Patterns de matching
│   └── metrics.py             # Métriques NLP
│
├── processors/                  # Processeurs de données
│   ├── scoring/                # Système de scoring
│   │   ├── __init__.py
│   │   ├── score_calculator.py # Calcul des scores
│   │   ├── thresholds.py      # Seuils et règles
│   │   ├── test_real_cases.py # Tests cas réels
│   │   └── test_scoring.py    # Tests scoring
│   │
│   ├── __init__.py
│   ├── base_processor.py       # Processeur de base
│   ├── text_processor.py       # Traitement texte
│   ├── entity_processor.py     # Traitement entités
│   ├── location_processor.py   # Traitement localisation
│   ├── sentiment_processor.py  # Traitement sentiment
│   ├── post_analyzer.py       # Analyse des posts
│   └── conversation_manager.py # Gestion conversations
│
├── scrapers/                   # Collecteurs de données
│   ├── base/                  # Classes de base
│   │   ├── __init__.py
│   │   ├── social_media_base.py # Base réseaux sociaux
│   │   ├── forum_base.py      # Base forums
│   │   └── website_base.py    # Base sites web
│   │
│   ├── social_media/          # Scrapers réseaux sociaux
│   │   ├── __init__.py
│   │   ├── reddit_scraper.py  # Scraper Reddit
│   │   └── twitter_scraper.py # Scraper Twitter
│   │
│   ├── forums/                # Scrapers forums
│   │   ├── __init__.py
│   │   └── medhelp_scraper.py # Scraper MedHelp
│   │
│   └── websites/              # Scrapers sites web
│       ├── __init__.py
│       └── medical_sites_scraper.py
│
├── storage/                    # Gestion du stockage
│   ├── __init__.py
│   ├── database.py            # Gestion base de données
│   ├── models.py              # Modèles de données
│   ├── csv_storage.py         # Stockage CSV
│   ├── json_storage.py        # Stockage JSON
│   └── base_storage.py        # Classe stockage base
│
├── config/                     # Configuration
│   ├── __init__.py
│   ├── settings.py            # Paramètres généraux
│   ├── database_config.py     # Config base de données
│   ├── nlp_config.py         # Config NLP
│   └── logging_config.py     # Config logging
│
├── tests/                     # Tests
│   ├── unit/                 # Tests unitaires
│   ├── integration/          # Tests d'intégration
│   ├── e2e/                 # Tests end-to-end
│   └── performance/         # Tests de performance
│
├── data/                     # Données
│   ├── raw/                 # Données brutes
│   ├── processed/           # Données traitées
│   ├── cache/              # Cache
│   └── logs/               # Logs
│
├── __init__.py
├── main.py                  # Point d'entrée principal
├── run_scraper.py          # Script de scraping
└── requirements.txt        # Dépendances
```

## 📦 Composants Principaux

### 🧠 NLP (Natural Language Processing)
- Analyse de texte médical
- Détection de localisation
- Analyse de sentiment
- Gestion des modèles linguistiques

### 🔄 Processors
- Calcul de scores
- Traitement des entités
- Gestion des conversations
- Analyse des posts

### 🌐 Scrapers
- Collecte depuis Reddit
- Collecte depuis forums médicaux
- Collecte depuis sites spécialisés

### 💾 Storage
- Gestion base de données
- Stockage fichiers
- Cache système

### ⚙️ Configuration
- Paramètres système
- Configuration base de données
- Configuration NLP
- Logging

### 🧪 Tests
- Tests unitaires
- Tests d'intégration
- Tests de performance
- Tests end-to-end

## Installation

1. Cloner le repository :
```