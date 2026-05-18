# ==============================================
# PLAN DE RESTRUCTURATION DU PROJET
# ==============================================
#
# RÔLE PRINCIPAL :
# --------------
# Ce fichier plan_de_restructuration.md décrit le plan de restructuration
# du projet. Il définit :
# - Les objectifs de la restructuration
# - Les changements à effectuer
# - Les étapes de mise en œuvre
# - Les impacts attendus
#
# RELATIONS AVEC LES AUTRES FICHIERS :
# ---------------------------------
# - ARCHITECTURE.md : Architecture du projet
# - README.md : Documentation principale
# - plan_execution.md : Plan d'exécution
# - docs/* : Documentation complémentaire
#
# STRUCTURE DU CONTENU :
# --------------------
# Le document est organisé en sections :
# 1. Vue d'ensemble
# 2. Objectifs
# 3. Changements proposés
# 4. Étapes de mise en œuvre
# 5. Impacts et risques
# 6. Planning
# 7. Ressources nécessaires
#
# IMPORTANCE ET SUPPRESSION :
# -------------------------
# Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
# - Il guide la restructuration
# - Il documente les changements
# - Il assure la cohérence
# - Il facilite la communication
#
# NOTE DE MAINTENANCE :
# -------------------
# - Maintenir à jour avec l'avancement
# - Documenter les décisions
# - Suivre les impacts
# - Adapter le planning si nécessaire
#
# ==============================================

# Plan de Restructuration du Projet TheKnowHow AI Agent

## 1. Structure du Projet

