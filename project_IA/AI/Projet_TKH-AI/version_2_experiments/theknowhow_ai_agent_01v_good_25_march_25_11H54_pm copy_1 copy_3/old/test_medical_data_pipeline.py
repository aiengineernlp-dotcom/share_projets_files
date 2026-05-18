"""
Tests end-to-end pour le pipeline complet de traitement des données médicales.
"""

import pytest
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import logging

from src.core.data_collection.scrapers.social.reddit_scraper import RedditScraper
from src.core.data_collection.preprocessing.text_processor import TextProcessor
from src.core.data_collection.analysis.medical_analyzer import MedicalAnalyzer
from src.core.data_collection.storage.sqlite_storage import SQLiteStorage

@pytest.fixture
def test_config():
    """Fixture pour la configuration de test."""
    return {
        'reddit': {
            'subreddits': ['AskDocs', 'medical', 'Health'],
            'time_filter': 'day',
            'limit': 5,
            'search_query': 'flair:emergency OR urgent OR severe'
        },
        'processing': {
            'batch_size': 2,
            'min_relevance': 0.5
        }
    }

@pytest.fixture
def temp_workspace():
    """Fixture pour créer un espace de travail temporaire."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Création de la structure des dossiers
        workspace = Path(temp_dir)
        (workspace / "data" / "databases").mkdir(parents=True)
        (workspace / "data" / "logs").mkdir(parents=True)
        
        # Configuration des chemins
        paths = {
            'workspace': workspace,
            'database': workspace / "data" / "databases" / "medical_posts.db",
            'logs': workspace / "data" / "logs" / "e2e_test.log"
        }
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(paths['logs']),
                logging.StreamHandler()
            ]
        )
        
        yield paths

@pytest.mark.e2e
def test_complete_pipeline(temp_workspace, test_config):
    """
    Teste le pipeline complet de bout en bout :
    1. Collecte des données depuis Reddit
    2. Prétraitement des posts
    3. Analyse médicale
    4. Stockage et récupération
    """
    # Initialisation des composants
    scraper = RedditScraper()
    processor = TextProcessor()
    analyzer = MedicalAnalyzer()
    storage = SQLiteStorage(temp_workspace['database'])
    
    logging.info("Démarrage du test end-to-end")
    
    try:
        # 1. Collecte des données
        logging.info("Collecte des posts Reddit")
        raw_posts = scraper.collect_posts(
            subreddits=test_config['reddit']['subreddits'],
            time_filter=test_config['reddit']['time_filter'],
            limit=test_config['reddit']['limit'],
            search_query=test_config['reddit']['search_query']
        )
        
        assert len(raw_posts) > 0, "Aucun post collecté"
        logging.info(f"{len(raw_posts)} posts collectés")
        
        # Stockage initial des posts bruts
        for post in raw_posts:
            storage.save_raw_post(post)
        
        # 2. Traitement par lots
        processed_count = 0
        relevant_count = 0
        batch_size = test_config['processing']['batch_size']
        
        while True:
            # Récupération d'un lot de posts non traités
            batch = storage.get_unprocessed_posts(limit=batch_size)
            if not batch:
                break
                
            for post in batch:
                try:
                    # Prétraitement
                    processed_data = processor.process_medical_post(post)
                    assert 'medical_entities' in processed_data
                    
                    # Analyse
                    analyzed_data = analyzer.analyze_post(processed_data)
                    assert 'urgency_score' in analyzed_data
                    
                    # Filtre sur la pertinence
                    if analyzed_data['relevance_score'] >= test_config['processing']['min_relevance']:
                        storage.save_analyzed_post(analyzed_data)
                        relevant_count += 1
                        
                    storage.mark_post_as_processed(post['id'])
                    processed_count += 1
                    
                except Exception as e:
                    logging.error(f"Erreur lors du traitement du post {post['id']}: {str(e)}")
                    continue
                    
        logging.info(f"Traitement terminé: {processed_count} posts traités, {relevant_count} pertinents")
        
        # 3. Vérification des résultats
        # Vérifie que tous les posts ont été traités
        assert len(storage.get_unprocessed_posts()) == 0
        
        # Récupère les posts analysés
        analyzed_posts = storage.get_analyzed_posts()
        assert len(analyzed_posts) == relevant_count
        
        # Vérifie la qualité des analyses
        for post in analyzed_posts:
            assert 0 <= post['urgency_score'] <= 1
            assert 0 <= post['relevance_score'] <= 1
            assert post['medical_category'] in {
                'cardiology', 'neurology', 'dermatology',
                'gastroenterology', 'orthopedics', 'general'
            }
            assert len(post['symptoms']) > 0
            
        # 4. Tests de requêtes spécifiques
        # Posts urgents
        urgent_posts = [p for p in analyzed_posts if p['urgency_score'] > 0.7]
        logging.info(f"Nombre de posts urgents: {len(urgent_posts)}")
        
        # Posts par catégorie
        categories = {}
        for post in analyzed_posts:
            cat = post['medical_category']
            categories[cat] = categories.get(cat, 0) + 1
        logging.info(f"Distribution par catégorie: {categories}")
        
        # 5. Vérification de la persistance
        # Recharge la base de données
        new_storage = SQLiteStorage(temp_workspace['database'])
        reloaded_posts = new_storage.get_analyzed_posts()
        assert len(reloaded_posts) == len(analyzed_posts)
        
        logging.info("Test end-to-end terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur lors du test end-to-end: {str(e)}")
        pytest.fail(f"Le test end-to-end a échoué: {str(e)}")

@pytest.mark.e2e
def test_error_recovery(temp_workspace, test_config):
    """
    Teste la récupération après erreur du pipeline :
    1. Simule des erreurs pendant le traitement
    2. Vérifie que le système peut reprendre après une erreur
    3. Vérifie l'intégrité des données
    """
    scraper = RedditScraper()
    processor = TextProcessor()
    analyzer = MedicalAnalyzer()
    storage = SQLiteStorage(temp_workspace['database'])
    
    logging.info("Démarrage du test de récupération après erreur")
    
    try:
        # 1. Collecte initiale
        raw_posts = scraper.collect_posts(
            subreddits=test_config['reddit']['subreddits'],
            limit=3
        )
        
        for post in raw_posts:
            storage.save_raw_post(post)
            
        # 2. Simulation d'une erreur pendant le traitement
        processed_count = 0
        for post in storage.get_unprocessed_posts():
            if processed_count == 1:  # Simule une erreur au deuxième post
                raise Exception("Erreur simulée")
                
            processed_data = processor.process_medical_post(post)
            analyzed_data = analyzer.analyze_post(processed_data)
            storage.save_analyzed_post(analyzed_data)
            storage.mark_post_as_processed(post['id'])
            processed_count += 1
            
    except Exception as e:
        logging.error(f"Erreur simulée capturée: {str(e)}")
        
    # 3. Vérification de l'état après erreur
    remaining_posts = storage.get_unprocessed_posts()
    assert len(remaining_posts) > 0
    
    # 4. Reprise du traitement
    for post in remaining_posts:
        try:
            processed_data = processor.process_medical_post(post)
            analyzed_data = analyzer.analyze_post(processed_data)
            storage.save_analyzed_post(analyzed_data)
            storage.mark_post_as_processed(post['id'])
            
        except Exception as e:
            logging.error(f"Erreur lors de la reprise: {str(e)}")
            continue
            
    # 5. Vérification finale
    assert len(storage.get_unprocessed_posts()) == 0
    logging.info("Test de récupération après erreur terminé avec succès") 