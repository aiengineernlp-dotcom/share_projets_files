"""
Tests unitaires pour le scraper Telegram.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import os
from pathlib import Path

from core.data_collection.scrapers.social_media.telegram_scraper import TelegramScraper
from core.utils.config import load_config

@pytest.fixture
def mock_config():
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
            'collect_media': False,
            'batch_size': 100
        },
        'medical_channels': ['test_channel'],
        'medical_keywords': ['test_keyword'],
        'storage': {
            'database_path': 'test.db',
            'media_path': 'test_media',
            'backup_path': 'test_backup'
        }
    }

@pytest.fixture
def telegram_scraper(mock_config):
    with patch('core.data_collection.scrapers.social_media.telegram_scraper.load_config', return_value=mock_config):
        scraper = TelegramScraper()
        yield scraper

@pytest.fixture
def mock_message():
    message = Mock()
    message.text = "Test medical message"
    message.date = datetime.now()
    message.from_user.username = "test_user"
    message.chat.title = "Test Channel"
    message.message_id = 12345
    return message

def test_init(telegram_scraper, mock_config):
    """Teste l'initialisation du scraper."""
    assert telegram_scraper.config == mock_config
    assert telegram_scraper.source_name == "telegram"
    assert telegram_scraper.source_type == "social_media"

@patch('telethon.TelegramClient')
def test_connect(mock_client, telegram_scraper):
    """Teste la connexion à Telegram."""
    # Configuration du mock
    mock_client.return_value.start.return_value = True
    mock_client.return_value.is_user_authorized.return_value = True

    # Test de la connexion
    result = telegram_scraper.connect()
    assert result is True
    mock_client.assert_called_once()

def test_is_relevant_message(telegram_scraper, mock_message):
    """Teste la vérification de pertinence des messages."""
    # Message récent et pertinent
    assert telegram_scraper._is_relevant_message(mock_message) is True

    # Message trop ancien
    mock_message.date = datetime.now() - timedelta(days=31)
    assert telegram_scraper._is_relevant_message(mock_message) is False

    # Message trop court
    mock_message.date = datetime.now()
    mock_message.text = "Short"
    assert telegram_scraper._is_relevant_message(mock_message) is False

@patch('core.data_collection.scrapers.social_media.telegram_scraper.SQLiteStorage')
def test_save_message(mock_storage, telegram_scraper, mock_message):
    """Teste la sauvegarde des messages."""
    telegram_scraper.storage = mock_storage
    telegram_scraper._save_message(mock_message)
    mock_storage.save_message.assert_called_once()

@patch('telethon.TelegramClient')
async def test_fetch_messages(mock_client, telegram_scraper, mock_message):
    """Teste la récupération des messages."""
    # Configuration du mock
    mock_client.return_value.get_messages.return_value = [mock_message]
    mock_client.return_value.get_entity.return_value = Mock()

    # Test de la récupération
    messages = await telegram_scraper.fetch_data()
    assert len(messages) == 1
    assert messages[0]['content'] == mock_message.text

def test_process_message(telegram_scraper, mock_message):
    """Teste le traitement des messages."""
    processed = telegram_scraper._process_message(mock_message)
    assert processed['content'] == mock_message.text
    assert processed['author'] == mock_message.from_user.username
    assert processed['channel'] == mock_message.chat.title
    assert processed['message_id'] == mock_message.message_id

@pytest.mark.asyncio
async def test_run(telegram_scraper):
    """Teste l'exécution complète du scraper."""
    with patch.object(telegram_scraper, 'connect', return_value=True), \
         patch.object(telegram_scraper, 'fetch_data', return_value=[]), \
         patch.object(telegram_scraper, 'process_data', return_value=[]):
        
        await telegram_scraper.run()
        assert telegram_scraper.metrics['items_processed'] == 0
        assert telegram_scraper.metrics['errors'] == 0 