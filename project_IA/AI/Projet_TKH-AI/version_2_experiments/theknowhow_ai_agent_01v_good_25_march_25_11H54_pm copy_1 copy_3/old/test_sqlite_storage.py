"""
Tests unitaires pour le stockage SQLite.
"""

import pytest
import sqlite3
from pathlib import Path
import tempfile
from datetime import datetime

from src.core.data_collection.storage.sqlite_storage import SQLiteStorage

@pytest.fixture
def temp_db_path():
    """Crée un chemin temporaire pour la base de données de test."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        yield Path(f.name)
        Path(f.name).unlink()

@pytest.fixture
def storage(temp_db_path):
    """Crée une instance de SQLiteStorage pour les tests."""
    return SQLiteStorage(str(temp_db_path))

@pytest.fixture
def sample_post():
    """Crée un post médical analysé pour les tests."""
    return {
        'id': 'test_1',
        'title': 'Test Medical Post',
        'content': 'Test content with medical symptoms',
        'processed_text': 'test content medical symptoms',
        'medical_entities': ['symptom1', 'symptom2'],
        'urgency_score': 0.8,
        'relevance_score': 0.7,
        'medical_category': 'general',
        'symptoms': ['headache', 'fever'],
        'created_at': datetime.now().timestamp(),
        'processed_at': datetime.now().timestamp()
    }

class TestSQLiteStorage:
    """Tests pour la classe SQLiteStorage."""

    def test_init(self, temp_db_path):
        """Teste l'initialisation du stockage."""
        storage = SQLiteStorage(str(temp_db_path))
        assert storage.db_path == str(temp_db_path)
        
        # Vérifie que la base de données est créée
        assert Path(temp_db_path).exists()
        
        # Vérifie que les tables sont créées
        with sqlite3.connect(str(temp_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert 'medical_posts' in tables

    def test_save_post(self, storage, sample_post):
        """Teste la sauvegarde d'un post."""
        # Sauvegarde du post
        storage.save_analyzed_post(sample_post)
        
        # Récupération et vérification
        stored_posts = storage.get_analyzed_posts()
        assert len(stored_posts) == 1
        
        stored_post = stored_posts[0]
        assert stored_post['id'] == sample_post['id']
        assert stored_post['urgency_score'] == sample_post['urgency_score']
        assert stored_post['medical_category'] == sample_post['medical_category']
        assert set(stored_post['symptoms']) == set(sample_post['symptoms'])

    def test_update_post(self, storage, sample_post):
        """Teste la mise à jour d'un post existant."""
        # Sauvegarde initiale
        storage.save_analyzed_post(sample_post)
        
        # Modification et mise à jour
        updated_post = sample_post.copy()
        updated_post['urgency_score'] = 0.9
        updated_post['symptoms'].append('nausea')
        storage.save_analyzed_post(updated_post)
        
        # Vérification
        stored_posts = storage.get_analyzed_posts()
        assert len(stored_posts) == 1  # Pas de doublon
        
        stored_post = stored_posts[0]
        assert stored_post['urgency_score'] == 0.9
        assert 'nausea' in stored_post['symptoms']

    def test_get_posts_by_category(self, storage, sample_post):
        """Teste la récupération des posts par catégorie."""
        # Sauvegarde de posts avec différentes catégories
        posts = [
            sample_post,
            {**sample_post, 'id': 'test_2', 'medical_category': 'cardiology'},
            {**sample_post, 'id': 'test_3', 'medical_category': 'general'}
        ]
        
        for post in posts:
            storage.save_analyzed_post(post)
        
        # Test de récupération par catégorie
        general_posts = storage.get_posts_by_category('general')
        assert len(general_posts) == 2
        assert all(post['medical_category'] == 'general' for post in general_posts)
        
        cardiology_posts = storage.get_posts_by_category('cardiology')
        assert len(cardiology_posts) == 1
        assert cardiology_posts[0]['medical_category'] == 'cardiology'

    def test_get_posts_by_urgency(self, storage, sample_post):
        """Teste la récupération des posts par niveau d'urgence."""
        # Sauvegarde de posts avec différents niveaux d'urgence
        posts = [
            sample_post,
            {**sample_post, 'id': 'test_2', 'urgency_score': 0.5},
            {**sample_post, 'id': 'test_3', 'urgency_score': 0.9}
        ]
        
        for post in posts:
            storage.save_analyzed_post(post)
        
        # Test de récupération par seuil d'urgence
        urgent_posts = storage.get_posts_by_urgency_threshold(0.8)
        assert len(urgent_posts) == 2
        assert all(post['urgency_score'] >= 0.8 for post in urgent_posts)
        
        non_urgent_posts = storage.get_posts_by_urgency_threshold(0.6, operator='<')
        assert len(non_urgent_posts) == 1
        assert non_urgent_posts[0]['urgency_score'] < 0.6

    def test_get_posts_by_symptom(self, storage, sample_post):
        """Teste la récupération des posts par symptôme."""
        # Sauvegarde de posts avec différents symptômes
        posts = [
            sample_post,
            {**sample_post, 'id': 'test_2', 'symptoms': ['cough', 'fever']},
            {**sample_post, 'id': 'test_3', 'symptoms': ['headache', 'nausea']}
        ]
        
        for post in posts:
            storage.save_analyzed_post(post)
        
        # Test de récupération par symptôme
        fever_posts = storage.get_posts_by_symptom('fever')
        assert len(fever_posts) == 2
        assert all('fever' in post['symptoms'] for post in fever_posts)
        
        headache_posts = storage.get_posts_by_symptom('headache')
        assert len(headache_posts) == 2
        assert all('headache' in post['symptoms'] for post in headache_posts)

    def test_error_handling(self, storage):
        """Teste la gestion des erreurs."""
        # Test avec un post invalide (champs manquants)
        invalid_post = {'id': 'invalid_1', 'title': 'Test'}
        
        with pytest.raises(Exception):
            storage.save_analyzed_post(invalid_post)
        
        # Test avec des valeurs invalides
        invalid_post = {
            **sample_post,
            'urgency_score': 1.5  # Score invalide > 1
        }
        
        with pytest.raises(ValueError):
            storage.save_analyzed_post(invalid_post)

    def test_data_integrity(self, storage, sample_post):
        """Teste l'intégrité des données stockées."""
        # Test de sauvegarde avec tous les champs requis
        storage.save_analyzed_post(sample_post)
        
        # Récupération et vérification de tous les champs
        stored_post = storage.get_analyzed_posts()[0]
        
        required_fields = [
            'id', 'title', 'content', 'processed_text', 'medical_entities',
            'urgency_score', 'relevance_score', 'medical_category', 'symptoms',
            'created_at', 'processed_at'
        ]
        
        for field in required_fields:
            assert field in stored_post
            assert stored_post[field] == sample_post[field]

    def test_connection_management(self, storage, sample_post):
        """Teste la gestion des connexions à la base de données."""
        # Test de multiples opérations
        for i in range(5):
            post = {**sample_post, 'id': f'test_{i}'}
            storage.save_analyzed_post(post)
        
        # Vérifie que les connexions sont correctement fermées
        stored_posts = storage.get_analyzed_posts()
        assert len(stored_posts) == 5
        
        # Vérifie qu'une nouvelle connexion peut être établie
        new_storage = SQLiteStorage(storage.db_path)
        assert len(new_storage.get_analyzed_posts()) == 5 