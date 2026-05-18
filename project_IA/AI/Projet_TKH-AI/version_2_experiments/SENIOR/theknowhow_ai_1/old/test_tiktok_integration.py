"""
Tests d'intégration pour le scraper TikTok.
"""

import pytest
from unittest.mock import Mock, patch
import os
import tempfile
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta

from core.phase_1_data_collection.scrapers.social_media.tiktok_scraper import TikTokScraper
from core.phase_1_data_collection.storage.sqlite_storage import SQLiteStorage
from core.utils.config import load_config

@pytest.fixture
def temp_db():
    """Crée une base de données temporaire pour les tests."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_tiktok.db")
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)
    os.rmdir(temp_dir)

@pytest.fixture
def temp_media_dir():
    """Crée un dossier temporaire pour les médias."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(temp_dir)

@pytest.fixture
def mock_config(temp_db, temp_media_dir):
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
            'database_path': temp_db,
            'media_path': temp_media_dir,
            'backup_path': os.path.join(temp_media_dir, 'backup')
        }
    }

@pytest.fixture
def tiktok_scraper(mock_config):
    with patch('core.data_collection.scrapers.social_media.tiktok_scraper.load_config', return_value=mock_config):
        scraper = TikTokScraper()
        yield scraper

@pytest.fixture
def mock_videos():
    """Crée une liste de vidéos simulées."""
    videos = []
    for i in range(5):
        video = Mock()
        video.id = f"video_{i}"
        video.desc = f"Medical information #{i} #health #doctor"
        video.create_time = int((datetime.now() - timedelta(days=i)).timestamp())
        video.author = Mock(unique_id=f"doctor_{i}")
        video.music = Mock(title=f"sound_{i}")
        video.stats = Mock(
            digg_count=1000 + i,  # likes
            comment_count=50 + i,
            share_count=20 + i,
            play_count=5000 + i
        )
        video.video_url = f"https://tiktok.com/video_{i}"
        videos.append(video)
    return videos

@pytest.mark.asyncio
async def test_full_scraping_workflow(tiktok_scraper, mock_videos, temp_db):
    """Teste le workflow complet du scraper avec la base de données."""
    
    # Simulation de la connexion
    with patch.object(tiktok_scraper, 'connect', return_value=True):
        # Simulation de la récupération des vidéos
        with patch.object(tiktok_scraper, '_get_videos_by_hashtag', return_value=mock_videos), \
             patch.object(tiktok_scraper, '_get_videos_by_user', return_value=mock_videos):
            
            # Exécution du scraping
            await tiktok_scraper.run()

            # Vérification des métriques
            assert tiktok_scraper.metrics['items_collected'] > 0
            assert tiktok_scraper.metrics['errors'] == 0

            # Vérification des données en base
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Vérification de la table des vidéos
            cursor.execute("SELECT COUNT(*) FROM tiktok_videos")
            count = cursor.fetchone()[0]
            assert count > 0

            # Vérification du contenu
            cursor.execute("""
                SELECT video_id, description, author, likes, comments 
                FROM tiktok_videos 
                LIMIT 1
            """)
            row = cursor.fetchone()
            assert "video_" in row[0]
            assert "health" in row[1]
            assert "doctor_" in row[2]
            assert row[3] >= 1000  # likes
            assert row[4] >= 50   # comments

            conn.close()

@pytest.mark.asyncio
async def test_incremental_update(tiktok_scraper, mock_videos, temp_db):
    """Teste la mise à jour incrémentale des données."""
    
    # Premier scraping avec les 2 premières vidéos
    with patch.object(tiktok_scraper, 'connect', return_value=True), \
         patch.object(tiktok_scraper, '_get_videos_by_hashtag', return_value=mock_videos[:2]), \
         patch.object(tiktok_scraper, '_get_videos_by_user', return_value=mock_videos[:2]):
        
        await tiktok_scraper.run()
        
        # Vérification après premier scraping
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tiktok_videos")
        first_count = cursor.fetchone()[0]
        assert first_count == 2
        conn.close()

    # Deuxième scraping avec les vidéos restantes
    with patch.object(tiktok_scraper, 'connect', return_value=True), \
         patch.object(tiktok_scraper, '_get_videos_by_hashtag', return_value=mock_videos[2:]), \
         patch.object(tiktok_scraper, '_get_videos_by_user', return_value=mock_videos[2:]):
        
        await tiktok_scraper.run()
        
        # Vérification après deuxième scraping
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tiktok_videos")
        second_count = cursor.fetchone()[0]
        assert second_count == len(mock_videos)
        conn.close()

def test_error_handling(tiktok_scraper):
    """Teste la gestion des erreurs lors du scraping."""
    
    # Simulation d'une erreur de connexion
    with patch.object(tiktok_scraper, 'connect', side_effect=Exception("Connection error")):
        with pytest.raises(Exception):
            tiktok_scraper.run()
        assert tiktok_scraper.metrics['errors'] > 0

    # Simulation d'une erreur lors de la récupération des vidéos
    with patch.object(tiktok_scraper, 'connect', return_value=True), \
         patch.object(tiktok_scraper, '_get_videos_by_hashtag', side_effect=Exception("API error")):
        with pytest.raises(Exception):
            tiktok_scraper.run()
        assert tiktok_scraper.metrics['errors'] > 0

@pytest.mark.asyncio
async def test_video_download(tiktok_scraper, mock_videos, temp_media_dir):
    """Teste le téléchargement des vidéos."""
    video = mock_videos[0]
    
    with patch('requests.get') as mock_get:
        # Simulation d'un fichier vidéo
        mock_get.return_value.content = b"fake_video_content"
        mock_get.return_value.status_code = 200
        
        # Test du téléchargement
        result = await tiktok_scraper._download_video(video)
        assert result is True
        
        # Vérification du fichier
        video_files = os.listdir(temp_media_dir)
        assert len(video_files) > 0

def test_hashtag_filtering(tiktok_scraper, mock_videos):
    """Teste le filtrage des vidéos par hashtag."""
    # Ajout de hashtags médicaux aux vidéos
    mock_videos[0].desc = "#health #doctor Medical video"
    mock_videos[1].desc = "#fitness #workout Exercise video"
    
    filtered_videos = [
        video for video in mock_videos 
        if tiktok_scraper._has_medical_hashtags(video.desc)
    ]
    
    assert len(filtered_videos) == 1
    assert "#health" in filtered_videos[0].desc 