```
theknowhow_ai_agent/
│
├── 📦 Phases Principales
│   │
│   ├── phase1_data_collection/           # Phase active
│   │   ├── nlp/
│   │   │   ├── keywords/
│   │   │   │   ├── __init__.py                 # (406B, 16 lignes)
│   │   │   │   ├── medical_terms.py            # (3.2KB, 67 lignes)
│   │   │   │   ├── medical_keywords.py         # (4.8KB, 107 lignes)
│   │   │   │   ├── location_keywords.py        # (11KB, 315 lignes)
│   │   │   │   ├── locations.py               # (2.2KB, 77 lignes)
│   │   │   │   ├── urgency.py                # (2.5KB, 86 lignes)
│   │   │   │   ├── urgency_keywords.py       # (5.0KB, 143 lignes)
│   │   │   │   ├── syntax.py                 # (2.6KB, 69 lignes)
│   │   │   │   └── syntax_keywords.py        # (8.0KB, 293 lignes)
│   │   │   │
│   │   │   ├── analysis/
│   │   │   │   ├── __init__.py               # (711B, 23 lignes)
│   │   │   │   ├── urgency_analyzer.py       # (15KB, 420 lignes)
│   │   │   │   ├── syntax_analyzer.py        # (11KB, 306 lignes)
│   │   │   │   ├── location_analyzer.py      # (11KB, 329 lignes)
│   │   │   │   ├── medical_analyzer.py       # (13KB, 397 lignes)
│   │   │   │   └── text_analyzer.py          # (5.5KB, 168 lignes)
│   │   │   │
│   │   │   ├── utils/                        # (Vide)
│   │   │   ├── __init__.py                   # (516B, 22 lignes)
│   │   │   ├── text_processor.py             # (6.8KB, 226 lignes)
│   │   │   ├── sentiment_analyzer.py         # (9.0KB, 233 lignes)
│   │   │   ├── model_manager.py             # (6.0KB, 178 lignes)
│   │   │   ├── matchers.py                  # (7.5KB, 214 lignes)
│   │   │   └── metrics.py                   # (564B, 19 lignes)
│   │   │
│   │   ├── processors/
│   │   │   ├── scoring/
│   │   │   │   ├── __init__.py              # (265B, 12 lignes)
│   │   │   │   ├── score_calculator.py      # (13KB, 339 lignes)
│   │   │   │   ├── thresholds.py           # (7.0KB, 177 lignes)
│   │   │   │   ├── test_real_cases.py      # (2.4KB, 63 lignes)
│   │   │   │   └── test_scoring.py         # (4.4KB, 107 lignes)
│   │   │   │
│   │   │   ├── __init__.py                  # (623B, 23 lignes)
│   │   │   ├── base_processor.py            # (2.4KB, 86 lignes)
│   │   │   ├── text_processor.py            # (5.1KB, 152 lignes)
│   │   │   ├── entity_processor.py          # (3.7KB, 115 lignes)
│   │   │   ├── location_processor.py        # (11KB, 247 lignes)
│   │   │   ├── sentiment_processor.py       # (5.7KB, 181 lignes)
│   │   │   ├── post_analyzer.py            # (7.9KB, 250 lignes)
│   │   │   └── conversation_manager.py     # (3.7KB, 103 lignes)
│   │   │
│   │   ├── scrapers/
│   │   │   ├── base/
│   │   │   │   ├── __init__.py              # (388B, 14 lignes)
│   │   │   │   ├── social_media_base.py     # (5.0KB, 148 lignes)
│   │   │   │   ├── forum_base.py           # (6.2KB, 183 lignes)
│   │   │   │   └── website_base.py         # (6.7KB, 198 lignes)
│   │   │   │
│   │   │   ├── social_media/
│   │   │   │   ├── __init__.py              # (132B, 9 lignes)
│   │   │   │   ├── reddit_scraper.py       # (5.5KB, 142 lignes)
│   │   │   │   └── twitter_scraper.py      # (4.5KB, 121 lignes)
│   │   │   │
│   │   │   ├── forums/
│   │   │   │   ├── __init__.py              # (323B, 12 lignes)
│   │   │   │   ├── sante_naturelle_scraper.py # (5.0KB, 137 lignes)
│   │   │   │   └── doctissimo_scraper.py    # (5.0KB, 137 lignes)
│   │   │   │
│   │   │   └── websites/
│   │   │       ├── __init__.py              # (357B, 12 lignes)
│   │   │       ├── doctissimo_scraper.py    # (3.8KB, 109 lignes)
│   │   │       └── sante_naturelle_scraper.py # (3.8KB, 109 lignes)
│   │   │
│   │   ├── storage/
│   │   │   ├── __init__.py                  # (429B, 20 lignes)
│   │   │   ├── database.py                  # (18KB, 419 lignes)
│   │   │   ├── models.py                    # (3.9KB, 140 lignes)
│   │   │   ├── csv_storage.py              # (4.8KB, 146 lignes)
│   │   │   ├── json_storage.py             # (4.5KB, 134 lignes)
│   │   │   └── base_storage.py             # (3.5KB, 118 lignes)
│   │   │
│   │   ├── __init__.py                      # (922B, 44 lignes)
│   │   ├── main.py                          # (2.5KB, 87 lignes)
│   │   ├── run_scraper.py                   # (8.2KB, 214 lignes)
│   │   ├── test_scoring.py                  # (2.5KB, 63 lignes)
│   │   ├── test_location_detection.py       # (805B, 25 lignes)
│   │   └── TODO.md                          # (3.0KB, 105 lignes)
│   │
│   ├── phase2_analysis/                     # (Vide - Préparé)
│   ├── phase3_interaction/                  # (Vide - Préparé)
│   ├── phase4_persuasion/                   # (Vide - Préparé)
│   └── phase5_monetization/                 # (Vide - Préparé)
│
├── 🛠 Infrastructure Commune
│   ├── api/
│   │   ├── endpoints/                       # (Vide)
│   │   ├── models/                         # (Vide)
│   │   └── routes/                         # (Vide)
│   │
│   ├── config/
│   │   ├── __init__.py                     # (260B, 9 lignes)
│   │   ├── settings.py                     # (1.2KB, 35 lignes)
│   │   ├── database_config.py             # (2.9KB, 103 lignes)
│   │   ├── nlp_config.py                  # (1.1KB, 48 lignes)
│   │   └── logging_config.py              # (1.6KB, 54 lignes)
│   │
│   ├── database/
│   │   ├── __init__.py                     # (1008B, 41 lignes)
│   │   ├── connection.py                   # (4.6KB, 147 lignes)
│   │   ├── schemas/
│   │   │   └── phase1_schemas.py          # (2.7KB, 99 lignes)
│   │   ├── models/
│   │   │   └── phase1_models.py           # (2.4KB, 76 lignes)
│   │   └── migrations/                     # (Vide)
│   │
│   ├── utils/
│   │   ├── __init__.py                     # (2.7KB, 121 lignes)
│   │   ├── nlp.py                         # (12KB, 294 lignes)
│   │   ├── helpers.py                     # (16KB, 664 lignes)
│   │   └── logger.py                      # (9.1KB, 308 lignes)
│   │
│   ├── dashboard/                          # (Vide - Préparé)
│   ├── error_handling/                     # (Vide - Préparé)
│   ├── monitoring/                         # (Vide - Préparé)
│   └── security/                           # (Vide - Préparé)
│
├── 📊 Données et Stockage
│   ├── data/
│   │   ├── cache/
│   │   │   ├── nlp/                        # (Vide)
│   │   │   └── scrapers/                   # (Vide)
│   │   │
│   │   ├── database/
│   │   │   ├── json/                       # (Vide)
│   │   │   ├── postgresql/                 # (Vide)
│   │   │   └── sqlite/                     # (Vide)
│   │   │
│   │   ├── processed/
│   │   │   ├── analytics/                  # (Vide)
│   │   │   ├── conversations/              # (Vide)
│   │   │   └── posts/                      # (Vide)
│   │   │
│   │   └── raw/
│   │       ├── social_media/
│   │       │   └── reddit/                 # (Vide)
│   │       ├── forums/                     # (Vide)
│   │       └── websites/                   # (Vide)
│   │
│   └── logs/
│       └── phase1.log                      # (29MB)
│
├── 🧪 Tests et Documentation
│   ├── tests/
│   │   ├── unit/
│   │   │   └── test_sentiment_analyzer.py  # (3.3KB, 107 lignes)
│   │   ├── integration/                    # (Vide)
│   │   ├── e2e/                           # (Vide)
│   │   └── performance/                    # (Vide)
│   │
│   ├── docs/
│   │   ├── idee_generale_Globale.md       # (2.3KB, 25 lignes)
│   │   ├── idee_projet.md                 # (1.8KB, 18 lignes)
│   │   ├── presentation_projet.md         # (3.4KB, 59 lignes)
│   │   ├── rentabilite.md                # (2.5KB, 42 lignes)
│   │   ├── api/                          # (Vide)
│   │   ├── architecture/                 # (Vide)
│   │   └── guides/                       # (Vide)
│   │
│   └── scripts/                           # (Vide)
│
├── 📝 Fichiers de Configuration
│   ├── .env                               # (811B, 30 lignes)
│   ├── requirements.txt                   # (944B, 40 lignes)
│   ├── setup.py                          # (1.0KB, 37 lignes)
│   └── .gitignore                        # (519B, 64 lignes)
│
├── 📄 Documentation Projet
│   ├── README.md                          # (2.8KB, 116 lignes)
│   ├── plan_de_restructuration.md        # (23KB, 631 lignes)
│   ├── plan_execution.md                 # (13KB, 294 lignes)
│   └── pense_bete.md                     # (1.7KB, 44 lignes)
│
└── 🔄 Code Principal
    ├── __init__.py                        # (66B, 3 lignes)
    └── phase__traitement_du_langage_naturel.py # (38KB, 1056 lignes)

├── data/                     # Données du projet
│   ├── raw/                 # Données brutes
│   │   ├── social_media/    # Données des réseaux sociaux
│   │   │   ├── reddit/     # Données spécifiques à Reddit
│   │   │   ├── twitter/    # Données spécifiques à Twitter
│   │   │   └── facebook/   # Données spécifiques à Facebook
│   │   ├── forums/         # Données des forums
│   │   └── websites/       # Données des sites web
│   │
│   ├── processed/          # Données traitées
│   │   ├── posts/         # Posts traités
│   │   ├── conversations/ # Conversations traitées
│   │   └── analytics/     # Données d'analyse
│   │
│   ├── database/          # Bases de données
│   │   ├── postgresql/    # Données structurées dans PostgreSQL
│   │   │   ├── migrations/  # Migrations de la base
│   │   │   └── backups/     # Sauvegardes PostgreSQL
│   │   ├── sqlite/       # Données SQLite (développement)
│   │   │   └── phase1.db   # Base SQLite principale
│   │   └── json/         # Données en format JSON
│   │       ├── raw/      # Données brutes en JSON
│   │       └── processed/ # Données traitées en JSON
│   │
│   └── cache/            # Cache temporaire
│       ├── scrapers/     # Cache des scrapers
│       └── nlp/         # Cache des modèles NLP
```

