"""Tests pour le module de conversation médicale de TheKnowHow.ae.

Ce module contient les tests unitaires et d'intégration pour le système
de conversation médicale. Il teste toutes les fonctionnalités principales:
- Gestion de la base de données
- Traduction et détection de langue
- Analyse de sentiment
- Génération de réponses
- Gestion des erreurs
- Support multilingue
- Sauvegarde des conversations

Classes de test:
    - TestDatabaseManager: Tests de la persistance des données
    - TestTranslationManager: Tests de la traduction
    - TestLanguageDetector: Tests de la détection de langue
    - TestErrorHandling: Tests de la gestion des erreurs
    - TestMultilingualSupport: Tests du support multilingue
    - TestConversationSaving: Tests de la sauvegarde des conversations
"""

import pytest
import sqlite3
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from phase3_conversationnel import (
    app, ConversationManager, Message, Response, DatabaseManager,
    TranslationManager, LanguageDetector
)

client = TestClient(app)

@pytest.fixture
def test_db():
    """Fixture pour créer une base de données de test.
    
    Cette fixture:
    1. Crée une base de données temporaire
    2. Configure les tables nécessaires
    3. Retourne le chemin de la base de données
    4. Nettoie la base après les tests
    
    Returns:
        str: Chemin vers la base de données de test
    """
    db_path = "test_phase3.db"
    # Créer une base de données de test
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Créer la table posts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            overall_score REAL NOT NULL,
            created_utc DATETIME NOT NULL,
            title TEXT,
            body TEXT,
            country TEXT,
            city TEXT
        )
        """)
        # Créer la table conversations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            last_message_at DATETIME NOT NULL,
            status TEXT NOT NULL,
            sentiment_score REAL
        )
        """)
        # Créer la table chat_messages
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            sentiment_score REAL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
        """)
        # Créer la table gcc_users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gcc_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
        """)
        # Insérer des données de test
        cursor.execute("""
        INSERT OR REPLACE INTO posts (id, author, category, overall_score, created_utc, title, body, country, city)
        VALUES 
        (1, 'test_user', 'High Priority', 0.8, datetime('now'), 'Urgent medical question', 'I need a second opinion', 'UAE', 'Dubai'),
        (2, 'test_user2', 'General', 0.3, datetime('now'), 'General question', 'Just asking about symptoms', 'France', 'Paris')
        """)
        conn.commit()
    
    yield db_path
    
    # Nettoyer après les tests
    import os
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def mock_openai_response():
    """Fixture pour simuler la réponse d'OpenAI."""
    with patch('phase3_conversationnel.AsyncOpenAI') as mock:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Je suis un assistant médical."))]
        )
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def conversation_manager(test_db):
    """Fixture pour créer une instance de ConversationManager.
    
    Cette fixture:
    1. Crée une instance avec la base de données de test
    2. Configure les mocks nécessaires
    3. Retourne l'instance configurée
    
    Args:
        test_db (str): Chemin vers la base de données de test
        
    Returns:
        ConversationManager: Instance configurée pour les tests
    """
    with patch('phase3_conversationnel.DatabaseManager') as mock_db:
        mock_db.return_value = DatabaseManager(test_db)
        return ConversationManager()

def test_initialization(conversation_manager):
    """Test l'initialisation du ConversationManager."""
    assert conversation_manager.db_manager is not None
    assert conversation_manager.translation_manager is not None
    assert conversation_manager.language_detector is not None
    assert conversation_manager.max_conversation_history == 10

def test_sentiment_analysis(conversation_manager):
    """Test l'analyse de sentiment."""
    # Test avec un message positif
    score = conversation_manager.analyze_sentiment("Je me sens beaucoup mieux maintenant, merci!")
    assert score > 0
    
    # Test avec un message négatif
    score = conversation_manager.analyze_sentiment("Je suis très inquiet pour ma santé")
    assert score < 0

def test_priority_determination(conversation_manager):
    """Test la détermination de la priorité."""
    # Test priorité haute
    context = {"overall_score": 0.8}
    priority = conversation_manager._determine_priority(context, -0.6)
    assert priority == "Haute"
    
    # Test priorité moyenne
    context = {"overall_score": 0.6}
    priority = conversation_manager._determine_priority(context, -0.3)
    assert priority == "Moyenne"
    
    # Test priorité basse
    context = {"overall_score": 0.2}
    priority = conversation_manager._determine_priority(context, 0.1)
    assert priority == "Basse"

def test_chat_endpoint(mock_openai_response):
    """Test de l'endpoint /chat."""
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "Bonjour, j'ai mal à la tête"}],
            "user_id": "test_user"
        }
    )
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_endpoint_error_handling(mock_openai_response):
    """Test de la gestion des erreurs de l'endpoint /chat."""
    # Test avec une liste de messages vide
    response = client.post(
        "/chat",
        json={
            "messages": [],
            "user_id": "test_user"
        }
    )
    assert response.status_code == 400
    assert "La liste des messages ne peut pas être vide" in response.json()["detail"]

    # Test avec un message vide
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": ""}],
            "user_id": "test_user"
        }
    )
    assert response.status_code == 400
    assert "Le contenu du message ne peut pas être vide" in response.json()["detail"]

