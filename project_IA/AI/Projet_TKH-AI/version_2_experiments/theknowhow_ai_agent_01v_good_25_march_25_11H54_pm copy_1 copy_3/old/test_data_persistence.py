"""
Tests d'intégration pour la persistance des données.
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

from src.core.data_collection.storage.sqlite_storage import SQLiteStorage

@pytest.fixture
def temp_db():
    """Fixture pour créer une base de données temporaire."""
    with tempfile.NamedTemporaryFile(suffix='.db') as f:
        db_path = f.name
        storage = SQLiteStorage(db_path)
        yield storage, db_path

@pytest.fixture
def sample_analyzed_post():
    """Fixture pour créer un post analysé de test."""
    return {
        'id': '1',
        'title': "Severe chest pain",
        'processed_title': "severe chest pain",
        'content': "Experiencing severe chest pain",
        'processed_content': "experiencing severe chest pain",
        'score': 20,
        'num_comments': 10,
        'created_at': datetime.now().timestamp(),
        'medical_entities': {
            'title': [{'text': 'chest pain', 'label': 'SYMPTOM'}],
            'content': [{'text': 'chest pain', 'label': 'SYMPTOM'}]
        },
        'sentiment': {
            'polarity': -0.5,
            'subjectivity': 0.8,
            'compound': 0.3
        },
        'urgency_score': 0.85,
        'relevance_score': 0.75,
        'medical_category': 'cardiology',
        'symptoms': ['chest pain'],
        'analysis_metadata': {
            'analyzed_at': datetime.now().timestamp(),
            'version': '1.0'
        }
    }

@pytest.mark.integration
def test_data_persistence(temp_db, sample_analyzed_post):
    """Teste la persistance complète des données."""
    storage, db_path = temp_db
    
    # Sauvegarde du post
    storage.save_analyzed_post(sample_analyzed_post)
    
    # Vérification directe dans la base de données
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Vérifie la table des posts
        cursor.execute("SELECT * FROM posts WHERE id = ?", (sample_analyzed_post['id'],))
        post_row = cursor.fetchone()
        assert post_row is not None
        
        # Vérifie la table des analyses
        cursor.execute("SELECT * FROM post_analyses WHERE post_id = ?", (sample_analyzed_post['id'],))
        analysis_row = cursor.fetchone()
        assert analysis_row is not None
        
        # Vérifie la table des entités médicales
        cursor.execute("SELECT * FROM medical_entities WHERE post_id = ?", (sample_analyzed_post['id'],))
        entities = cursor.fetchall()
        assert len(entities) > 0

@pytest.mark.integration
def test_data_retrieval(temp_db, sample_analyzed_post):
    """Teste la récupération des données."""
    storage, _ = temp_db
    
    # Sauvegarde plusieurs posts
    posts = []
    for i in range(3):
        post = sample_analyzed_post.copy()
        post['id'] = str(i + 1)
        post['created_at'] = (datetime.now() - timedelta(days=i)).timestamp()
        storage.save_analyzed_post(post)
        posts.append(post)
    
    # Teste la récupération par ID
    retrieved_post = storage.get_post_by_id(posts[0]['id'])
    assert retrieved_post is not None
    assert retrieved_post['id'] == posts[0]['id']
    
    # Teste la récupération par date
    recent_posts = storage.get_posts_by_date_range(
        start_date=(datetime.now() - timedelta(days=1)).timestamp()
    )
    assert len(recent_posts) == 2
    
    # Teste la récupération par catégorie
    cardio_posts = storage.get_posts_by_category('cardiology')
    assert len(cardio_posts) == 3

@pytest.mark.integration
def test_data_updates(temp_db, sample_analyzed_post):
    """Teste les mises à jour des données."""
    storage, _ = temp_db
    
    # Sauvegarde initiale
    storage.save_analyzed_post(sample_analyzed_post)
    
    # Mise à jour du score d'urgence
    updated_post = sample_analyzed_post.copy()
    updated_post['urgency_score'] = 0.95
    storage.update_post_analysis(updated_post)
    
    # Vérifie la mise à jour
    retrieved_post = storage.get_post_by_id(sample_analyzed_post['id'])
    assert retrieved_post['urgency_score'] == 0.95
    
    # Teste le marquage comme traité
    storage.mark_post_as_processed(sample_analyzed_post['id'])
    unprocessed = storage.get_unprocessed_posts()
    assert sample_analyzed_post['id'] not in [p['id'] for p in unprocessed]

@pytest.mark.integration
def test_data_consistency(temp_db, sample_analyzed_post):
    """Teste la cohérence des données."""
    storage, db_path = temp_db
    
    # Sauvegarde du post
    storage.save_analyzed_post(sample_analyzed_post)
    
    # Vérifie la cohérence entre les tables
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Vérifie les clés étrangères
        cursor.execute("""
            SELECT p.id, pa.post_id, me.post_id
            FROM posts p
            LEFT JOIN post_analyses pa ON p.id = pa.post_id
            LEFT JOIN medical_entities me ON p.id = me.post_id
            WHERE p.id = ?
        """, (sample_analyzed_post['id'],))
        
        rows = cursor.fetchall()
        assert len(rows) > 0
        for row in rows:
            assert row[0] == row[1] == row[2]  # Toutes les clés étrangères correspondent
            
    # Teste la suppression en cascade
    storage.delete_post(sample_analyzed_post['id'])
    
    # Vérifie que toutes les données associées ont été supprimées
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM posts WHERE id = ?", (sample_analyzed_post['id'],))
        assert cursor.fetchone()[0] == 0
        
        cursor.execute("SELECT COUNT(*) FROM post_analyses WHERE post_id = ?", (sample_analyzed_post['id'],))
        assert cursor.fetchone()[0] == 0
        
        cursor.execute("SELECT COUNT(*) FROM medical_entities WHERE post_id = ?", (sample_analyzed_post['id'],))
        assert cursor.fetchone()[0] == 0 