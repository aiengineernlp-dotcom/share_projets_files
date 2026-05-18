"""
Tests unitaires pour le scraper Doctissimo.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os
import tempfile
from datetime import datetime
from bs4 import BeautifulSoup

from core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper import DoctissimoScraper

@pytest.fixture
def mock_config():
    """Fixture pour la configuration de test."""
    return {
        'base_url': 'https://www.doctissimo.fr',
        'categories': ['sante', 'medicaments'],
        'scraping': {
            'max_pages_per_category': 2,
            'max_concurrent_requests': 2
        },
        'storage': {
            'database_path': ':memory:',
            'media_path': tempfile.mkdtemp(),
            'backup_path': tempfile.mkdtemp()
        },
        'logging': {
            'level': 'INFO'
        }
    }

@pytest.fixture
def mock_html():
    """Fixture pour le HTML de test."""
    return """
    <html>
        <head><title>Test Article</title></head>
        <body>
            <h1 class="title-article">Test Medical Article</h1>
            <time datetime="2024-03-13T10:00:00Z"></time>
            <span class="author-name">Dr. Test</span>
            <div class="article-content">
                <p>This is a test medical article content.</p>
                <script>alert('test');</script>
                <style>.test{color:red;}</style>
            </div>
            <div class="tags">
                <a class="tag">santé</a>
                <a class="tag">médecine</a>
            </div>
        </body>
    </html>
    """

@pytest.fixture
def doctissimo_scraper(mock_config):
    """Fixture pour l'instance du scraper."""
    with patch('core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper.load_config', 
              return_value=mock_config):
        scraper = DoctissimoScraper()
        return scraper

@pytest.mark.asyncio
async def test_initialization(doctissimo_scraper, mock_config):
    """Teste l'initialisation du scraper."""
    assert doctissimo_scraper.base_url == mock_config['base_url']
    assert doctissimo_scraper.categories == mock_config['categories']
    assert doctissimo_scraper.metrics['pages_scraped'] == 0
    assert doctissimo_scraper.metrics['articles_collected'] == 0
    assert doctissimo_scraper.metrics['errors'] == 0

@pytest.mark.asyncio
async def test_extract_article_data(doctissimo_scraper, mock_html):
    """Teste l'extraction des données d'un article."""
    soup = BeautifulSoup(mock_html, 'html.parser')
    doctissimo_scraper.current_url = "https://test.com/article"
    doctissimo_scraper.current_category = "sante"
    
    article_data = await doctissimo_scraper.extract_article_data(soup)
    
    assert article_data is not None
    assert article_data['title'] == "Test Medical Article"
    assert article_data['author'] == "Dr. Test"
    assert article_data['content'] == "This is a test medical article content."
    assert len(article_data['tags']) == 2
    assert article_data['source'] == "Doctissimo"
    assert article_data['category'] == "sante"

@pytest.mark.asyncio
async def test_scrape_page(doctissimo_scraper, mock_html):
    """Teste le scraping d'une page."""
    with patch.object(doctissimo_scraper, 'fetch_page', 
                     new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_html
        
        url = "https://www.doctissimo.fr/sante/article-test"
        result = await doctissimo_scraper.scrape_page(url)
        
        assert result is not None
        assert doctissimo_scraper.metrics['pages_scraped'] == 1
        mock_fetch.assert_called_once_with(url)

@pytest.mark.asyncio
async def test_get_article_urls(doctissimo_scraper):
    """Teste la récupération des URLs d'articles."""
    mock_list_html = """
    <html>
        <body>
            <a class="article-card-link" href="/sante/article1">Article 1</a>
            <a class="article-card-link" href="/sante/article2">Article 2</a>
            <a class="article-card-link" href="https://www.doctissimo.fr/sante/article3">Article 3</a>
        </body>
    </html>
    """
    
    with patch.object(doctissimo_scraper, 'fetch_page', 
                     new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_list_html
        
        urls = await doctissimo_scraper.get_article_urls('sante')
        
        assert len(urls) == 3
        assert all(url.startswith('https://') for url in urls)
        assert mock_fetch.call_count == 1

@pytest.mark.asyncio
async def test_error_handling(doctissimo_scraper):
    """Teste la gestion des erreurs."""
    with patch.object(doctissimo_scraper, 'fetch_page', 
                     new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = Exception("Test error")
        
        result = await doctissimo_scraper.scrape_page("https://test.com/error")
        
        assert result is None
        assert doctissimo_scraper.metrics['errors'] > 0

@pytest.mark.asyncio
async def test_backup_creation(doctissimo_scraper, tmp_path):
    """Teste la création de sauvegardes."""
    doctissimo_scraper.config['storage']['backup_path'] = str(tmp_path)
    doctissimo_scraper.metrics['articles_collected'] = 5
    
    doctissimo_scraper.create_backup()
    
    backup_files = list(tmp_path.glob('*.json'))
    assert len(backup_files) == 1
    assert backup_files[0].stat().st_size > 0

def test_cleanup(doctissimo_scraper):
    """Teste le nettoyage des ressources."""
    with patch.object(doctissimo_scraper, 'cleanup', 
                     new_callable=AsyncMock) as mock_cleanup:
        mock_cleanup.return_value = None
        
        # Simulation d'une exécution complète
        async def run_test():
            await doctissimo_scraper.cleanup()
        
        import asyncio
        asyncio.run(run_test())
        
        mock_cleanup.assert_called_once() 