"""
Tests d'intégration pour le scraper Doctissimo.
"""

import pytest
import os
import tempfile
import sqlite3
from datetime import datetime
from unittest.mock import patch, AsyncMock
import aiohttp
from bs4 import BeautifulSoup

from core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper import DoctissimoScraper

@pytest.fixture
def temp_test_env():
    """Crée un environnement de test temporaire."""
    base_dir = tempfile.mkdtemp()
    db_dir = os.path.join(base_dir, "db")
    media_dir = os.path.join(base_dir, "media")
    backup_dir = os.path.join(base_dir, "backup")
    log_dir = os.path.join(base_dir, "logs")

    # Création des dossiers
    for dir_path in [db_dir, media_dir, backup_dir, log_dir]:
        os.makedirs(dir_path)

    env = {
        'base_dir': base_dir,
        'db_path': os.path.join(db_dir, "test_doctissimo.db"),
        'media_dir': media_dir,
        'backup_dir': backup_dir,
        'log_dir': log_dir
    }

    yield env

    # Nettoyage
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(base_dir)

@pytest.fixture
def test_config(temp_test_env):
    """Crée une configuration de test."""
    return {
        'base_url': 'https://www.doctissimo.fr',
        'categories': ['sante'],
        'scraping': {
            'max_pages_per_category': 2,
            'max_concurrent_requests': 2,
            'request_delay': 0.1
        },
        'storage': {
            'database_path': temp_test_env['db_path'],
            'media_path': temp_test_env['media_dir'],
            'backup_path': temp_test_env['backup_dir']
        },
        'logging': {
            'file_path': os.path.join(temp_test_env['log_dir'], 'test.log'),
            'level': 'INFO'
        }
    }

@pytest.fixture
def mock_article_response():
    """Simule une réponse d'article."""
    return """
    <html>
        <head><title>Article Test Complet</title></head>
        <body>
            <h1 class="title-article">Article Médical de Test</h1>
            <time datetime="2024-03-13T10:00:00Z"></time>
            <span class="author-name">Dr. Test Integration</span>
            <div class="article-content">
                <p>Ceci est un article médical de test pour l'intégration.</p>
                <p>Il contient plusieurs paragraphes avec des informations médicales.</p>
            </div>
            <div class="tags">
                <a class="tag">santé</a>
                <a class="tag">médecine</a>
                <a class="tag">test</a>
            </div>
        </body>
    </html>
    """

@pytest.fixture
def mock_list_response():
    """Simule une réponse de liste d'articles."""
    return """
    <html>
        <body>
            <div class="article-list">
                <a class="article-card-link" href="/sante/article1">Article 1</a>
                <a class="article-card-link" href="/sante/article2">Article 2</a>
                <a class="article-card-link" href="/sante/article3">Article 3</a>
            </div>
        </body>
    </html>
    """

@pytest.mark.asyncio
async def test_full_scraping_workflow(test_config, mock_article_response, mock_list_response):
    """Teste le workflow complet de scraping."""
    with patch('core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper.load_config',
              return_value=test_config):
        scraper = DoctissimoScraper()

        # Mock des requêtes HTTP
        async def mock_get(*args, **kwargs):
            class MockResponse:
                async def __aenter__(self):
                    return self
                
                async def __aexit__(self, *args):
                    pass
                
                @property
                def status(self):
                    return 200
                
                async def text(self):
                    if 'article' in args[0]:
                        return mock_article_response
                    return mock_list_response

            return MockResponse()

        with patch('aiohttp.ClientSession.get', side_effect=mock_get):
            await scraper.run()

            # Vérification des métriques
            assert scraper.metrics['articles_collected'] > 0
            assert scraper.metrics['errors'] == 0
            assert scraper.metrics['pages_scraped'] > 0

            # Vérification de la base de données
            conn = sqlite3.connect(test_config['storage']['database_path'])
            cursor = conn.cursor()
            
            # Vérification de la table des articles
            cursor.execute("SELECT COUNT(*) FROM medical_articles")
            article_count = cursor.fetchone()[0]
            assert article_count > 0

            # Vérification du contenu d'un article
            cursor.execute("""
                SELECT title, author, source, category 
                FROM medical_articles 
                LIMIT 1
            """)
            row = cursor.fetchone()
            assert row is not None
            assert "Article Médical" in row[0]
            assert "Dr. Test" in row[1]
            assert row[2] == "Doctissimo"
            assert row[3] == "sante"

            conn.close()

@pytest.mark.asyncio
async def test_incremental_scraping(test_config, mock_article_response, mock_list_response):
    """Teste le scraping incrémental."""
    with patch('core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper.load_config',
              return_value=test_config):
        scraper = DoctissimoScraper()

        # Premier scraping
        with patch('aiohttp.ClientSession.get',
                  new_callable=AsyncMock) as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 200
            mock_get.return_value.__aenter__.return_value.text = AsyncMock(
                return_value=mock_article_response
            )
            
            await scraper.run()
            first_count = scraper.metrics['articles_collected']

        # Deuxième scraping
        with patch('aiohttp.ClientSession.get',
                  new_callable=AsyncMock) as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 200
            mock_get.return_value.__aenter__.return_value.text = AsyncMock(
                return_value=mock_article_response
            )
            
            await scraper.run()
            second_count = scraper.metrics['articles_collected']

        # Le deuxième scraping devrait trouver moins ou autant d'articles
        assert second_count >= first_count

@pytest.mark.asyncio
async def test_error_recovery(test_config):
    """Teste la récupération après erreur."""
    with patch('core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper.load_config',
              return_value=test_config):
        scraper = DoctissimoScraper()

        # Simulation d'erreurs temporaires
        error_count = 0
        async def mock_get_with_errors(*args, **kwargs):
            nonlocal error_count
            if error_count < 2:  # Les 2 premières requêtes échouent
                error_count += 1
                raise aiohttp.ClientError("Test error")
            
            class MockResponse:
                async def __aenter__(self):
                    return self
                async def __aexit__(self, *args):
                    pass
                @property
                def status(self):
                    return 200
                async def text(self):
                    return "<html><body>Test content</body></html>"

            return MockResponse()

        with patch('aiohttp.ClientSession.get', side_effect=mock_get_with_errors):
            await scraper.run()

            # Vérifie que le scraper a continué malgré les erreurs
            assert scraper.metrics['errors'] == 2
            assert scraper.metrics['articles_collected'] >= 0

@pytest.mark.asyncio
async def test_data_consistency(test_config, mock_article_response):
    """Teste la cohérence des données sauvegardées."""
    with patch('core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper.load_config',
              return_value=test_config):
        scraper = DoctissimoScraper()

        # Mock d'une seule page d'article
        with patch('aiohttp.ClientSession.get',
                  new_callable=AsyncMock) as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 200
            mock_get.return_value.__aenter__.return_value.text = AsyncMock(
                return_value=mock_article_response
            )
            
            await scraper.scrape_page("https://test.com/article1")

            # Vérification en base de données
            conn = sqlite3.connect(test_config['storage']['database_path'])
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT title, content, author, source, category, url, 
                       collected_at, created_at
                FROM medical_articles 
                WHERE url = ?
            """, ("https://test.com/article1",))
            
            row = cursor.fetchone()
            assert row is not None
            
            # Vérification des champs obligatoires
            assert all(field is not None for field in row)
            
            # Vérification des formats de date
            collected_at = datetime.fromisoformat(row[6])
            created_at = datetime.fromisoformat(row[7])
            assert isinstance(collected_at, datetime)
            assert isinstance(created_at, datetime)
            
            conn.close() 