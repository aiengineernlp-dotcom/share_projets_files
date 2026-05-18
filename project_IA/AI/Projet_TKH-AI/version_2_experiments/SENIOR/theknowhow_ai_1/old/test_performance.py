"""
Tests de performance pour le pipeline de traitement des données médicales.
"""

import pytest
import time
import logging
from pathlib import Path
import tempfile
from datetime import datetime
import statistics

from src.core.data_collection.scrapers.social.reddit_scraper import RedditScraper
from src.core.data_collection.preprocessing.text_processor import TextProcessor
from src.core.data_collection.analysis.medical_analyzer import MedicalAnalyzer
from src.core.data_collection.storage.sqlite_storage import SQLiteStorage

@pytest.fixture
def performance_config():
    """Fixture pour la configuration des tests de performance."""
    return {
        'reddit': {
            'subreddits': ['AskDocs', 'medical', 'Health'],
            'time_filter': 'week',
            'limit': 50  # Nombre plus important pour les tests de performance
        },
        'batch_sizes': [1, 5, 10, 20],
        'iterations': 3,  # Nombre d'itérations pour moyenner les résultats
        'performance_thresholds': {
            'processing_time_per_post': 2.0,  # secondes
            'memory_per_post': 5 * 1024 * 1024,  # 5 MB
            'db_operation_time': 0.1  # secondes
        }
    }

