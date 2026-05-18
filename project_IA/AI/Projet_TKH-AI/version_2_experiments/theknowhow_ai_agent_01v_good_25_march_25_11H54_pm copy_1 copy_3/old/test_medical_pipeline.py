"""
Tests d'intégration pour le pipeline de traitement médical.
"""

import pytest
from pathlib import Path
import tempfile
import sqlite3
from datetime import datetime

from src.core.data_collection.preprocessing.text_processor import TextProcessor
from src.core.data_collection.analysis.medical_analyzer import MedicalAnalyzer
from src.core.data_collection.storage.sqlite_storage import SQLiteStorage

@pytest.fixture
def temp_db():
    """Fixture pour créer une base de données temporaire."""
    with tempfile.NamedTemporaryFile(suffix='.db') as f:
        db_path = f.name
        storage = SQLiteStorage(db_path)
        yield storage
        
@pytest.fixture
def sample_posts():
    """Fixture pour créer un ensemble de posts médicaux de test."""
    return [
        {
            'id': '1',
            'title': "Severe chest pain and difficulty breathing",
            'content': "I've been experiencing severe chest pain and difficulty breathing for the last 2 hours. Should I go to the ER?",
            'score': 25,
            'num_comments': 15,
            'created_at': datetime.now().timestamp()
        },
        {
            'id': '2',
            'title': "Chronic headache getting worse",
            'content': "I've had chronic headaches for years but they're getting much worse lately. The pain is intense and medication isn't helping.",
            'score': 12,
            'num_comments': 8,
            'created_at': datetime.now().timestamp()
        },
        {
            'id': '3',
            'title': "Skin rash after new medication",
            'content': "Developed a skin rash after starting a new antibiotic. It's itchy and spreading. Should I stop the medication?",
            'score': 8,
            'num_comments': 5,
            'created_at': datetime.now().timestamp()
        }
    ]

@pytest.mark.integration
def test_complete_pipeline(temp_db, sample_posts):
    """Teste l'intégration complète du pipeline de traitement."""
    # Initialisation des composants
    processor = TextProcessor()
    analyzer = MedicalAnalyzer()
    
    # Stockage des posts bruts
    for post in sample_posts:
        temp_db.save_raw_post(post)
    
    # Vérification du stockage initial
    stored_posts = temp_db.get_unprocessed_posts()
    assert len(stored_posts) == len(sample_posts)
    
    # Traitement et analyse des posts
    processed_posts = []
    for post in stored_posts:
        try:
            # Prétraitement
            processed_data = processor.process_medical_post(post)
            assert 'medical_entities' in processed_data
            assert 'preprocessing_metadata' in processed_data
            
            # Analyse
            analyzed_data = analyzer.analyze_post(processed_data)
            assert 'sentiment' in analyzed_data
            assert 'urgency_score' in analyzed_data
            assert 'medical_category' in analyzed_data
            
            # Vérification des scores
            assert 0 <= analyzed_data['urgency_score'] <= 1
            assert 0 <= analyzed_data['relevance_score'] <= 1
            
            processed_posts.append(analyzed_data)
            
            # Stockage des résultats
            temp_db.save_analyzed_post(analyzed_data)
            temp_db.mark_post_as_processed(post['id'])
            
        except Exception as e:
            pytest.fail(f"Erreur lors du traitement du post {post['id']}: {str(e)}")
    
    # Vérification du traitement complet
    assert len(processed_posts) == len(sample_posts)
    
    # Vérification des catégories médicales
    categories = [post['medical_category'] for post in processed_posts]
    assert 'cardiology' in categories  # Pour le post de douleur thoracique
    assert 'neurology' in categories   # Pour le post de maux de tête
    assert 'dermatology' in categories # Pour le post d'éruption cutanée
    
    # Vérification des scores d'urgence
    urgency_scores = [post['urgency_score'] for post in processed_posts]
    # Le post de douleur thoracique devrait avoir le score d'urgence le plus élevé
    assert max(urgency_scores) == urgency_scores[0]
    
    # Vérification du statut de traitement
    unprocessed = temp_db.get_unprocessed_posts()
    assert len(unprocessed) == 0

@pytest.mark.integration
def test_error_handling(temp_db):
    """Teste la gestion des erreurs dans le pipeline."""
    processor = TextProcessor()
    analyzer = MedicalAnalyzer()
    
    # Test avec un post mal formaté
    invalid_post = {
        'id': 'invalid',
        'title': None,  # Titre manquant
        'content': '',  # Contenu vide
        'score': 'not_a_number',  # Score invalide
        'created_at': 'invalid_date'
    }
    
    # Le pipeline devrait gérer l'erreur sans planter
    try:
        processed_data = processor.process_medical_post(invalid_post)
        analyzed_data = analyzer.analyze_post(processed_data)
        
        # Vérifie que les champs requis sont présents même avec des données invalides
        assert 'processed_title' in processed_data
        assert 'processed_content' in processed_data
        assert 'medical_entities' in processed_data
        
        assert 'sentiment' in analyzed_data
        assert 'urgency_score' in analyzed_data
        assert 'medical_category' in analyzed_data
        
    except Exception as e:
        pytest.fail(f"Le pipeline n'a pas géré correctement les données invalides: {str(e)}")

@pytest.mark.integration
def test_batch_processing(temp_db, sample_posts):
    """Teste le traitement par lots."""
    processor = TextProcessor()
    analyzer = MedicalAnalyzer()
    batch_size = 2
    
    # Stockage des posts
    for post in sample_posts:
        temp_db.save_raw_post(post)
    
    # Traitement par lots
    total_processed = 0
    while True:
        # Récupération d'un lot
        batch = temp_db.get_unprocessed_posts(limit=batch_size)
        if not batch:
            break
            
        # Traitement du lot
        for post in batch:
            processed_data = processor.process_medical_post(post)
            analyzed_data = analyzer.analyze_post(processed_data)
            
            temp_db.save_analyzed_post(analyzed_data)
            temp_db.mark_post_as_processed(post['id'])
            total_processed += 1
            
        # Vérification de la progression
        remaining = len(temp_db.get_unprocessed_posts())
        assert remaining == len(sample_posts) - total_processed
    
    # Vérification finale
    assert total_processed == len(sample_posts)
    assert len(temp_db.get_unprocessed_posts()) == 0 