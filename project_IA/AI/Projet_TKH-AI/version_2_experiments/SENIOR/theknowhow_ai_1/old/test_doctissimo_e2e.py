"""
Tests end-to-end pour le scraper Doctissimo.
Ces tests effectuent des requêtes réelles sur le site Doctissimo.
"""

import pytest
import os
import tempfile
import sqlite3
import json
from datetime import datetime, timedelta
import asyncio
import logging
from pathlib import Path

from core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper import DoctissimoScraper

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
        'base_url': 'https://www.doctissimo.fr',
        'categories': ['sante', 'medicaments'],  # Limité pour les tests
        'scraping': {
            'max_pages_per_category': 2,  # Limité pour les tests
            'max_concurrent_requests': 2,
            'request_delay': 1.0,  # Délai pour éviter la détection
            'timeout': 30
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
        },
        'storage': {
            'database_path': os.path.join(db_dir, "doctissimo_test.db"),
            'media_path': media_dir,
            'backup_path': backup_dir
        },
        'logging': {
            'file_path': os.path.join(log_dir, "doctissimo_test.log"),
            'level': 'INFO'
        }
    }

    env_data = {
        'base_dir': base_dir,
        'config': config,
        'db_path': os.path.join(db_dir, "doctissimo_test.db"),
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

@pytest.mark.asyncio
async def test_full_scraping_cycle(test_env):
    """
    Teste un cycle complet de scraping avec une vraie connexion à Doctissimo.
    Ce test effectue des requêtes réelles sur le site.
    """
    try:
        # Initialisation du scraper
        scraper = DoctissimoScraper()
        scraper.config = test_env['config']

        # Exécution du scraping
        await scraper.run()
        logger.info(f"Scraping terminé. Métriques: {scraper.metrics}")

        # Vérification des résultats
        assert scraper.metrics['articles_collected'] > 0, "Aucun article n'a été collecté"
        assert scraper.metrics['pages_scraped'] > 0, "Aucune page n'a été scrapée"
        
        # Vérification de la base de données
        conn = sqlite3.connect(test_env['db_path'])
        cursor = conn.cursor()
        
        # Vérification de la structure de la base
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        assert ('medical_articles',) in tables, "La table des articles n'existe pas"
        
        # Vérification des données
        cursor.execute("SELECT COUNT(*) FROM medical_articles")
        article_count = cursor.fetchone()[0]
        assert article_count > 0, "Aucun article n'a été sauvegardé en base"
        
        # Vérification du contenu des articles
        cursor.execute("""
            SELECT title, content, author, source, category, url, 
                   collected_at, created_at
            FROM medical_articles 
            LIMIT 1
        """)
        row = cursor.fetchone()
        assert row is not None, "Impossible de récupérer un article"
        assert all(field is not None for field in row), "Certains champs sont manquants"
        
        # Vérification des fichiers de log
        log_file = test_env['config']['logging']['file_path']
        assert os.path.exists(log_file), "Le fichier de log n'a pas été créé"
        assert os.path.getsize(log_file) > 0, "Le fichier de log est vide"

        conn.close()

    except Exception as e:
        logger.error(f"Erreur lors du test E2E: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_category_scraping(test_env):
    """
    Teste le scraping d'une catégorie spécifique.
    """
    try:
        scraper = DoctissimoScraper()
        scraper.config = test_env['config']
        scraper.categories = ['sante']  # Test sur une seule catégorie
        
        await scraper.run()
        
        # Vérification en base de données
        conn = sqlite3.connect(test_env['db_path'])
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT category 
            FROM medical_articles
        """)
        categories = cursor.fetchall()
        
        assert len(categories) == 1, "Plus d'une catégorie trouvée"
        assert categories[0][0] == 'sante', "Mauvaise catégorie"
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur lors du test de catégorie: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_backup_functionality(test_env):
    """
    Teste la fonctionnalité de sauvegarde.
    """
    try:
        scraper = DoctissimoScraper()
        scraper.config = test_env['config']
        
        # Exécution d'un scraping limité
        scraper.categories = ['sante']
        scraper.config['scraping']['max_pages_per_category'] = 1
        
        await scraper.run()
        
        # Vérification des sauvegardes
        backup_files = list(Path(test_env['backup_dir']).glob('*.json'))
        assert len(backup_files) > 0, "Aucun fichier de sauvegarde créé"
        
        # Vérification du contenu de la sauvegarde
        with open(backup_files[0], 'r') as f:
            backup_data = json.load(f)
            assert 'articles_collected' in backup_data
            assert backup_data['articles_collected'] > 0
            
    except Exception as e:
        logger.error(f"Erreur lors du test de sauvegarde: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_long_running_stability(test_env):
    """
    Teste la stabilité du scraper sur une période plus longue.
    """
    try:
        scraper = DoctissimoScraper()
        scraper.config = test_env['config']
        
        # Configuration pour un test plus long
        scraper.categories = ['sante', 'medicaments']
        scraper.config['scraping']['max_pages_per_category'] = 5
        
        start_time = datetime.now()
        await scraper.run()
        end_time = datetime.now()
        
        # Le test devrait durer au moins quelques minutes
        duration = end_time - start_time
        assert duration > timedelta(minutes=1), "Le test s'est terminé trop rapidement"
        
        # Vérification des métriques
        assert scraper.metrics['errors'] == 0, "Des erreurs sont survenues"
        assert scraper.metrics['articles_collected'] > 10, "Trop peu d'articles collectés"
        
    except Exception as e:
        logger.error(f"Erreur lors du test de stabilité: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main([__file__, '-v']) 