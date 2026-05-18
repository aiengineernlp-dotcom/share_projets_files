# ==============================================
# FICHIER D'AUTOMATISATION MAKE
# ==============================================
#
# RÔLE PRINCIPAL :
# --------------
# Ce Makefile automatise les tâches courantes du développement et du déploiement.
# Il fournit des commandes pour :
# - L'installation des dépendances
# - L'exécution des tests
# - La vérification du code
# - Le nettoyage du projet
# - La sauvegarde des données
#
# RELATIONS AVEC LES AUTRES FICHIERS :
# ---------------------------------
# - requirements.txt : Dépendances à installer
# - pyproject.toml : Configuration des outils
# - .env : Variables d'environnement
# - data/* : Données à sauvegarder
#
# STRUCTURE DU CONTENU :
# --------------------
# Le fichier est organisé en sections :
# 1. Variables globales
# 2. Commandes principales :
#    - help : Affiche l'aide
#    - install : Installation des dépendances
#    - test : Exécution des tests
#    - lint : Vérification du code
#    - format : Formatage du code
#    - clean : Nettoyage
#    - run : Lancement de l'application
#    - backup : Sauvegarde des données
#    - docs : Génération de la documentation
#    - coverage : Rapport de couverture
#
# IMPORTANCE ET SUPPRESSION :
# -------------------------
# Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
# - Il automatise les tâches de développement
# - Il standardise les commandes du projet
# - Il facilite l'intégration continue
# - Il assure la cohérence des opérations
#
# NOTE DE MAINTENANCE :
# -------------------
# - Maintenir à jour les commandes
# - Documenter les nouvelles commandes
# - Vérifier la compatibilité des outils
# - Tester les commandes après modification
#
# ==============================================

.PHONY: help install test lint format clean run backup docs coverage

# Variables
PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
BLACK := $(VENV)/bin/black
FLAKE8 := $(VENV)/bin/flake8
ISORT := $(VENV)/bin/isort
COVERAGE := $(VENV)/bin/coverage

help:
	@echo "Commandes disponibles:"
	@echo "  make install    - Installe les dépendances"
	@echo "  make test      - Lance les tests"
	@echo "  make lint      - Vérifie le style du code"
	@echo "  make format    - Formate le code"
	@echo "  make clean     - Nettoie les fichiers temporaires"
	@echo "  make run       - Lance l'application"
	@echo "  make backup    - Sauvegarde les données"
	@echo "  make docs      - Génère la documentation"
	@echo "  make coverage  - Génère le rapport de couverture"

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PYTHON) -m spacy download fr_core_news_lg

test:
	$(PYTEST) tests/ -v --cov=src

lint:
	$(FLAKE8) phase1_data_collection/
	$(BLACK) --check phase1_data_collection/
	$(ISORT) --check-only phase1_data_collection/

format:
	$(BLACK) phase1_data_collection/
	$(ISORT) phase1_data_collection/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +

run:
	$(PYTHON) phase1_data_collection/run_scraper.py

backup:
	@echo "Sauvegarde des données..."
	@mkdir -p backups
	@tar -czf backups/data_$(shell date +%Y%m%d_%H%M%S).tar.gz data/
	@echo "Sauvegarde terminée"

docs:
	cd docs && make html
	@echo "Documentation générée dans docs/_build/html/"

coverage:
	$(COVERAGE) run -m pytest tests/
	$(COVERAGE) report
	$(COVERAGE) html
	@echo "Rapport de couverture généré dans htmlcov/"

setup-dev: install
	$(PIP) install -r requirements-dev.txt
	pre-commit install

test-quick:
	$(PYTEST) tests/ -v -m "not slow"

test-full: test lint coverage

validate:
	$(PYTHON) scripts/validate_config.py
	$(PYTHON) scripts/check_dependencies.py

check-security:
	$(PYTHON) scripts/security_check.py
	$(PYTHON) scripts/check_vulnerabilities.py

update-deps:
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) freeze > requirements.txt

clean-data:
	@echo "Nettoyage des données..."
	$(PYTHON) scripts/clean_data.py
	@echo "Nettoyage terminé"

optimize-db:
	@echo "Optimisation de la base de données..."
	$(PYTHON) scripts/optimize_db.py
	@echo "Optimisation terminée"

check-quality:
	$(PYTHON) scripts/check_code_quality.py
	$(PYTHON) scripts/check_test_coverage.py
	$(PYTHON) scripts/check_documentation.py 