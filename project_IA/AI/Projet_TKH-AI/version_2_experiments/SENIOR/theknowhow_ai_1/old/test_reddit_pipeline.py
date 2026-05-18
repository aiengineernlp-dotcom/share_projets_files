"""
Tests end-to-end spécifiques pour la collecte et l'analyse des données Reddit.
"""

import pytest
import os
import tempfile
from pathlib import Path
from datetime import datetime
import logging

from src.core.data_collection.scrapers.social.reddit_scraper import RedditScraper
from src.core.data_collection.preprocessing.text_processor import TextProcessor
from src.core.data_collection.analysis.medical_analyzer import MedicalAnalyzer
from src.core.data_collection.storage.sqlite_storage import SQLiteStorage

@pytest.fixture
def reddit_config():
    """Configuration spécifique pour les tests Reddit."""
    return {
        'subreddits': ['AskDocs', 'medical', 'Health'],
        'time_filter': 'day',
        'limit': 5,
        'search_query': 'flair:emergency OR urgent OR severe',
        'min_relevance': 0.5,
        'batch_size': 2
    }

@pytest.fixture
def temp_workspace():
    """Crée un espace de travail temporaire pour les tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        (workspace / "data" / "databases").mkdir(parents=True)
        (workspace / "data" / "logs").mkdir(parents=True)
        
        paths = {
            'workspace': workspace,
            'database': workspace / "data" / "databases" / "reddit_posts.db",
            'logs': workspace / "data" / "logs" / "reddit_test.log"
        }
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(paths['logs']),
                logging.StreamHandler()
            ]
        )
        
        yield paths

@pytest.mark.reddit
@pytest.mark.e2e
def test_reddit_collection(temp_workspace, reddit_config):
    """
    Teste la collecte des posts Reddit.
    """
    scraper = RedditScraper()
    storage = SQLiteStorage(temp_workspace['database'])
    
    logging.info("Démarrage du test de collecte Reddit")
    
    try:
        # Collecte des posts
        raw_posts = scraper.collect_posts(
            subreddits=reddit_config['subreddits'],
            time_filter=reddit_config['time_filter'],
            limit=reddit_config['limit'],
            search_query=reddit_config['search_query']
        )
        
        assert len(raw_posts) > 0, "Aucun post Reddit collecté"
        logging.info(f"{len(raw_posts)} posts collectés")
        
        # Vérification du format des posts
        for post in raw_posts:
            required_fields = {'id', 'title', 'content', 'score', 'num_comments', 'created_at'}
            assert all(field in post for field in required_fields), f"Champs manquants dans le post {post['id']}"
            storage.save_raw_post(post)
            
        logging.info("Test de collecte Reddit terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur lors de la collecte Reddit: {str(e)}")
        pytest.fail(str(e))

@pytest.mark.reddit
@pytest.mark.e2e
def test_reddit_processing(temp_workspace, reddit_config):
    """
    Teste le traitement et l'analyse des posts Reddit.
    """
    processor = TextProcessor()
    analyzer = MedicalAnalyzer()
    storage = SQLiteStorage(temp_workspace['database'])
    
    # Création de posts de test
    test_posts = []
    for i in range(3):
        post = {
            'id': f"reddit_{i}",
            'title': f"Test Reddit post {i}",
            'content': "Symptômes: fièvre, toux, fatigue. Urgent.",
            'score': 10,
            'num_comments': 5,
            'created_at': datetime.now().timestamp(),
            'subreddit': reddit_config['subreddits'][0]
        }
        test_posts.append(post)
        storage.save_raw_post(post)
    
    processed_count = 0
    relevant_count = 0
    
    try:
        for post in test_posts:
            # Prétraitement
            processed_data = processor.process_medical_post(post)
            assert 'medical_entities' in processed_data
            
            # Analyse
            analyzed_data = analyzer.analyze_post(processed_data)
            assert 'urgency_score' in analyzed_data
            assert 'relevance_score' in analyzed_data
            
            if analyzed_data['relevance_score'] >= reddit_config['min_relevance']:
                storage.save_analyzed_post(analyzed_data)
                relevant_count += 1
            
            storage.mark_post_as_processed(post['id'])
            processed_count += 1
        
        # Vérifications
        assert processed_count == len(test_posts)
        assert relevant_count > 0
        
        # Vérification des scores et catégories
        analyzed_posts = storage.get_analyzed_posts()
        for post in analyzed_posts:
            assert 0 <= post['urgency_score'] <= 1
            assert 0 <= post['relevance_score'] <= 1
            assert post['medical_category'] in {
                'cardiology', 'neurology', 'dermatology',
                'gastroenterology', 'orthopedics', 'general'
            }
            assert len(post['symptoms']) > 0
        
        logging.info(
            f"Test de traitement terminé: "
            f"{processed_count} posts traités, "
            f"{relevant_count} posts pertinents"
        )
        
    except Exception as e:
        logging.error(f"Erreur lors du traitement: {str(e)}")
        pytest.fail(str(e))

@pytest.mark.reddit
@pytest.mark.e2e
def test_reddit_error_handling(temp_workspace, reddit_config):
    """
    Teste la gestion des erreurs pour le pipeline Reddit.
    """
    scraper = RedditScraper()
    processor = TextProcessor()
    analyzer = MedicalAnalyzer()
    storage = SQLiteStorage(temp_workspace['database'])
    
    # Test avec un post invalide
    invalid_post = {
        'id': 'invalid_1',
        'title': 'Test invalide'
        # Champs manquants intentionnellement
    }
    
    try:
        storage.save_raw_post(invalid_post)
        processed_data = processor.process_medical_post(invalid_post)
        pytest.fail("Le traitement aurait dû échouer avec un post invalide")
    except Exception as e:
        logging.info(f"Erreur attendue capturée: {str(e)}")
    
    # Test avec une requête invalide
    try:
        scraper.collect_posts(
            subreddits=['subreddit_inexistant'],
            time_filter='invalid',
            limit=1
        )
        pytest.fail("La collecte aurait dû échouer avec un subreddit invalide")
    except Exception as e:
        logging.info(f"Erreur attendue capturée: {str(e)}")
    
    logging.info("Tests de gestion d'erreurs terminés avec succès") 