## 2. Restructuration du Code Existant

### 2.1 Migration du Code de `phase__traitement_du_langage_naturel.py`

#### Dans `phase1_data_collection/scrapers/base/social_media_base.py`:
# Code source : Base pour réseaux sociaux (lignes 151-200)
- Classe abstraite SocialMediaBaseScraper
- Méthodes communes aux réseaux sociaux
- Gestion des erreurs communes aux réseaux sociaux
- Authentification et API

#### Dans `phase1_data_collection/scrapers/base/forum_base.py`:
# Code source : Base pour forums (lignes 201-250)
- Classe abstraite ForumBaseScraper
- Méthodes communes aux forums
- Gestion des erreurs communes aux forums
- Parsing HTML commun

#### Dans `phase1_data_collection/scrapers/base/website_base.py`:
# Code source : Base pour sites web (lignes 251-300)
- Classe abstraite WebsiteBaseScraper
- Méthodes communes aux sites web
- Gestion des erreurs communes aux sites web
- Gestion des robots.txt et sitemap

#### Dans `phase1_data_collection/scrapers/social_media/reddit_scraper.py`:
# Code source : Scraper Reddit (lignes 301-350)
- Configuration spécifique à Reddit
- Fonctions de scraping Reddit
- Gestion des erreurs Reddit
- Adaptation des méthodes de base

