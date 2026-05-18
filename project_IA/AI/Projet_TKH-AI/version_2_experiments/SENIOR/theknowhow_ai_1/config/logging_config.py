"""
Configuration du système de logging.
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 15-21 : configuration logging)
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from .settings import LOGS_DIR

# Création du dossier logs s'il n'existe pas
os.makedirs(os.path.join(LOGS_DIR, "error"), exist_ok=True)
os.makedirs(os.path.join(LOGS_DIR, "access"), exist_ok=True)

# Configuration du format de logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Configuration du logging de base
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)

# Création du logger principal
logger = logging.getLogger("theknowhow_ai")
logger.setLevel(logging.INFO)

# Handler pour les logs d'erreur
error_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, "error", "error.log"),
    maxBytes=10485760,  # 10MB
    backupCount=5
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(error_handler)

# Handler pour les logs d'accès
access_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, "access", "access.log"),
    maxBytes=10485760,  # 10MB
    backupCount=5
)
access_handler.setLevel(logging.INFO)
access_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(access_handler)

# Handler pour la console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(console_handler) 