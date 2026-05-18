# ==============================================
# DOCUMENTATION D'ARCHITECTURE
# ==============================================
#
# RÔLE PRINCIPAL :
# --------------
# Ce document ARCHITECTURE.md décrit l'architecture globale du projet de collecte
# de données médicales. Il explique :
# - La structure du projet
# - Les composants principaux
# - Les interactions entre modules
# - Les choix architecturaux
#
# RELATIONS AVEC LES AUTRES FICHIERS :
# ---------------------------------
# - README.md : Vue d'ensemble du projet
# - docs/* : Documentation détaillée des modules
# - config/* : Fichiers de configuration
# - src/* : Code source
#
# STRUCTURE DU CONTENU :
# --------------------
# Le document est organisé en sections :
# 1. Vue d'Ensemble
# 2. Fichiers de Configuration
#    - Configuration Principale
#    - Tests et Qualité
# 3. Docker et Déploiement
#    - Configuration Docker
#    - Monitoring
# 4. Documentation
#    - Documentation Générale
#    - Documentation des Modules
# 5. Automatisation
#    - Scripts et Outils
# 6. Structure des Modules
#    - NLP
#    - Processors
#    - Scrapers
#    - Storage
#    - Configuration
#    - Tests
#
# IMPORTANCE ET SUPPRESSION :
# -------------------------
# Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
# - Il documente l'architecture du projet
# - Il guide les développeurs
# - Il facilite la maintenance
# - Il assure la cohérence du code
#
# NOTE DE MAINTENANCE :
# -------------------
# - Maintenir à jour avec les changements architecturaux
# - Documenter les nouvelles fonctionnalités
# - Vérifier la cohérence avec le code
# - Mettre à jour les diagrammes si présents
#
# ==============================================

# Architecture du Projet

## 📋 Vue d'Ensemble
Ce document explique la raison d'être de chaque fichier et composant du projet de collecte de données médicales.

## 🔧 Fichiers de Configuration

### Configuration Principale
- `.env.example` : Modèle de configuration des variables d'environnement pour différents contextes (développement, production, test).
- `pyproject.toml` : Configuration centrale des outils Python (black, pytest, mypy) pour maintenir la qualité du code.
- `.pylintrc` : Règles de style et conventions de code Python pour assurer la cohérence.
- `.pre-commit-config.yaml` : Vérifications automatiques avant chaque commit pour prévenir les erreurs.

### Tests et Qualité
- `pytest.ini` : Configuration des tests automatisés pour garantir la fiabilité du code.
- `setup.py` : Configuration de l'installation du package pour le déploiement.
- `requirements.txt` : Liste des dépendances Python pour reproduire l'environnement.

## 🐳 Docker et Déploiement

### Configuration Docker
- `Dockerfile` : Instructions de construction de l'image Docker pour l'isolation et la portabilité.
- `docker-compose.yml` : Orchestration des services (app, base de données, cache, monitoring).
- `.dockerignore` : Liste des fichiers à exclure de l'image Docker pour l'optimisation.

### Monitoring
- `monitoring/prometheus/prometheus.yml` : Configuration de la collecte de métriques.
- `monitoring/prometheus/rules/alerts.yml` : Règles d'alertes pour la surveillance.
- `monitoring/grafana/dashboards/medical_data_collection.json` : Tableaux de bord de visualisation.

## 📚 Documentation

### Documentation Générale
- `README.md` : Point d'entrée de la documentation, vue d'ensemble du projet.
- `DEPENDENCIES.md` : Documentation des dépendances entre composants.
- `LICENSE.md` : Licence MIT définissant les conditions d'utilisation.

### Documentation des Modules
- `nlp/README.md` : Documentation du traitement du langage naturel.
- `processors/README.md` : Documentation du traitement des données.
- `scrapers/README.md` : Documentation de la collecte de données.
- `storage/README.md` : Documentation du stockage des données.

## 🔄 Automatisation

### Scripts et Outils
- `Makefile` : Automatisation des tâches courantes (installation, tests, build).
- `.gitignore` : Liste des fichiers à ignorer dans le contrôle de version.

## 🏗️ Structure des Modules

### NLP (Natural Language Processing)
- Raison : Analyse et compréhension du texte médical
- Composants :
  - `keywords/` : Définition des termes médicaux
  - `analysis/` : Analyse des textes
  - `utils/` : Outils communs

### Processors
- Raison : Traitement et transformation des données
- Composants :
  - `base/` : Classes de base
  - `medical/` : Traitement spécifique médical
  - `scoring/` : Système de scoring

### Scrapers
- Raison : Collecte de données depuis diverses sources
- Composants :
  - `base/` : Classes de base
  - `platforms/` : Scrapers spécifiques
  - `utils/` : Outils de scraping

### Storage
- Raison : Persistance et gestion des données
- Composants :
  - `database/` : Gestion base de données
  - `cache/` : Système de cache
  - `backup/` : Sauvegarde des données

## 🔐 Sécurité et Monitoring

### Sécurité
- Configuration SSL/TLS
- Gestion des secrets
- Protection des données sensibles

### Monitoring
- Métriques système
- Métriques applicatives
- Alertes et notifications

## 📈 Évolution et Maintenance

### Versioning
- Gestion des versions
- Migration des données
- Compatibilité ascendante

### Tests
- Tests unitaires
- Tests d'intégration
- Tests de performance

## 🚀 Déploiement

### Infrastructure
- Conteneurisation
- Orchestration
- Mise à l'échelle

### CI/CD
- Intégration continue
- Déploiement continu
- Qualité du code 