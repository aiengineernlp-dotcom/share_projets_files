"""
Module d'initialisation de la phase 1 de collecte de données.

RÔLE PRINCIPAL :
---------------
Ce module initialise le package de la phase 1 de collecte de données.
Il définit les constantes, les chemins et les configurations globales
nécessaires au bon fonctionnement de tous les composants du système.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * run_phase1.py (script principal)
  * phase1.py (logique principale)
  * tous les sous-modules du package

- Configure les chemins pour :
  * config/ (fichiers de configuration)
  * logs/ (fichiers de logs)
  * data/ (données collectées)
  * models/ (modèles NLP)

STRUCTURE DU CONTENU :
--------------------
1. Imports système
2. Définition des chemins :
   - ROOT_DIR : Répertoire racine du projet
   - CONFIG_DIR : Répertoire des configurations
   - DATA_DIR : Répertoire des données
   - LOGS_DIR : Répertoire des logs
3. Configuration du logging
4. Initialisation des variables d'environnement

FONCTIONS PRINCIPALES :
---------------------
- setup_paths() : Configure les chemins du projet
- init_logging() : Initialise le système de logging
- load_env_vars() : Charge les variables d'environnement

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il initialise l'environnement du projet
- Il définit les chemins essentiels
- Il configure le logging global
- Il est importé par tous les autres modules
"""

__version__ = "0.1" 

"""
Phase 1 Data Collection Package
This package contains all the scrapers and processors for collecting health-related data
from various sources including forums and social media platforms.
"""

__version__ = '1.0.0' 