#### Dans `phase1_data_collection/scrapers/social_media/twitter_scraper.py`:
# Code source : Scraper Twitter (lignes 351-400)
- Configuration de l'API Twitter
- Fonctions de scraping spécifiques à Twitter
- Gestion des erreurs Twitter

#### Dans `phase1_data_collection/scrapers/forums/medhelp_scraper.py`:
# Code source : Scraper MedHelp (lignes 401-450)
- Configuration du scraping MedHelp
- Fonctions de scraping spécifiques à MedHelp
- Gestion des erreurs MedHelp

#### Dans `phase1_data_collection/nlp/matchers.py`:
# Code source : Initialisation des matchers (lignes 451-500)
- Initialisation des matchers
- Patterns de phrases
- Patterns syntaxiques

#### Dans `phase1_data_collection/nlp/text_processor.py`:
# Code source : Traitement du texte (lignes 501-550)
- Fonction clean_text()
- Fonction extract_medical_terms()
- Autres fonctions de traitement de texte

#### Dans `phase1_data_collection/storage/database.py`:
# Code source : Gestion de la base de données (lignes 551-600)
- Initialisation de la base de données
- Création des tables
- Opérations CRUD

#### Dans `phase1_data_collection/processors/post_analyzer.py`:
# Code source : Analyse des posts (lignes 601-650)
- Fonction analyze_post()
- Fonction calculate_scores()
- Analyse des posts

#### Dans `phase1_data_collection/processors/location_processor.py`:
# Code source : Traitement de la localisation (lignes 651-700)
- Fonction is_gcc_country()
- Fonction extract_location()
- Fonction is_african_country()
- Fonction get_african_region()

#### Dans `api/routes/phase1_routes.py`:
# Code source : Routes FastAPI (lignes 701-750)
- Routes API
- Modèles Pydantic
- Endpoints

#### Dans `api/models/schemas.py`:
# Code source : Schémas Pydantic (lignes 751-800)
- Modèles Pydantic communs
  - BaseModel pour les réponses API
  - Validation des données
  - Modèles de requête et de réponse
  - Schémas de validation des données

#### Dans `api/endpoints/posts.py`:
# Code source : Endpoint /posts (lignes 801-850)
- Endpoint GET /posts
  - Filtrage par score et catégorie
  - Pagination des résultats
  - Formatage des réponses
  - Gestion des erreurs
  - Validation des paramètres

#### Dans `api/endpoints/analyze.py`:
# Code source : Endpoint /analyze (lignes 851-900)
- Endpoint POST /analyze
  - Analyse de texte médical
  - Calcul des scores
  - Recommandations
  - Validation des entrées
  - Gestion des erreurs

#### Dans `api/endpoints/scrape.py`:
# Code source : Endpoint /scrape (lignes 901-950)
- Endpoint POST /scrape
  - Configuration du scraping
  - Gestion des limites
  - Suivi du progrès
  - Validation des paramètres
  - Gestion des erreurs

#### Dans `api/endpoints/stats.py`:
# Code source : Endpoints /stats et /gcc_stats (lignes 951-1000)
- Endpoints GET /stats et /gcc_stats
  - Statistiques globales
  - Métriques par région
  - Tendances temporelles
  - Agrégation des données
  - Formatage des réponses

#### Dans `api/endpoints/conversation.py`:
# Code source : Endpoints /conversation (lignes 1001-1050)
- Endpoints POST et GET /conversation
  - Gestion des conversations
  - Historique des interactions
  - Analyse de sentiment
  - Validation des messages
  - Gestion des erreurs

