# ==============================================
# FICHIER DE CONFIGURATION D'INSTALLATION
# ==============================================
#
# RÔLE PRINCIPAL :
# --------------
# Ce fichier setup.py configure l'installation du package Python.
# Il définit :
# - Les métadonnées du package
# - Les dépendances
# - Les scripts d'installation
# - Les données additionnelles
#
# RELATIONS AVEC LES AUTRES FICHIERS :
# ---------------------------------
# - pyproject.toml : Configuration générale du projet
# - requirements.txt : Dépendances directes
# - MANIFEST.in : Fichiers à inclure
# - setup.cfg : Configuration additionnelle
#
# STRUCTURE DU CONTENU :
# --------------------
# Le fichier est organisé en sections :
# 1. Imports et configuration
# 2. Métadonnées du package
# 3. Dépendances
# 4. Scripts d'installation
# 5. Configuration de build
# 6. Données additionnelles
#
# IMPORTANCE ET SUPPRESSION :
# -------------------------
# Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
# - Il permet l'installation du package
# - Il gère les dépendances
# - Il configure le build
# - Il est requis par pip
#
# NOTE DE MAINTENANCE :
# -------------------
# - Maintenir à jour les versions
# - Vérifier les dépendances
# - Optimiser l'installation
# - Documenter les changements
#
# ==============================================

from setuptools import setup, find_packages

setup(
    name="phase1_data_collection",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "beautifulsoup4",
        "spacy",
        "tqdm",
        "requests",
        "numpy",
        "pandas"
    ]
) 