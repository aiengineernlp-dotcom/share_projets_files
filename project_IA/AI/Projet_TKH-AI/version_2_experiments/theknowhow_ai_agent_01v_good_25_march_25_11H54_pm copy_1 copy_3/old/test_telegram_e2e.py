"""
Tests end-to-end pour le scraper Telegram.
"""

import pytest
import os
import tempfile
from pathlib import Path
import sqlite3
import json
from datetime import datetime, timedelta
import asyncio
import logging

from core.data_collection.scrapers.social_media.telegram_scraper import TelegramScraper
from core.data_collection.storage.sqlite_storage import SQLiteStorage
from core.utils.config import load_config

# Configuration du logging pour les tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def test_env():
    """Crée un environnement de test complet."""
    # Création des dossiers temporaires
    base_dir = tempfile.mkdtemp()
    db_dir = os.path.join(base_dir, "databases")
    media_dir = os.path.join(base_dir, "media")
    backup_dir = os.path.join(base_dir, "backups")
    log_dir = os.path.join(base_dir, "logs")

    # Création de la structure des dossiers
    for dir_path in [db_dir, media_dir, backup_dir, log_dir]:
        os.makedirs(dir_path, exist_ok=True)

    # Configuration de test
    config = {
        'api': {
            'api_id': os.getenv('TELEGRAM_API_ID', ''),
            'api_hash': os.getenv('TELEGRAM_API_HASH', ''),
            'phone_number': os.getenv('TELEGRAM_PHONE', ''),
            'session_name': 'test_session'
        },
        'scraping': {
            'max_message_age_days': 1,  # Limité pour les tests
            'min_message_length': 10,
            'collect_media': True,
            'batch_size': 10
        },
        'medical_channels': [
            os.getenv('TELEGRAM_TEST_CHANNEL', 'test_medical_channel')
        ],
        'medical_keywords': ['medical', 'health', 'doctor', 'patient'],
        'storage': {
            'database_path': os.path.join(db_dir, "telegram_test.db"),
            'media_path': media_dir,
            'backup_path': backup_dir
        },
        'logging': {
            'file_path': os.path.join(log_dir, "telegram_test.log"),
            'level': 'INFO'
        }
    }

    env_data = {
        'base_dir': base_dir,
        'config': config,
        'db_path': os.path.join(db_dir, "telegram_test.db"),
        'media_dir': media_dir,
        'backup_dir': backup_dir,
        'log_dir': log_dir
    }

    yield env_data

    # Nettoyage après les tests
    try:
        for root, dirs, files in os.walk(base_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(base_dir)
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {str(e)}")

@pytest.mark.skipif(
    not (os.getenv('TELEGRAM_API_ID') and os.getenv('TELEGRAM_API_HASH')),
    reason="Les credentials Telegram ne sont pas configurés"
)
@pytest.mark.asyncio
async def test_full_scraping_cycle(test_env):
    """
    Teste un cycle complet de scraping avec une vraie connexion à Telegram.
    
    Ce test nécessite des credentials Telegram valides et une connexion internet.
    Il effectue un véritable scraping sur un canal de test.
    """
    try:
        # Initialisation du scraper
        scraper = TelegramScraper()
        scraper.config = test_env['config']

        # Connexion à Telegram
        assert await scraper.connect(), "La connexion à Telegram a échoué"
        logger.info("Connexion à Telegram réussie")

        # Exécution du scraping
        await scraper.run()
        logger.info(f"Scraping terminé. Métriques: {scraper.metrics}")

        # Vérification des résultats
        assert scraper.metrics['errors'] == 0, "Des erreurs sont survenues pendant le scraping"
        
        # Vérification de la base de données
        conn = sqlite3.connect(test_env['db_path'])
        cursor = conn.cursor()
        
        # Vérification de la structure de la base
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert ('telegram_messages',) in tables, "La table des messages n'existe pas"
        
        # Vérification des données
        cursor.execute("SELECT COUNT(*) FROM telegram_messages")
        message_count = cursor.fetchone()[0]
        assert message_count > 0, "Aucun message n'a été collecté"
        
        # Vérification du contenu des messages
        cursor.execute("""
            SELECT content, author, channel, created_at, collected_at 
            FROM telegram_messages 
            LIMIT 1
        """)
        row = cursor.fetchone()
        assert all(x is not None for x in row), "Certains champs sont manquants"
        
        conn.close()
        
        # Vérification des fichiers médias
        if test_env['config']['scraping']['collect_media']:
            media_files = os.listdir(test_env['media_dir'])
            logger.info(f"Fichiers médias trouvés: {media_files}")
        
        # Vérification des logs
        log_file = test_env['config']['logging']['file_path']
        assert os.path.exists(log_file), "Le fichier de log n'a pas été créé"
        assert os.path.getsize(log_file) > 0, "Le fichier de log est vide"

    except Exception as e:
        logger.error(f"Erreur lors du test E2E: {str(e)}")
        raise

@pytest.mark.skipif(
    not (os.getenv('TELEGRAM_API_ID') and os.getenv('TELEGRAM_API_HASH')),
    reason="Les credentials Telegram ne sont pas configurés"
)
@pytest.mark.asyncio
async def test_incremental_scraping(test_env):
    """
    Teste le scraping incrémental sur plusieurs exécutions.
    """
    try:
        scraper = TelegramScraper()
        scraper.config = test_env['config']
        
        # Premier scraping
        await scraper.run()
        first_count = scraper.metrics['items_collected']
        
        # Deuxième scraping (devrait trouver moins ou pas de nouveaux messages)
        await scraper.run()
        second_count = scraper.metrics['items_collected']
        
        assert second_count <= first_count, "Le deuxième scraping a trouvé plus de messages que le premier"
        
    except Exception as e:
        logger.error(f"Erreur lors du test de scraping incrémental: {str(e)}")
        raise

@pytest.mark.skipif(
    not (os.getenv('TELEGRAM_API_ID') and os.getenv('TELEGRAM_API_HASH')),
    reason="Les credentials Telegram ne sont pas configurés"
)
def test_backup_functionality(test_env):
    """
    Teste la fonctionnalité de sauvegarde des données.
    """
    try:
        # Création d'une sauvegarde
        backup_file = os.path.join(
            test_env['backup_dir'],
            f"telegram_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        # Lecture des données de la base
        conn = sqlite3.connect(test_env['db_path'])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telegram_messages")
        rows = cursor.fetchall()
        conn.close()
        
        # Sauvegarde des données
        with open(backup_file, 'w') as f:
            json.dump({
                'messages': [dict(zip([col[0] for col in cursor.description], row))
                           for row in rows]
            }, f)
        
        assert os.path.exists(backup_file), "Le fichier de sauvegarde n'a pas été créé"
        assert os.path.getsize(backup_file) > 0, "Le fichier de sauvegarde est vide"
        
    except Exception as e:
        logger.error(f"Erreur lors du test de sauvegarde: {str(e)}")
        raise 