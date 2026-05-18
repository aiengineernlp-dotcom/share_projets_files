"""
Tests unitaires pour le scraper de base.
"""

import pytest
from datetime import datetime
from src.core.data_collection.base_scraper import BaseScraper

class MockBaseScraper(BaseScraper):
    """Mock du scraper de base pour les tests."""
    
    def __init__(self):
        super().__init__()
        self.platform = "test_platform"
    
    def fetch_posts(self, query, limit=10):
        """Implémentation mock de fetch_posts."""
        return [
            {
                'id': f'test_{i}',
                'title': f'Test Post {i}',
                'content': f'Test content {i}',
                'created_at': datetime.now().timestamp(),
                'platform': self.platform
            }
            for i in range(limit)
        ]

class TestBaseScraper:
    """Tests pour la classe BaseScraper."""

    @pytest.fixture
    def scraper(self):
        """Fixture pour créer une instance de test du scraper."""
        return MockBaseScraper()

    def test_initialization(self, scraper):
        """Teste l'initialisation du scraper."""
        assert scraper.platform == "test_platform"
        assert hasattr(scraper, 'fetch_posts')

    def test_fetch_posts_structure(self, scraper):
        """Teste la structure des posts récupérés."""
        posts = scraper.fetch_posts("test", limit=1)
        assert len(posts) == 1
        
        post = posts[0]
        required_fields = ['id', 'title', 'content', 'created_at', 'platform']
        for field in required_fields:
            assert field in post

    def test_fetch_posts_limit(self, scraper):
        """Teste la limite du nombre de posts récupérés."""
        limit = 5
        posts = scraper.fetch_posts("test", limit=limit)
        assert len(posts) == limit

    def test_post_validation(self, scraper):
        """Teste la validation des posts."""
        post = scraper.fetch_posts("test", limit=1)[0]
        
        # Vérifie que les champs requis sont présents
        assert isinstance(post['id'], str)
        assert isinstance(post['title'], str)
        assert isinstance(post['content'], str)
        assert isinstance(post['created_at'], float)
        assert isinstance(post['platform'], str)

    def test_error_handling(self, scraper):
        """Teste la gestion des erreurs."""
        with pytest.raises(ValueError):
            scraper.fetch_posts("", limit=0)  # Limite invalide
            
        with pytest.raises(ValueError):
            scraper.fetch_posts("", limit=-1)  # Limite négative 