"""
Tests d'intégration pour le stockage des données médicales.
"""

import pytest
import tempfile
from pathlib import Path
import logging
from datetime import datetime, timedelta

from src.core.data_collection.storage.sqlite_storage import SQLiteStorage

@pytest.fixture
def storage_instance(base_integration_workspace):
    """Initialise une instance de stockage pour les tests."""
    db_path = base_integration_workspace['databases_dir'] / "storage_test.db"
    return SQLiteStorage(str(db_path))

@pytest.fixture
def sample_analyzed_posts():
    """Génère un ensemble de posts analysés pour les tests."""
    current_time = datetime.now()
    return [
        {
            'id': 'post_1',
            'title': 'Chest Pain Emergency',
            'content': 'Severe chest pain with shortness of breath',
            'processed_text': 'severe chest pain shortness breath',
            'medical_entities': ['chest pain', 'shortness of breath'],
            'urgency_score': 0.9,
            'relevance_score': 0.85,
            'medical_category': 'cardiology',
            'symptoms': ['chest pain', 'dyspnea'],
            'created_at': current_time.timestamp(),
            'processed_at': current_time.timestamp()
        },
        {
            'id': 'post_2',
            'title': 'Chronic Headache',
            'content': 'Daily headaches for 2 weeks',
            'processed_text': 'daily headaches two weeks',
            'medical_entities': ['headache', 'chronic'],
            'urgency_score': 0.5,
            'relevance_score': 0.75,
            'medical_category': 'neurology',
            'symptoms': ['chronic headache'],
            'created_at': (current_time - timedelta(days=1)).timestamp(),
            'processed_at': current_time.timestamp()
        }
    ]

@pytest.mark.integration
def test_basic_storage_operations(storage_instance, sample_analyzed_posts):
    """
    Teste les opérations basiques de stockage.
    """
    # Sauvegarde des posts
    for post in sample_analyzed_posts:
        storage_instance.save_analyzed_post(post)
    
    # Récupération et vérification
    stored_posts = storage_instance.get_analyzed_posts()
    assert len(stored_posts) == len(sample_analyzed_posts)
    
    for stored_post in stored_posts:
        original_post = next(p for p in sample_analyzed_posts if p['id'] == stored_post['id'])
        assert stored_post['urgency_score'] == original_post['urgency_score']
        assert stored_post['medical_category'] == original_post['medical_category']
        assert set(stored_post['symptoms']) == set(original_post['symptoms'])

@pytest.mark.integration
def test_data_persistence(storage_instance, sample_analyzed_posts):
    """
    Teste la persistance des données après réinitialisation de la connexion.
    """
    # Sauvegarde initiale
    for post in sample_analyzed_posts:
        storage_instance.save_analyzed_post(post)
    
    # Réinitialisation de la connexion
    db_path = storage_instance.db_path
    storage_instance = SQLiteStorage(db_path)
    
    # Vérification après réinitialisation
    stored_posts = storage_instance.get_analyzed_posts()
    assert len(stored_posts) == len(sample_analyzed_posts)
    
    for post in sample_analyzed_posts:
        stored_post = next(p for p in stored_posts if p['id'] == post['id'])
        assert stored_post is not None

@pytest.mark.integration
def test_update_operations(storage_instance, sample_analyzed_posts):
    """
    Teste les opérations de mise à jour des posts.
    """
    # Sauvegarde initiale
    for post in sample_analyzed_posts:
        storage_instance.save_analyzed_post(post)
    
    # Modification d'un post
    updated_post = sample_analyzed_posts[0].copy()
    updated_post['urgency_score'] = 0.95
    updated_post['symptoms'].append('fatigue')
    storage_instance.save_analyzed_post(updated_post)
    
    # Vérification de la mise à jour
    stored_posts = storage_instance.get_analyzed_posts()
    updated_stored_post = next(p for p in stored_posts if p['id'] == updated_post['id'])
    
    assert updated_stored_post['urgency_score'] == 0.95
    assert 'fatigue' in updated_stored_post['symptoms']
    assert len(stored_posts) == len(sample_analyzed_posts)  # Pas de doublon créé

@pytest.mark.integration
def test_query_operations(storage_instance, sample_analyzed_posts):
    """
    Teste les opérations de requête sur les données stockées.
    """
    # Sauvegarde des posts
    for post in sample_analyzed_posts:
        storage_instance.save_analyzed_post(post)
    
    # Test de requête par catégorie
    cardiology_posts = storage_instance.get_posts_by_category('cardiology')
    assert len(cardiology_posts) == 1
    assert cardiology_posts[0]['id'] == 'post_1'
    
    # Test de requête par niveau d'urgence
    urgent_posts = storage_instance.get_posts_by_urgency_threshold(0.8)
    assert len(urgent_posts) == 1
    assert urgent_posts[0]['urgency_score'] >= 0.8
    
    # Test de requête par symptôme
    headache_posts = storage_instance.get_posts_by_symptom('headache')
    assert len(headache_posts) == 1
    assert 'headache' in ' '.join(headache_posts[0]['symptoms'])

@pytest.mark.integration
def test_data_integrity(storage_instance, sample_analyzed_posts):
    """
    Teste l'intégrité des données stockées.
    """
    # Test d'insertion de données invalides
    invalid_post = {
        'id': 'invalid_1',
        'title': 'Invalid Post'
        # Champs manquants intentionnellement
    }
    
    with pytest.raises(Exception):
        storage_instance.save_analyzed_post(invalid_post)
    
    # Vérification que les données valides sont toujours acceptées
    for post in sample_analyzed_posts:
        storage_instance.save_analyzed_post(post)
    
    stored_posts = storage_instance.get_analyzed_posts()
    assert len(stored_posts) == len(sample_analyzed_posts)
    
    # Vérification de l'intégrité des données stockées
    for stored_post in stored_posts:
        assert all(key in stored_post for key in [
            'id', 'title', 'content', 'processed_text', 'medical_entities',
            'urgency_score', 'relevance_score', 'medical_category', 'symptoms',
            'created_at', 'processed_at'
        ])

@pytest.mark.integration
def test_concurrent_operations(storage_instance, sample_analyzed_posts):
    """
    Teste les opérations concurrentes sur le stockage.
    """
    from concurrent.futures import ThreadPoolExecutor
    import random
    import time
    
    def save_and_verify(post):
        storage_instance.save_analyzed_post(post)
        time.sleep(random.uniform(0.1, 0.3))  # Simulation de latence
        stored = next(p for p in storage_instance.get_analyzed_posts() if p['id'] == post['id'])
        assert stored['urgency_score'] == post['urgency_score']
        return True
    
    # Test d'opérations concurrentes
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(save_and_verify, post) for post in sample_analyzed_posts * 2]
        results = [f.result() for f in futures]
    
    assert all(results)
    
    # Vérification finale
    stored_posts = storage_instance.get_analyzed_posts()
    assert len(stored_posts) == len(sample_analyzed_posts)  # Pas de doublons 