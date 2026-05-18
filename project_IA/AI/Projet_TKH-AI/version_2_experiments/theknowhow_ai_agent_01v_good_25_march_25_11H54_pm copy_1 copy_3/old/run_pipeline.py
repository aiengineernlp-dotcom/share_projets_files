#!/usr/bin/env python3
"""
Script d'exécution du pipeline de la Phase 1.
Ce script coordonne l'ensemble du processus de collecte et d'analyse des données.
"""

import os
import sys
import asyncio
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Définir les variables d'environnement pour les chemins de stockage si elles ne sont pas déjà définies
if 'MEDICAL_DB_PATH' not in os.environ:
    os.environ['MEDICAL_DB_PATH'] = 'data/databases/medical_websites/medical_data.db'
if 'REDDIT_DB_PATH' not in os.environ:
    os.environ['REDDIT_DB_PATH'] = 'data/databases/social_media/reddit/reddit_data.db'
if 'TWITTER_DB_PATH' not in os.environ:
    os.environ['TWITTER_DB_PATH'] = 'data/databases/social_media/twitter'

# Définir le répertoire racine
root_dir = str(Path(__file__).resolve().parent.parent.parent.parent)

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, root_dir)

# Import du pipeline
from src.core.phase_1_data_collection.pipeline import Phase1Pipeline

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(root_dir, "data/logs/phase1_run.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("phase1_run")

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées."""
    try:
        import tweepy
        import praw
        import aiohttp
        import bs4
        import nltk
        import spacy
        import textblob
        import sklearn
        
        # Vérifier les modèles NLTK
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Téléchargement des ressources NLTK...")
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
        
        # Vérifier les modèles spaCy (ignorer les erreurs)
        try:
            # Ignorer les avertissements de version incompatible
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    spacy.load('en_core_web_sm')
                except Exception as e:
                    logger.warning(f"Impossible de charger le modèle spaCy: {e}")
                    logger.warning("Le traitement NLP avancé pourrait ne pas fonctionner correctement")
        except Exception as e:
            logger.warning(f"Erreur lors de la vérification des modèles spaCy: {e}")
            logger.warning("Le traitement NLP avancé pourrait ne pas fonctionner correctement")
        
        logger.info("Toutes les dépendances sont installées")
        return True
    
    except ImportError as e:
        logger.error(f"Dépendance manquante: {e}")
        logger.error("Veuillez installer toutes les dépendances avec 'pip install -r requirements.txt'")
        return False

def check_directories():
    """Vérifie que tous les dossiers nécessaires existent."""
    directories = [
        "data",
        "data/databases",
        "data/databases/social_media",
        "data/databases/social_media/twitter",
        "data/databases/social_media/reddit",
        "data/databases/medical_websites",
        "data/databases/medical_websites/doctissimo",
        "data/processed",
        "data/processed/doctissimo",
        "data/processed/twitter",
        "data/processed/reddit",
        "data/logs"
    ]
    
    for directory in directories:
        dir_path = os.path.join(root_dir, directory)
        if not os.path.exists(dir_path):
            logger.info(f"Création du dossier {directory}")
            os.makedirs(dir_path, exist_ok=True)
    
    logger.info("Tous les dossiers nécessaires sont présents")
    return True

def check_api_keys():
    """Vérifie que les clés API nécessaires sont définies."""
    # Twitter
    twitter_keys = [
        'TWITTER_API_KEY',
        'TWITTER_API_KEY_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'TWITTER_BEARER_TOKEN'
    ]
    
    # Reddit
    reddit_keys = [
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USER_AGENT'
    ]
    
    missing_keys = []
    
    for key in twitter_keys:
        if not os.environ.get(key):
            missing_keys.append(key)
    
    for key in reddit_keys:
        if not os.environ.get(key):
            missing_keys.append(key)
    
    if missing_keys:
        logger.warning(f"Clés API manquantes: {', '.join(missing_keys)}")
        logger.warning("Certaines fonctionnalités peuvent ne pas fonctionner correctement")
        return False
    
    logger.info("Toutes les clés API sont définies")
    return True

async def run_pipeline(args):
    """Exécute le pipeline de la Phase 1."""
    logger.info("Démarrage du pipeline de la Phase 1")
    
    # Vérifications préliminaires
    if not check_dependencies():
        logger.error("Impossible de continuer sans les dépendances requises")
        return False
    
    check_directories()
    
    # Vérification des clés API, mais on peut continuer même si elles sont manquantes
    api_keys_ok = check_api_keys()
    if not api_keys_ok and not args.ignore_auth_errors:
        logger.warning("Des clés API sont manquantes, mais on continue car --ignore-auth-errors est activé")
    
    # Initialisation du pipeline
    pipeline = Phase1Pipeline()
    
    # Exécution du pipeline selon les options
    if args.collect_only:
        await pipeline.collect_data()
    elif args.process_only:
        await pipeline.process_data()
    elif args.analyze_only:
        await pipeline.analyze_data()
    else:
        await pipeline.run()
    
    logger.info("Pipeline de la Phase 1 terminé avec succès")
    return True

def parse_arguments():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description="Exécute le pipeline de la Phase 1")
    parser.add_argument("--collect-only", action="store_true", help="Exécute uniquement la collecte de données")
    parser.add_argument("--process-only", action="store_true", help="Exécute uniquement le traitement des données")
    parser.add_argument("--analyze-only", action="store_true", help="Exécute uniquement l'analyse et la classification des données")
    parser.add_argument("--ignore-auth-errors", action="store_true", help="Ignore les erreurs d'authentification API")
    return parser.parse_args()

if __name__ == "__main__":
    # Parse les arguments
    args = parse_arguments()
    
    # Exécution du pipeline
    success = asyncio.run(run_pipeline(args))
    
    # Code de sortie
    sys.exit(0 if success else 1) 