#### Dans `database/models/phase1_models.py`:
# Code source : Modèles de données (lignes 1051-1100)
- Modèle Post
  - Champs: id, title, body, url, created_utc, subreddit, author
  - Scores: second_opinion, urgency, medical_relevance, sentiment, overall
  - Localisation: country, city, region, latitude, longitude
  - Relations et contraintes
  - Indexes pour optimisation

- Modèle GCCUser
  - Champs: id, post_id, country, city, region, coordinates
  - Relations avec Post
  - Validation des données
  - Indexes pour recherche

- Modèle Response
  - Champs: id, post_id, response_text, sent_time, status
  - Relations avec Post
  - Validation des données
  - Indexes pour suivi

#### Dans `database/schemas/phase1_schemas.py`:
# Code source : Schémas de validation (lignes 1101-1150)
- Schémas de validation
  - Validation des données
  - Conversions de types
  - Relations entre modèles
  - Indexes et contraintes
  - Schémas de migration

#### Dans `phase1_data_collection/processors/scoring/score_calculator.py`:
# Code source : Calcul des scores (lignes 1151-1200)
- Calcul des scores individuels
  - Score second avis
  - Score d'urgence
  - Score de pertinence médicale
  - Score de sentiment
  - Score global
- Pondération des scores
- Catégorisation
- Validation des résultats

#### Dans `phase1_data_collection/processors/scoring/thresholds.py`:
# Code source : Seuils et catégories (lignes 1201-1250)
- Seuils de catégorisation
  - Seuils pour second avis
  - Seuils pour urgence
  - Seuils pour pertinence
  - Seuils pour sentiment
- Poids des différents scores
- Règles de classification
- Paramètres configurables

#### Dans `phase1_data_collection/nlp/keywords/medical_keywords.py`:
# Code source : Mots-clés médicaux (lignes 1251-1300)
- Phrases clés pour la recherche médicale
  - Termes médicaux spécifiques
  - Vocabulaire médical
  - Patterns de phrases médicales
  - Catégories de symptômes
  - Types de conditions

#### Dans `phase1_data_collection/nlp/keywords/urgency_keywords.py`:
# Code source : Mots-clés d'urgence (lignes 1301-1350)
- Phrases exprimant l'inquiétude
  - Termes d'urgence
  - Expressions d'anxiété
  - Indicateurs de gravité
  - Niveaux d'urgence
  - Patterns temporels

#### Dans `phase1_data_collection/nlp/keywords/location_keywords.py`:
# Code source : Mots-clés géographiques (lignes 1351-1400)
- Pays du GCC
  - Villes principales
  - Régions africaines
  - Patterns de localisation
  - Coordonnées géographiques
  - Zones de service

#### Dans `phase1_data_collection/nlp/keywords/syntax_keywords.py`:
# Code source : Mots-clés de structure (lignes 1401-1450)
- Patterns "Should I"
  - Patterns "Is this"
  - Patterns "Could this be"
  - Patterns "What does"
  - Structures de questions
  - Patterns de doute

#### Dans `config/nlp_config.py`:
# Code source : Configuration NLP (lignes 1451-1500)
- Configuration de spaCy
  - Chargement du modèle "en_core_web_sm"
  - Gestion des erreurs de chargement
  - Configuration des pipelines NLP
  - Paramètres des modèles

#### Dans `config/database_config.py`:
# Code source : Configuration base de données (lignes 1501-1550)
- Configuration de la base de données
  - Paramètres de connexion
  - Chemins des fichiers DB
    - Base principale : data/database/phase1.db
    - Sauvegardes : data/database/backups/
  - Configuration des tables
  - Gestion des migrations
  - Politique de sauvegarde
  - Gestion du cache

#### Dans `phase1_data_collection/nlp/model_manager.py`:
# Code source : Gestion des modèles NLP (lignes 1551-1600)
- Gestion des modèles NLP
  - Initialisation de spaCy
  - Chargement des modèles
  - Gestion des erreurs
  - Pipeline de traitement

#### Dans `phase1_data_collection/processors/conversation_manager.py`:
# Code source : Gestion des conversations (lignes 1601-1650)
- Gestion des conversations
  - Intégration avec ConversationalAgent
  - Gestion des sessions
  - Historique des interactions
  - Analyse de sentiment
  - Gestion des erreurs

