"""
Tests d'intégration pour le scraper Telegram.
"""

import pytest
from unittest.mock import Mock, patch
import os
import tempfile
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta

from core.data_collection.scrapers.social_media.telegram_scraper import TelegramScraper
from core.data_collection.storage.sqlite_storage import SQLiteStorage
from core.utils.config import load_config

@pytest.fixture
def temp_db():
    """Crée une base de données temporaire pour les tests."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_telegram.db")
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
        'api': {
            'api_id': 'test_id',
            'api_hash': 'test_hash',
            'phone_number': '+33600000000',
            'session_name': 'test_session'
        },
        'scraping': {
            'max_message_age_days': 30,
            'min_message_length': 10,
            'collect_media': True,
            'batch_size': 100
        },
        'medical_channels': ['test_channel'],
        'medical_keywords': ['medical', 'health'],
        'storage': {
            'database_path': temp_db,
            'media_path': temp_media_dir,
            'backup_path': os.path.join(temp_media_dir, 'backup')
        }
    }

@pytest.fixture
def telegram_scraper(mock_config):
    with patch('core.data_collection.scrapers.social_media.telegram_scraper.load_config', return_value=mock_config):
        scraper = TelegramScraper()
        yield scraper

@pytest.fixture
def mock_messages():
    """Crée une liste de messages simulés."""
    messages = []
    for i in range(5):
        message = Mock()
        message.text = f"Test medical message {i}"
        message.date = datetime.now() - timedelta(days=i)
        message.from_user = Mock(username=f"user_{i}")
        message.chat = Mock(title="Test Medical Channel")
        message.message_id = i + 1000
        message.media = None
        messages.append(message)
    return messages

@pytest.mark.asyncio
async def test_full_scraping_workflow(telegram_scraper, mock_messages, temp_db):
    """Teste le workflow complet du scraper avec la base de données."""
    
    # Simulation de la connexion
    with patch.object(telegram_scraper, 'connect', return_value=True):
        # Simulation de la récupération des messages
        with patch.object(telegram_scraper, '_get_messages_from_channel', return_value=mock_messages):
            # Exécution du scraping
            await telegram_scraper.run()

            # Vérification des métriques
            assert telegram_scraper.metrics['items_collected'] == len(mock_messages)
            assert telegram_scraper.metrics['errors'] == 0

            # Vérification des données en base
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Vérification de la table des messages
            cursor.execute("SELECT COUNT(*) FROM telegram_messages")
            count = cursor.fetchone()[0]
            assert count == len(mock_messages)

            # Vérification du contenu
            cursor.execute("SELECT content, author, channel FROM telegram_messages LIMIT 1")
            row = cursor.fetchone()
            assert "Test medical message" in row[0]
            assert "user_" in row[1]
            assert "Test Medical Channel" == row[2]

            conn.close()

@pytest.mark.asyncio
async def test_incremental_update(telegram_scraper, mock_messages, temp_db):
    """Teste la mise à jour incrémentale des données."""
    
    # Premier scraping
    with patch.object(telegram_scraper, 'connect', return_value=True), \
         patch.object(telegram_scraper, '_get_messages_from_channel', return_value=mock_messages[:2]):
        await telegram_scraper.run()
        
        # Vérification après premier scraping
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM telegram_messages")
        first_count = cursor.fetchone()[0]
        assert first_count == 2
        conn.close()

    # Deuxième scraping avec nouveaux messages
    with patch.object(telegram_scraper, 'connect', return_value=True), \
         patch.object(telegram_scraper, '_get_messages_from_channel', return_value=mock_messages[2:]):
        await telegram_scraper.run()
        
        # Vérification après deuxième scraping
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM telegram_messages")
        second_count = cursor.fetchone()[0]
        assert second_count == len(mock_messages)
        conn.close()

def test_error_handling(telegram_scraper, mock_messages):
    """Teste la gestion des erreurs lors du scraping."""
    
    # Simulation d'une erreur de connexion
    with patch.object(telegram_scraper, 'connect', side_effect=Exception("Connection error")):
        with pytest.raises(Exception):
            telegram_scraper.run()
        assert telegram_scraper.metrics['errors'] > 0

    # Simulation d'une erreur lors de la récupération des messages
    with patch.object(telegram_scraper, 'connect', return_value=True), \
         patch.object(telegram_scraper, '_get_messages_from_channel', side_effect=Exception("API error")):
        with pytest.raises(Exception):
            telegram_scraper.run()
        assert telegram_scraper.metrics['errors'] > 0

def test_media_handling(telegram_scraper, mock_messages, temp_media_dir):
    """Teste la gestion des médias."""
    
    # Ajout d'un média à un message
    mock_messages[0].media = Mock(
        photo=True,
        document=False,
        video=False
    )
    
    with patch.object(telegram_scraper, 'connect', return_value=True), \
         patch.object(telegram_scraper, '_get_messages_from_channel', return_value=[mock_messages[0]]), \
         patch.object(telegram_scraper, '_download_media', return_value=True):
        
        telegram_scraper.run()
        
        # Vérification du téléchargement du média
        media_files = os.listdir(temp_media_dir)
        assert len(media_files) > 0 