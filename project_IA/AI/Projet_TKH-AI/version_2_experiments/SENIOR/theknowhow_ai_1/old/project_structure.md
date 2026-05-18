# Structure du Projet IA_Agents

## Vue d'ensemble
Ce projet implémente un système d'agents IA pour l'analyse médicale et l'interaction avec les utilisateurs.

## Structure des Dossiers

```
IA_Agents/
├── src/                                # Code source principal (2.9KB)
│   ├── core/                          # Cœur de l'application
│   │   ├── conversation/              # Gestion des conversations
│   │   ├── data_collection/           # Collecte de données
│   │   ├── nlp/                       # Traitement du langage naturel
│   │   ├── scraper_utils.py          # Utilitaires de scraping (4.4KB)
│   │   ├── base_adapter.py           # Adaptateur de base (2.4KB)
│   │   └── __init__.py               # Initialisation du module (0B)
│   ├── interfaces/                    # Interfaces utilisateur et API
│   ├── infrastructure/                # Infrastructure technique
│   ├── services/                      # Services métier
│   ├── utils/                         # Utilitaires communs
│   ├── __init__.py                   # Initialisation du package (0B)
│   └── main.py                        # Point d'entrée principal (2.9KB)
│
├── config/                            # Configuration globale du projet
│   ├── development/                   # Configuration de développement
│   ├── production/                    # Configuration de production
│   └── testing/                       # Configuration de tests
│
├── data/                              # Données du projet
│   ├── databases/                     # Bases de données
│   │   ├── reddit_deals.db           # Base de données des offres (156KB)
│   │   └── reddit_posts.db           # Base de données des posts (156KB)
│   ├── logs/                         # Journaux d'activité
│   ├── processed/                    # Données traitées
│   ├── raw_json/                     # Données brutes
│   │   ├── medical/                  # Données médicales
│   │   └── reddit/                   # Données Reddit
│   └── .gitignore                    # Configuration Git pour data (194B)
│
├── docs/                             # Documentation
│   ├── api/                         # Documentation API
│   ├── architecture/                # Documentation technique
│   ├── guides/                      # Guides d'utilisation
│   ├── monetisation/               # Plans de monétisation
│   ├── planning/                   # Documents de planification
│   │   └── PLAN_du_projet.txt     # Plan détaillé du projet (5.9KB)
│   ├── improvements/               # Documents d'amélioration
│   │   ├── AMELIORATION.txt       # Pistes d'amélioration (4.3KB)
│   │   ├── ADAPTATION_SECTEURS.txt # Guide d'adaptation (7.3KB)
│   │   └── DOMAINES_APPLICATION.txt # Domaines d'application (14KB)
│   ├── CHANGELOG.md                # Journal des modifications (1.3KB)
│   ├── README.md                   # Documentation principale (954B)
│   └── project_structure.md        # Structure du projet (4.7KB)
│
├── tests/                           # Tests du projet
│   ├── unit/                       # Tests unitaires
│   ├── integration/                # Tests d'intégration
│   ├── e2e/                        # Tests end-to-end
│   └── __init__.py                 # Initialisation des tests (0B)
│
├── tools/                          # Outils et scripts utilitaires
│
├── .gitignore                      # Configuration Git globale (534B)
├── docker-compose.yml              # Configuration Docker (1.6KB)
├── requirements.txt                # Dépendances Python (208B)
└── __init__.py                    # Initialisation du projet (0B)

## Description des Composants

### Core (`src/core/`)
- `conversation/` : Gestion des conversations et agents IA
  - Traitement des messages
  - Génération de réponses
  - Gestion du contexte
- `data_collection/` : Collecte et stockage des données
  - Scraping de données médicales
  - Stockage dans SQLite
  - Traitement des données brutes
- `nlp/` : Traitement du langage naturel
  - Analyse de sentiment
  - Extraction d'entités
  - Classification de texte

### Configuration (`config/`)
- `development/` : Configuration de développement
  - Variables d'environnement
  - Paramètres de debug
- `production/` : Configuration de production
  - Paramètres optimisés
  - Sécurité renforcée
- `testing/` : Configuration de tests
  - Environnement de test
  - Données de test

### Données (`data/`)
- `databases/` : Stockage persistant
  - SQLite pour les données structurées
  - Optimisé pour les requêtes fréquentes
- `raw_json/` : Données brutes
  - Format JSON pour flexibilité
  - Conservation des métadonnées
- `processed/` : Données nettoyées
  - Prêtes pour l'analyse
  - Format optimisé

### Documentation (`docs/`)
- Documentation technique (API, architecture)
- Guides d'utilisation et tutoriels
- Plans de monétisation
- Documents de planification et d'amélioration
- Journal des modifications

### Tests (`tests/`)
- Tests unitaires pour les composants
- Tests d'intégration pour les flux
- Tests end-to-end pour les scénarios

## Notes de Maintenance
- Les dossiers vides contiennent des `__init__.py`
- Structure modulaire pour faciliter l'extension
- Documentation dans chaque composant majeur
- Tailles de fichiers indiquées pour référence

*Dernière mise à jour manuelle : 2024-03-13 09:00*
