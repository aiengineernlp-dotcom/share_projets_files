"""Tests unitaires pour le module de gestion des conversations."""

import pytest
import sqlite3
import os
from unittest.mock import MagicMock, patch
from phase3_conversationnel import DatabaseManager, TranslationManager, Message, Conversation, Response

@pytest.fixture
def db_manager():
    """Fixture pour le gestionnaire de base de données"""
    # Utiliser une base de données temporaire
    db_path = "test_temp.db"
    
    # Supprimer la base de données si elle existe déjà
    if os.path.exists(db_path):
        os.remove(db_path)
    
    manager = DatabaseManager(db_path)
    
    yield manager
    
    # Nettoyer la base de données temporaire
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def translation_manager():
    """Fixture pour créer une instance de TranslationManager."""
    return TranslationManager()

def test_database_initialization(db_manager):
    """Test l'initialisation de la base de données"""
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        assert "conversations" in table_names
        assert "chat_messages" in table_names
        assert "gcc_users" in table_names
        assert "posts" in table_names

def test_save_and_get_message(db_manager):
    """Test la sauvegarde et la récupération des messages"""
    # Créer une conversation
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (user_id, created_at, last_message_at, status) VALUES (?, datetime('now'), datetime('now'), 'active')",
            ("test_user",)
        )
        conversation_id = cursor.lastrowid
        conn.commit()
    
    # Sauvegarder un message
    db_manager.save_message(conversation_id, "user", "Test message")
    
    # Récupérer l'historique
    history = db_manager.get_conversation_history(conversation_id)
    assert len(history) == 1
    assert history[0][1] == "user"  # Le rôle est le deuxième élément du tuple
    assert history[0][2] == "Test message"  # Le contenu est le troisième élément

def test_get_user_context(db_manager):
    """Test la récupération du contexte utilisateur"""
    # Insérer les données de test
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (id, author, category, overall_score, created_utc) VALUES (?, ?, ?, ?, ?)",
            (1, "test_user", "Urgent", 0.8, 1234567890)
        )
        cursor.execute(
            "INSERT INTO gcc_users (post_id, country, city) VALUES (?, ?, ?)",
            (1, "UAE", "Dubai")
        )
        conn.commit()
    
    # Récupérer le contexte
    context = db_manager.get_user_context("test_user")
    assert context["country"] == "UAE"
    assert context["city"] == "Dubai"
    assert context["category"] == "Urgent"
    assert context["score"] == 0.8

@patch('deep_translator.GoogleTranslator.translate')
def test_translation_manager(mock_translate, translation_manager):
    """Test le gestionnaire de traduction"""
    # Configurer le mock pour retourner une traduction différente
    mock_translate.return_value = "Hello"
    
    # Test avec un texte simple
    text = "Bonjour"
    translated = translation_manager.translate_text(text, "en")
    assert translated == "Hello"  # Vérifie que la traduction a été effectuée
    
    # Vérifier que le mock a été appelé
    mock_translate.assert_called_once()
    
    # Test avec le même traducteur (devrait utiliser le cache)
    translator1 = translation_manager.get_translator("en")
    translator2 = translation_manager.get_translator("en")
    assert translator1 is translator2  # Vérifie que le même objet est réutilisé

def test_conversation_validation():
    """Test la validation des conversations"""
    # Test avec une conversation vide
    with pytest.raises(ValueError):
        Conversation(messages=[], user_id="test_user")
    
    # Test avec une conversation valide
    conversation = Conversation(
        messages=[Message(role="user", content="Test")],
        user_id="test_user"
    )
    assert len(conversation.messages) == 1
    assert conversation.user_id == "test_user"

def test_response_validation():
    """Test la validation des réponses"""
    # Test avec une réponse valide
    response = Response(
        message="Test message",
        action="Contacter immédiatement",
        priority="Haute"
    )
    assert response.message == "Test message"
    assert response.action == "Contacter immédiatement"
    assert response.priority == "Haute"
    
    # Test avec une action invalide
    with pytest.raises(ValueError):
        Response(
            message="Test message",
            action="Action invalide",
            priority="Haute"
        ) 