## 3. Plan d'Action

1. **Étape 1 : Création de la Structure**
   - Créer tous les dossiers nécessaires
   - Créer les fichiers __init__.py
   - Configurer les fichiers de base

2. **Étape 2 : Migration du Code**
   - Déplacer le code dans les modules appropriés
   - Mettre à jour les imports
   - Adapter les dépendances

3. **Étape 3 : Configuration**
   - Créer les fichiers de configuration
   - Configurer le logging
   - Mettre en place la sécurité

4. **Étape 4 : Tests**
   - Créer les tests unitaires
   - Créer les tests d'intégration
   - Vérifier la cohérence

5. **Étape 5 : Documentation**
   - Mettre à jour le README
   - Documenter l'API
   - Créer les guides d'utilisation

## 4. Prochaines Étapes

1. Commencer par la création de la structure de base
2. Migrer le code existant de manière modulaire
3. Mettre en place les tests
4. Documenter le projet
5. Préparer la transition vers les phases suivantes

## 5. Notes Importantes

- Maintenir la compatibilité avec le code existant
- Assurer la cohérence des imports
- Gérer les dépendances correctement
- Documenter chaque module
- Prévoir l'évolutivité

## 6. Gestion des Erreurs et Retry

### 6.1 Stratégie de Retry
- Implémentation de backoff exponentiel
- Gestion des timeouts
- Limites de retry par type d'erreur
- Journalisation des retries

### 6.2 Fallbacks
- Sources alternatives pour chaque scraper
- Cache local pour les données fréquentes
- Mode dégradé en cas d'erreur

### 6.3 Tracking des Erreurs
- Système de logging détaillé
- Catégorisation des erreurs
- Alertes sur les erreurs critiques

## 7. Monitoring et Métriques

### 7.1 Métriques des Scrapers
- Taux de succès
- Temps de réponse
- Volume de données
- Taux d'erreurs

### 7.2 Performance
- Utilisation des ressources
- Temps de traitement
- Taux de cache
- Latence

### 7.3 Système d'Alertes
- Seuils d'alerte configurables
- Canaux de notification multiples
- Escalade automatique

## 8. Sécurité

### 8.1 Gestion des Secrets
- Stockage sécurisé des tokens
- Rotation des clés
- Gestion des permissions

### 8.2 Rate Limiting
- Limites par IP
- Limites par utilisateur
- Quotas par service

### 8.3 Protection des Données
- Chiffrement des données sensibles
- Anonymisation des données
- Politique de rétention

## 9. Tests

### 9.1 Tests Unitaires
- Couverture minimale de 80%
- Tests des composants isolés
- Mocks et fixtures

### 9.2 Tests d'Intégration
- Tests des interactions entre composants
- Tests des API
- Tests de base de données

### 9.3 Tests End-to-End
- Scénarios complets
- Tests de workflows
- Tests de régression

### 9.4 Tests de Performance
- Tests de charge
- Tests de stress
- Tests de scalabilité

## 10. Documentation

### 10.1 Documentation Technique
- Architecture détaillée
- Diagrammes de flux
- API documentation

### 10.2 Guides de Développement
- Standards de code
- Workflows Git
- Processus de déploiement

### 10.3 Documentation Utilisateur
- Guides d'utilisation
- FAQ
- Troubleshooting

## 📈 Métriques de Succès

1. **Performance**
   - Réduction du temps de traitement de 30%
   - Réduction de l'utilisation mémoire de 25%
   - Amélioration des temps de réponse de 40%
   - Optimisation du chargement des modèles NLP
   - Réduction du temps de requête DB de 35%

## 🏗️ Nouvelle Architecture

### Structure des Dossiers
```
phase1_data_collection/
├── core/
│   ├── nlp/
│   │   ├── models/
│   │   ├── analyzers/
│   │   └── processors/
│   ├── storage/
│   │   ├── repositories/
│   │   ├── cache/
│   │   └── backup/
│   └── processors/
│       ├── medical/
│       ├── scoring/
│       └── validation/
├── services/
│   ├── scrapers/
│   │   ├── reddit/
│   │   └── medical_sources/
│   └── analyzers/
│       ├── sentiment/
│       └── medical/
├── infrastructure/
│   ├── cache/
│   │   ├── redis/
│   │   └── local/
│   └── database/
│       ├── postgres/
│       └── migrations/
└── interfaces/
    ├── api/
    └── cli/
``` 