"""
Tests unitaires pour le scraper TikTok.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import os
from pathlib import Path

from core.data_collection.scrapers.social_media.tiktok_scraper import TikTokScraper
from core.utils.config import load_config

@pytest.fixture
def mock_config():
    return {
        'auth': {
            'session_id': 'test_session',
            'user_agent': 'test_agent'
        },
        'scraping': {
            'max_video_age_days': 30,
            'min_likes': 100,
            'min_comments': 10,
            'collect_comments': True,
            'max_videos_per_hashtag': 500
        },
        'medical_hashtags': ['medecine', 'health'],
        'medical_accounts': ['doctorsoftiktok'],
        'storage': {
            'database_path': 'test.db',
            'media_path': 'test_media',
            'backup_path': 'test_backup'
        }
    }

@pytest.fixture
def tiktok_scraper(mock_config):
    with patch('core.data_collection.scrapers.social_media.tiktok_scraper.load_config', return_value=mock_config):
        scraper = TikTokScraper()
        yield scraper

@pytest.fixture
def mock_video():
    video = Mock()
    video.id = "test_video_id"
    video.desc = "Medical information #health"
    video.create_time = int(datetime.now().timestamp())
    video.author = Mock(unique_id="test_user")
    video.stats = Mock(
        digg_count=1000,  # likes
        comment_count=50,
        share_count=20,
        play_count=5000
    )
    return video

def test_init(tiktok_scraper, mock_config):
    """Teste l'initialisation du scraper."""
    assert tiktok_scraper.config == mock_config
    assert tiktok_scraper.source_name == "tiktok"
    assert tiktok_scraper.source_type == "social_media"

@patch('TikTokApi.TikTokApi')
def test_connect(mock_api, tiktok_scraper):
    """Teste la connexion à TikTok."""
    mock_api.return_value.get_instance.return_value = True
    
    result = tiktok_scraper.connect()
    assert result is True
    mock_api.assert_called_once()

def test_is_relevant_video(tiktok_scraper, mock_video):
    """Teste la vérification de pertinence des vidéos."""
    # Vidéo pertinente
    assert tiktok_scraper._is_relevant_video(mock_video) is True

    # Vidéo trop ancienne
    mock_video.create_time = int((datetime.now() - timedelta(days=31)).timestamp())
    assert tiktok_scraper._is_relevant_video(mock_video) is False

    # Pas assez de likes
    mock_video.create_time = int(datetime.now().timestamp())
    mock_video.stats.digg_count = 50
    assert tiktok_scraper._is_relevant_video(mock_video) is False

@patch('core.data_collection.scrapers.social_media.tiktok_scraper.SQLiteStorage')
def test_save_video(mock_storage, tiktok_scraper, mock_video):
    """Teste la sauvegarde des vidéos."""
    tiktok_scraper.storage = mock_storage
    tiktok_scraper._save_video(mock_video)
    mock_storage.save_video.assert_called_once()

@patch('TikTokApi.TikTokApi')
async def test_fetch_videos(mock_api, tiktok_scraper, mock_video):
    """Teste la récupération des vidéos."""
    mock_api.return_value.hashtag.videos.return_value = [mock_video]
    mock_api.return_value.user.videos.return_value = [mock_video]

    videos = await tiktok_scraper.fetch_data()
    assert len(videos) > 0
    assert videos[0]['video_id'] == mock_video.id

def test_process_video(tiktok_scraper, mock_video):
    """Teste le traitement des vidéos."""
    processed = tiktok_scraper._process_video(mock_video)
    assert processed['video_id'] == mock_video.id
    assert processed['description'] == mock_video.desc
    assert processed['author'] == mock_video.author.unique_id
    assert processed['likes'] == mock_video.stats.digg_count

@pytest.mark.asyncio
async def test_run(tiktok_scraper):
    """Teste l'exécution complète du scraper."""
    with patch.object(tiktok_scraper, 'connect', return_value=True), \
         patch.object(tiktok_scraper, 'fetch_data', return_value=[]), \
         patch.object(tiktok_scraper, 'process_data', return_value=[]):
        
        await tiktok_scraper.run()
        assert tiktok_scraper.metrics['items_processed'] == 0
        assert tiktok_scraper.metrics['errors'] == 0

def test_download_video(tiktok_scraper, mock_video):
    """Teste le téléchargement des vidéos."""
    with patch('core.data_collection.scrapers.social_media.tiktok_scraper.requests.get') as mock_get:
        mock_get.return_value.content = b"fake_video_content"
        
        result = tiktok_scraper._download_video(mock_video)
        assert result is True
        assert mock_get.called 