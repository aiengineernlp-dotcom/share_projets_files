"""
Tests unitaires pour le scraper Facebook.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.facebook.scraper import FacebookScraper

@pytest.fixture
def mock_facebook_api():
    """Fixture pour mocker l'API Facebook."""
    with patch('src.facebook.scraper.facebook_sdk.GraphAPI') as mock_api:
        mock_posts = [
            {
                'id': f'post_{i}',
                'message': f'Facebook post content {i}',
                'created_time': datetime.now().isoformat(),
                'from': {'id': f'user_{i}', 'name': f'User {i}'}
            } for i in range(5)
        ]
        mock_api.return_value.get_connections.return_value = {'data': mock_posts}
        yield mock_api

@pytest.fixture
def scraper(mock_facebook_api):
    """Fixture pour créer une instance de test du scraper Facebook."""
    return FacebookScraper(
        access_token="test_token",
        app_id="test_app_id",
        app_secret="test_secret"
    )

class TestFacebookScraper:
    """Tests pour la classe FacebookScraper."""

    def test_initialization(self, scraper):
        """Teste l'initialisation du scraper."""
        assert scraper.platform == "facebook"
        assert scraper.access_token == "test_token"
        assert scraper.app_id == "test_app_id"
        assert scraper.app_secret == "test_secret"

    def test_fetch_posts(self, scraper, mock_facebook_api):
        """Teste la récupération des posts."""
        posts = scraper.fetch_posts("test query", limit=5)
        
        assert len(posts) == 5
        for post in posts:
            assert isinstance(post['id'], str)
            assert isinstance(post['content'], str)
            assert isinstance(post['created_at'], float)
            assert post['platform'] == 'facebook'

    def test_post_processing(self, scraper, mock_facebook_api):
        """Teste le traitement des posts récupérés."""
        posts = scraper.fetch_posts("test query", limit=1)
        post = posts[0]
        
        # Vérifie la structure du post
        required_fields = ['id', 'content', 'created_at', 'platform', 'author_id', 'author_name']
        for field in required_fields:
            assert field in post

    def test_error_handling(self, scraper):
        """Teste la gestion des erreurs."""
        # Test avec une requête vide
        with pytest.raises(ValueError):
            scraper.fetch_posts("", limit=10)
        
        # Test avec une limite invalide
        with pytest.raises(ValueError):
            scraper.fetch_posts("test", limit=0)
        
        # Test avec des identifiants invalides
        with pytest.raises(ValueError):
            FacebookScraper(access_token="", app_id="", app_secret="")

    def test_rate_limiting(self, scraper, mock_facebook_api):
        """Teste la gestion des limites de taux."""
        # Simule une erreur de limite de taux
        mock_facebook_api.return_value.get_connections.side_effect = Exception("API calls quota exceeded")
        
        with pytest.raises(Exception) as exc_info:
            scraper.fetch_posts("test", limit=10)
        assert "API calls quota exceeded" in str(exc_info.value)

    def test_post_types(self, scraper, mock_facebook_api):
        """Teste le traitement de différents types de posts."""
        # Test avec différents types de posts Facebook
        mock_posts = [
            {
                'id': 'post_1',
                'message': 'Regular post',
                'created_time': datetime.now().isoformat(),
                'from': {'id': 'user_1', 'name': 'User 1'}
            },
            {
                'id': 'post_2',
                'message': 'Post with link',
                'link': 'https://example.com',
                'created_time': datetime.now().isoformat(),
                'from': {'id': 'user_2', 'name': 'User 2'}
            },
            {
                'id': 'post_3',
                'message': 'Post with image',
                'picture': 'image_url',
                'created_time': datetime.now().isoformat(),
                'from': {'id': 'user_3', 'name': 'User 3'}
            }
        ]
        
        mock_facebook_api.return_value.get_connections.return_value = {'data': mock_posts}
        posts = scraper.fetch_posts("test", limit=3)
        
        assert len(posts) == 3
        # Vérifie que chaque type de post est correctement traité
        for post in posts:
            assert 'content' in post
            assert 'created_at' in post
            assert 'author_id' in post 