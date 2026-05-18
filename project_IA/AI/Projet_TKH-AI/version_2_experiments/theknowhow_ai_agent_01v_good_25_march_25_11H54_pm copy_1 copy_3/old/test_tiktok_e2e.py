"""
Tests end-to-end pour le scraper TikTok.
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

from core.phase_1_data_collection.scrapers.social_media.tiktok_scraper import TikTokScraper
from core.phase_1_data_collection.storage.sqlite_storage import SQLiteStorage
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
        'auth': {
            'session_id': os.getenv('TIKTOK_SESSION_ID', ''),
            'user_agent': os.getenv('TIKTOK_USER_AGENT', 'Mozilla/5.0')
        },
        'scraping': {
            'max_video_age_days': 1,  # Limité pour les tests
            'min_likes': 100,
            'min_comments': 10,
            'collect_comments': True,
            'max_videos_per_hashtag': 10  # Limité pour les tests
        },
        'medical_hashtags': ['medecine', 'health', 'doctor'],
        'medical_accounts': [os.getenv('TIKTOK_TEST_ACCOUNT', 'doctorsoftiktok')],
        'storage': {
            'database_path': os.path.join(db_dir, "tiktok_test.db"),
            'media_path': media_dir,
            'backup_path': backup_dir
        },
        'logging': {
            'file_path': os.path.join(log_dir, "tiktok_test.log"),
            'level': 'INFO'
        }
    }

    env_data = {
        'base_dir': base_dir,
        'config': config,
        'db_path': os.path.join(db_dir, "tiktok_test.db"),
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
    not os.getenv('TIKTOK_SESSION_ID'),
    reason="Les credentials TikTok ne sont pas configurés"
)
@pytest.mark.asyncio
async def test_full_scraping_cycle(test_env):
    """
    Teste un cycle complet de scraping avec une vraie connexion à TikTok.
    
    Ce test nécessite des credentials TikTok valides et une connexion internet.
    Il effectue un véritable scraping sur des hashtags et comptes médicaux.
    """
    try:
        # Initialisation du scraper
        scraper = TikTokScraper()
        scraper.config = test_env['config']

        # Connexion à TikTok
        assert await scraper.connect(), "La connexion à TikTok a échoué"
        logger.info("Connexion à TikTok réussie")

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
        assert ('tiktok_videos',) in tables, "La table des vidéos n'existe pas"
        
        # Vérification des données
        cursor.execute("SELECT COUNT(*) FROM tiktok_videos")
        video_count = cursor.fetchone()[0]
        assert video_count > 0, "Aucune vidéo n'a été collectée"
        
        # Vérification du contenu des vidéos
        cursor.execute("""
            SELECT video_id, description, author, likes, comments, created_at, collected_at 
            FROM tiktok_videos 
            LIMIT 1
        """)
        row = cursor.fetchone()
        assert all(x is not None for x in row), "Certains champs sont manquants"
        
        conn.close()
        
        # Vérification des fichiers médias
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
    not os.getenv('TIKTOK_SESSION_ID'),
    reason="Les credentials TikTok ne sont pas configurés"
)
@pytest.mark.asyncio
async def test_hashtag_scraping(test_env):
    """
    Teste spécifiquement le scraping par hashtag.
    """
    try:
        scraper = TikTokScraper()
        scraper.config = test_env['config']
        await scraper.connect()
        
        # Test avec un hashtag médical spécifique
        test_hashtag = "health"
        videos = await scraper._get_videos_by_hashtag(test_hashtag)
        
        assert len(videos) > 0, f"Aucune vidéo trouvée pour le hashtag #{test_hashtag}"
        
        # Vérification du contenu des vidéos
        for video in videos[:5]:  # Vérifie les 5 premières vidéos
            assert hasattr(video, 'id'), "La vidéo n'a pas d'ID"
            assert hasattr(video, 'desc'), "La vidéo n'a pas de description"
            assert hasattr(video, 'author'), "La vidéo n'a pas d'auteur"
            
    except Exception as e:
        logger.error(f"Erreur lors du test de scraping par hashtag: {str(e)}")
        raise

@pytest.mark.skipif(
    not os.getenv('TIKTOK_SESSION_ID'),
    reason="Les credentials TikTok ne sont pas configurés"
)
@pytest.mark.asyncio
async def test_user_scraping(test_env):
    """
    Teste spécifiquement le scraping par utilisateur.
    """
    try:
        scraper = TikTokScraper()
        scraper.config = test_env['config']
        await scraper.connect()
        
        # Test avec un compte médical spécifique
        test_account = test_env['config']['medical_accounts'][0]
        videos = await scraper._get_videos_by_user(test_account)
        
        assert len(videos) > 0, f"Aucune vidéo trouvée pour le compte {test_account}"
        
        # Vérification du contenu des vidéos
        for video in videos[:5]:  # Vérifie les 5 premières vidéos
            assert hasattr(video, 'id'), "La vidéo n'a pas d'ID"
            assert hasattr(video, 'desc'), "La vidéo n'a pas de description"
            assert video.author.unique_id == test_account, "L'auteur ne correspond pas"
            
    except Exception as e:
        logger.error(f"Erreur lors du test de scraping par utilisateur: {str(e)}")
        raise

@pytest.mark.skipif(
    not os.getenv('TIKTOK_SESSION_ID'),
    reason="Les credentials TikTok ne sont pas configurés"
)
def test_backup_functionality(test_env):
    """
    Teste la fonctionnalité de sauvegarde des données.
    """
    try:
        # Création d'une sauvegarde
        backup_file = os.path.join(
            test_env['backup_dir'],
            f"tiktok_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        # Lecture des données de la base
        conn = sqlite3.connect(test_env['db_path'])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tiktok_videos")
        rows = cursor.fetchall()
        conn.close()
        
        # Sauvegarde des données
        with open(backup_file, 'w') as f:
            json.dump({
                'videos': [dict(zip([col[0] for col in cursor.description], row))
                          for row in rows]
            }, f)
        
        assert os.path.exists(backup_file), "Le fichier de sauvegarde n'a pas été créé"
        assert os.path.getsize(backup_file) > 0, "Le fichier de sauvegarde est vide"
        
    except Exception as e:
        logger.error(f"Erreur lors du test de sauvegarde: {str(e)}")
        raise 