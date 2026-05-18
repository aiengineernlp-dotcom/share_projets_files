"""
Tests unitaires pour le scraper YouTube.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import os
from pathlib import Path

from core.data_collection.scrapers.social_media.youtube_scraper import YouTubeScraper
from core.utils.config import load_config

@pytest.fixture
def mock_config():
    return {
        'api': {
            'api_key': 'test_key',
            'application_name': 'Medical Content Collector'
        },
        'scraping': {
            'max_video_age_days': 30,
            'min_views': 1000,
            'min_likes': 50,
            'collect_comments': True,
            'max_comments_per_video': 100,
            'language_filter': ['fr', 'en']
        },
        'medical_channels': [
            'UCZgwcpRFCLxWg9iOPXNu-Dg',
            'UC7sXGI8p8PvKosLWagkK9wQ'
        ],
        'search_keywords': ['medical education', 'healthcare'],
        'storage': {
            'database_path': 'test.db',
            'media_path': 'test_media',
            'backup_path': 'test_backup'
        }
    }

@pytest.fixture
def youtube_scraper(mock_config):
    with patch('core.data_collection.scrapers.social_media.youtube_scraper.load_config', return_value=mock_config):
        scraper = YouTubeScraper()
        yield scraper

@pytest.fixture
def mock_video():
    video = Mock()
    video.id = {'videoId': 'test_video_id'}
    video.snippet = Mock(
        title='Medical Education Video',
        description='Healthcare information',
        publishedAt='2024-03-13T10:00:00Z',
        channelId='UCZgwcpRFCLxWg9iOPXNu-Dg',
        channelTitle='Medical Channel'
    )
    video.statistics = Mock(
        viewCount='5000',
        likeCount='200',
        commentCount='50'
    )
    return video

def test_init(youtube_scraper, mock_config):
    """Teste l'initialisation du scraper."""
    assert youtube_scraper.config == mock_config
    assert youtube_scraper.source_name == "youtube"
    assert youtube_scraper.source_type == "social_media"

@patch('googleapiclient.discovery.build')
def test_connect(mock_build, youtube_scraper):
    """Teste la connexion à l'API YouTube."""
    mock_build.return_value = Mock()
    
    result = youtube_scraper.connect()
    assert result is True
    mock_build.assert_called_once_with(
        'youtube', 'v3',
        developerKey=youtube_scraper.config['api']['api_key']
    )

def test_is_relevant_video(youtube_scraper, mock_video):
    """Teste la vérification de pertinence des vidéos."""
    # Vidéo pertinente
    assert youtube_scraper._is_relevant_video(mock_video) is True

    # Vidéo trop ancienne
    mock_video.snippet.publishedAt = (datetime.now() - timedelta(days=31)).isoformat() + 'Z'
    assert youtube_scraper._is_relevant_video(mock_video) is False

    # Pas assez de vues
    mock_video.snippet.publishedAt = datetime.now().isoformat() + 'Z'
    mock_video.statistics.viewCount = '500'
    assert youtube_scraper._is_relevant_video(mock_video) is False

@patch('core.data_collection.scrapers.social_media.youtube_scraper.SQLiteStorage')
def test_save_video(mock_storage, youtube_scraper, mock_video):
    """Teste la sauvegarde des vidéos."""
    youtube_scraper.storage = mock_storage
    youtube_scraper._save_video(mock_video)
    mock_storage.save_video.assert_called_once()

@patch('googleapiclient.discovery.build')
async def test_fetch_videos(mock_build, youtube_scraper, mock_video):
    """Teste la récupération des vidéos."""
    mock_service = Mock()
    mock_service.search.return_value.list.return_value.execute.return_value = {
        'items': [mock_video]
    }
    mock_build.return_value = mock_service

    videos = await youtube_scraper.fetch_data()
    assert len(videos) > 0
    assert videos[0]['video_id'] == mock_video.id['videoId']

def test_process_video(youtube_scraper, mock_video):
    """Teste le traitement des vidéos."""
    processed = youtube_scraper._process_video(mock_video)
    assert processed['video_id'] == mock_video.id['videoId']
    assert processed['title'] == mock_video.snippet.title
    assert processed['channel_id'] == mock_video.snippet.channelId
    assert processed['views'] == int(mock_video.statistics.viewCount)

@pytest.mark.asyncio
async def test_run(youtube_scraper):
    """Teste l'exécution complète du scraper."""
    with patch.object(youtube_scraper, 'connect', return_value=True), \
         patch.object(youtube_scraper, 'fetch_data', return_value=[]), \
         patch.object(youtube_scraper, 'process_data', return_value=[]):
        
        await youtube_scraper.run()
        assert youtube_scraper.metrics['items_processed'] == 0
        assert youtube_scraper.metrics['errors'] == 0

@patch('pytube.YouTube')
def test_download_video(mock_youtube, youtube_scraper, mock_video):
    """Teste le téléchargement des vidéos."""
    mock_stream = Mock()
    mock_stream.download.return_value = "test_path.mp4"
    mock_youtube.return_value.streams.get_highest_resolution.return_value = mock_stream
    
    result = youtube_scraper._download_video(mock_video.id['videoId'])
    assert result == "test_path.mp4"
    mock_youtube.assert_called_once()

def test_get_video_comments(youtube_scraper, mock_video):
    """Teste la récupération des commentaires."""
    mock_service = Mock()
    mock_comment = Mock(
        snippet=Mock(
            topLevelComment=Mock(
                snippet=Mock(
                    textDisplay="Test comment",
                    authorDisplayName="Test User",
                    publishedAt="2024-03-13T10:00:00Z",
                    likeCount=10
                )
            )
        )
    )
    mock_service.commentThreads.return_value.list.return_value.execute.return_value = {
        'items': [mock_comment]
    }
    youtube_scraper.youtube = mock_service

    comments = youtube_scraper._get_video_comments(mock_video.id['videoId'])
    assert len(comments) > 0
    assert comments[0]['text'] == "Test comment" 