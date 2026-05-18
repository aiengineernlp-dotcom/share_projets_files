"""
Tests unitaires pour le scraper Twitter.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.twitter.scraper import TwitterScraper

@pytest.fixture
def mock_twitter_api():
    """Fixture pour mocker l'API Twitter."""
    with patch('src.twitter.scraper.tweepy.Client') as mock_client:
        mock_tweets = [
            MagicMock(
                id=f'tweet_{i}',
                text=f'Tweet content {i}',
                created_at=datetime.now(),
                author_id=f'user_{i}'
            ) for i in range(5)
        ]
        mock_client.return_value.search_recent_tweets.return_value = MagicMock(data=mock_tweets)
        yield mock_client

@pytest.fixture
def scraper(mock_twitter_api):
    """Fixture pour créer une instance de test du scraper Twitter."""
    return TwitterScraper(
        bearer_token="test_token",
        api_key="test_key",
        api_secret="test_secret"
    )

class TestTwitterScraper:
    """Tests pour la classe TwitterScraper."""

    def test_initialization(self, scraper):
        """Teste l'initialisation du scraper."""
        assert scraper.platform == "twitter"
        assert scraper.bearer_token == "test_token"
        assert scraper.api_key == "test_key"
        assert scraper.api_secret == "test_secret"

    def test_fetch_posts(self, scraper, mock_twitter_api):
        """Teste la récupération des posts."""
        posts = scraper.fetch_posts("test query", limit=5)
        
        assert len(posts) == 5
        for post in posts:
            assert isinstance(post['id'], str)
            assert isinstance(post['content'], str)
            assert isinstance(post['created_at'], float)
            assert post['platform'] == 'twitter'

    def test_post_processing(self, scraper, mock_twitter_api):
        """Teste le traitement des posts récupérés."""
        posts = scraper.fetch_posts("test query", limit=1)
        post = posts[0]
        
        # Vérifie la structure du post
        required_fields = ['id', 'content', 'created_at', 'platform', 'author_id']
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
            TwitterScraper(bearer_token="", api_key="", api_secret="")

    def test_rate_limiting(self, scraper, mock_twitter_api):
        """Teste la gestion des limites de taux."""
        # Simule une erreur de limite de taux
        mock_twitter_api.return_value.search_recent_tweets.side_effect = Exception("Rate limit exceeded")
        
        with pytest.raises(Exception) as exc_info:
            scraper.fetch_posts("test", limit=10)
        assert "Rate limit exceeded" in str(exc_info.value)

    def test_tweet_parsing(self, scraper, mock_twitter_api):
        """Teste l'analyse des tweets."""
        # Test avec un tweet contenant des mentions et des hashtags
        mock_tweet = MagicMock(
            id='tweet_special',
            text='Test #medical tweet with @mention',
            created_at=datetime.now(),
            author_id='user_special'
        )
        mock_twitter_api.return_value.search_recent_tweets.return_value = MagicMock(data=[mock_tweet])
        
        posts = scraper.fetch_posts("test", limit=1)
        assert len(posts) == 1
        assert '#medical' in posts[0]['content']
        assert '@mention' in posts[0]['content'] 