@pytest.fixture
def temp_workspace():
    """Fixture pour créer un espace de travail temporaire."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        (workspace / "data" / "databases").mkdir(parents=True)
        (workspace / "data" / "logs").mkdir(parents=True)
        
        paths = {
            'workspace': workspace,
            'database': workspace / "data" / "databases" / "performance_test.db",
            'logs': workspace / "data" / "logs" / "performance_test.log"
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

class PerformanceMetrics:
    """Classe pour collecter et analyser les métriques de performance."""
    
    def __init__(self):
        self.processing_times = []
        self.db_operation_times = []
        self.batch_metrics = {}
        
    def add_processing_time(self, time_seconds):
        self.processing_times.append(time_seconds)
        
    def add_db_operation_time(self, time_seconds):
        self.db_operation_times.append(time_seconds)
        
    def add_batch_metric(self, batch_size, metric_name, value):
        if batch_size not in self.batch_metrics:
            self.batch_metrics[batch_size] = {}
        if metric_name not in self.batch_metrics[batch_size]:
            self.batch_metrics[batch_size][metric_name] = []
        self.batch_metrics[batch_size][metric_name].append(value)
        
    def get_average_processing_time(self):
        return statistics.mean(self.processing_times)
        
    def get_average_db_operation_time(self):
        return statistics.mean(self.db_operation_times)
        
    def get_batch_statistics(self, batch_size, metric_name):
        values = self.batch_metrics[batch_size][metric_name]
        return {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0
        }

@pytest.mark.e2e
@pytest.mark.performance
def test_processing_performance(temp_workspace, performance_config):
    """
    Teste les performances du pipeline de traitement :
    1. Mesure le temps de traitement par post
    2. Analyse l'impact de différentes tailles de lots
    3. Vérifie les seuils de performance
    """
    metrics = PerformanceMetrics()
    
    # Initialisation des composants
    scraper = RedditScraper()
    processor = TextProcessor()
    analyzer = MedicalAnalyzer()
    storage = SQLiteStorage(temp_workspace['database'])
    
    logging.info("Démarrage des tests de performance")
    
    try:
        # 1. Collecte des données de test
        raw_posts = scraper.collect_posts(**performance_config['reddit'])
        assert len(raw_posts) > 0, "Aucun post collecté pour les tests de performance"
        
        # 2. Tests avec différentes tailles de lots
        for batch_size in performance_config['batch_sizes']:
            logging.info(f"\nTest avec taille de lot = {batch_size}")
            
            for iteration in range(performance_config['iterations']):
                # Réinitialisation de la base de données
                storage.reset_database()
                
                # Stockage initial
                start_time = time.time()
                for post in raw_posts:
                    storage.save_raw_post(post)
                db_time = time.time() - start_time
                metrics.add_batch_metric(batch_size, 'db_write_time', db_time)
                
                # Traitement par lots
                total_processing_time = 0
                processed_count = 0
                
                for i in range(0, len(raw_posts), batch_size):
                    batch = raw_posts[i:i + batch_size]
                    
                    # Mesure du temps de traitement
                    start_time = time.time()
                    
                    for post in batch:
                        # Prétraitement
                        processed_data = processor.process_medical_post(post)
                        
                        # Analyse
                        analyzed_data = analyzer.analyze_post(processed_data)
                        
                        # Stockage
                        storage.save_analyzed_post(analyzed_data)
                        processed_count += 1
                        
                    batch_time = time.time() - start_time
                    metrics.add_batch_metric(batch_size, 'batch_processing_time', batch_time)
                    total_processing_time += batch_time
                
                # Calcul des métriques moyennes
                avg_time_per_post = total_processing_time / processed_count
                metrics.add_processing_time(avg_time_per_post)
                
                logging.info(
                    f"Itération {iteration + 1}: "
                    f"Temps moyen par post = {avg_time_per_post:.3f}s, "
                    f"Total = {total_processing_time:.3f}s"
                )
        
        # 3. Analyse des résultats
        logging.info("\nRésultats de performance:")
        
        # Temps de traitement moyen
        avg_processing_time = metrics.get_average_processing_time()
        logging.info(f"Temps de traitement moyen par post: {avg_processing_time:.3f}s")
        assert avg_processing_time <= performance_config['performance_thresholds']['processing_time_per_post']
        
        # Analyse par taille de lot
        for batch_size in performance_config['batch_sizes']:
            stats = metrics.get_batch_statistics(batch_size, 'batch_processing_time')
            logging.info(
                f"\nTaille de lot {batch_size}:"
                f"\n  - Temps moyen: {stats['mean']:.3f}s"
                f"\n  - Médiane: {stats['median']:.3f}s"
                f"\n  - Écart-type: {stats['std_dev']:.3f}s"
            )
        
        logging.info("Tests de performance terminés avec succès")
        
    except Exception as e:
        logging.error(f"Erreur lors des tests de performance: {str(e)}")
        pytest.fail(str(e))

@pytest.mark.e2e
@pytest.mark.performance
def test_database_performance(temp_workspace, performance_config):
    """
    Teste les performances des opérations de base de données :
    1. Mesure les temps d'écriture
    2. Mesure les temps de lecture
    3. Vérifie les seuils de performance
    """
    metrics = PerformanceMetrics()
    storage = SQLiteStorage(temp_workspace['database'])
    
    logging.info("Démarrage des tests de performance de la base de données")
    
    try:
        # Création d'un ensemble de données de test
        test_posts = []
        for i in range(100):
            test_posts.append({
                'id': f'test_{i}',
                'title': f'Test post {i}',
                'content': f'Test content {i}',
                'score': i,
                'num_comments': i,
                'created_at': datetime.now().timestamp(),
                'medical_category': 'test',
                'urgency_score': 0.5,
                'relevance_score': 0.5
            })
        
        # Test d'écriture en masse
        start_time = time.time()
        for post in test_posts:
            storage.save_raw_post(post)
        write_time = time.time() - start_time
        metrics.add_db_operation_time(write_time / len(test_posts))
        
        logging.info(f"Temps d'écriture moyen par post: {write_time / len(test_posts):.3f}s")
        
        # Test de lecture en masse
        start_time = time.time()
        posts = storage.get_unprocessed_posts(limit=100)
        read_time = time.time() - start_time
        metrics.add_db_operation_time(read_time / len(posts))
        
        logging.info(f"Temps de lecture moyen par post: {read_time / len(posts):.3f}s")
        
        # Vérification des seuils
        avg_db_time = metrics.get_average_db_operation_time()
        assert avg_db_time <= performance_config['performance_thresholds']['db_operation_time']
        
        logging.info("Tests de performance de la base de données terminés avec succès")
        
    except Exception as e:
        logging.error(f"Erreur lors des tests de performance de la base de données: {str(e)}")
        pytest.fail(str(e)) 