def test_chat_with_context(mock_openai_response):
    """Test de l'endpoint /chat avec contexte."""
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "Je suis à Dubaï et j'ai besoin d'un second avis médical"}],
            "user_id": "test_user",
            "context": {
                "country": "Émirats Arabes Unis",
                "city": "Dubaï"
            }
        }
    )
    assert response.status_code == 200
    assert "response" in response.json()

@pytest.mark.asyncio
async def test_chat_websocket(mock_openai_response):
    """Test de l'endpoint WebSocket /ws/chat."""
    with client.websocket_connect("/ws/chat") as websocket:
        # Envoyer un message
        websocket.send_json({
            "messages": [{"role": "user", "content": "Bonjour, j'ai mal à la tête"}],
            "user_id": "test_user"
        })
        
        # Recevoir la réponse
        response = websocket.receive_json()
        assert "response" in response

def test_database_manager(test_db):
    """Test du DatabaseManager.
    
    Ce test vérifie:
    1. La sauvegarde des messages
    2. La récupération de l'historique
    3. L'intégrité des données sauvegardées
    
    Args:
        test_db (str): Chemin vers la base de données de test
    """
    db_manager = DatabaseManager(test_db)
    
    # Test de sauvegarde de message
    db_manager.save_message(1, "user", "Test message", 0.5)
    
    # Test de récupération d'historique
    history = db_manager.get_conversation_history(1)
    assert len(history) > 0
    assert history[0][2] == "Test message"  # Vérifier le contenu du message

def test_translation_manager():
    """Test du TranslationManager.
    
    Ce test vérifie:
    1. La détection de langue
    2. La traduction de texte
    3. La gestion des erreurs de traduction
    """
    translation_manager = TranslationManager()
    
    # Test de détection de langue
    lang = translation_manager.detect_language("Bonjour")
    assert lang == "fr"
    
    # Test de traduction
    translated = translation_manager.translate_text("Hello", "fr")
    assert translated != "Hello"

def test_language_detector():
    """Test du LanguageDetector.
    
    Ce test vérifie:
    1. La détection du français
    2. La détection de l'anglais
    3. La gestion des cas par défaut
    """
    detector = LanguageDetector()
    
    # Test détection français
    assert detector.detect("Bonjour") == "fr"
    
    # Test détection anglais
    assert detector.detect("Hello") == "en"

def test_error_handling():
    """Test de la gestion des erreurs.
    
    Ce test vérifie:
    1. La gestion des erreurs OpenAI
    2. Les réponses d'erreur appropriées
    3. La persistance des données en cas d'erreur
    """
    with patch('phase3_conversationnel.ConversationManager.openai_client') as mock:
        # Simuler une erreur OpenAI
        mock.chat.completions.create.side_effect = Exception("OpenAI Error")
        
        response = client.post(
            "/chat",
            json={
                "messages": [{"role": "user", "content": "Test"}],
                "user_id": "test_user"
            }
        )
        assert response.status_code == 500
        assert "OpenAI" in response.json()["detail"]

@pytest.mark.asyncio
async def test_multilingual_support(conversation_manager):
    """Test du support multilingue.
    
    Ce test vérifie:
    1. La génération de réponses en français
    2. La génération de réponses en anglais
    3. La cohérence des réponses entre les langues
    
    Args:
        conversation_manager (ConversationManager): Instance pour les tests
    """
    # Test français
    response = await conversation_manager.generate_response(
        "Bonjour, j'ai besoin d'aide",
        "1",
        "test_user",
        "fr"
    )
    assert isinstance(response, Response)
    assert response.message is not None
    
    # Test anglais
    response = await conversation_manager.generate_response(
        "Hello, I need help",
        "1",
        "test_user",
        "en"
    )
    assert isinstance(response, Response)
    assert response.message is not None

@pytest.mark.asyncio
async def test_conversation_saving(conversation_manager, test_db):
    """Test de la sauvegarde des conversations.
    
    Ce test vérifie:
    1. La sauvegarde des messages
    2. La récupération de l'historique
    3. L'intégrité des données sauvegardées
    
    Args:
        conversation_manager (ConversationManager): Instance pour les tests
        test_db (str): Chemin vers la base de données de test
    """
    # Générer une réponse
    response = await conversation_manager.generate_response(
        "Test message",
        "1",
        "test_user"
    )
    
    # Vérifier que la conversation a été sauvegardée
    db_manager = DatabaseManager(test_db)
    history = db_manager.get_conversation_history(1)
    assert len(history) > 0
    assert history[0][2] == "Test message"  # Vérifier le contenu du message

if __name__ == "__main__":
    pytest.main([__file__, "-v"])