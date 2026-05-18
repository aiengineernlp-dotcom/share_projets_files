"""Script de test pour vérifier le fonctionnement de toutes les phases du projet."""

import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_phase1() -> Dict[str, Any]:
    """Test de la Phase 1 - Collecte de données."""
    logger.info("Démarrage des tests de la Phase 1")
    try:
        from phase1.database_manager import DatabaseManager
        from phase1.reddit_scraper import RedditScraper
        
        # Test de la base de données
        db = DatabaseManager("data/phase1_data.db")
        logger.info("✓ Base de données initialisée avec succès")
        
        # Test du scraper Reddit
        scraper = RedditScraper()
        logger.info("✓ Scraper Reddit initialisé avec succès")
        
        return {
            "status": "success",
            "message": "Phase 1 testée avec succès",
            "database_o": "ok",
            "scraper": "ok"
        }
    except Exception as e:
        logger.error(f"Erreur dans la Phase 1: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def test_phase2() -> Dict[str, Any]:
    """Test de la Phase 2 - Traitement du langage naturel."""
    logger.info("Démarrage des tests de la Phase 2")
    try:
        from phase2.text_processor import TextProcessor
        from phase2.entity_extractor import EntityExtractor
        from phase2.sentiment_analyzer import SentimentAnalyzer
        
        # Test du processeur de texte
        processor = TextProcessor()
        test_text = "J'ai des symptômes de fièvre et de toux."
        processed_text = processor.preprocess(test_text)
        logger.info("✓ Processeur de texte testé avec succès")
        
        # Test de l'extracteur d'entités
        extractor = EntityExtractor()
        entities = extractor.extract_entities(test_text)
        logger.info("✓ Extracteur d'entités testé avec succès")
        
        # Test de l'analyseur de sentiment
        analyzer = SentimentAnalyzer()
        sentiment = analyzer.analyze_sentiment(test_text)
        logger.info("✓ Analyseur de sentiment testé avec succès")
        
        return {
            "status": "success",
            "message": "Phase 2 testée avec succès",
            "text_processor": "ok",
            "entity_extractor": "ok",
            "sentiment_analyzer": "ok"
        }
    except Exception as e:
        logger.error(f"Erreur dans la Phase 2: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def test_phase3() -> Dict[str, Any]:
    """Test de la Phase 3 - Analyse avancée."""
    logger.info("Démarrage des tests de la Phase 3")
    try:
        from phase3.classifier import AdvancedClassifier
        from phase3.pattern_detector import PatternDetector
        from phase3.temporal_analyzer import TemporalAnalyzer
        
        # Test du classificateur
        classifier = AdvancedClassifier()
        logger.info("✓ Classificateur initialisé avec succès")
        
        # Test du détecteur de motifs
        detector = PatternDetector()
        logger.info("✓ Détecteur de motifs initialisé avec succès")
        
        # Test de l'analyseur temporel
        analyzer = TemporalAnalyzer()
        logger.info("✓ Analyseur temporel initialisé avec succès")
        
        return {
            "status": "success",
            "message": "Phase 3 testée avec succès",
            "classifier": "ok",
            "pattern_detector": "ok",
            "temporal_analyzer": "ok"
        }
    except Exception as e:
        logger.error(f"Erreur dans la Phase 3: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def test_phase4() -> Dict[str, Any]:
    """Test de la Phase 4 - Évaluation et reporting."""
    logger.info("Démarrage des tests de la Phase 4")
    try:
        from phase4.evaluator import ModelEvaluator
        from phase4.report_generator import ReportGenerator
        from phase4.dashboard import Dashboard
        
        # Test de l'évaluateur
        evaluator = ModelEvaluator()
        logger.info("✓ Évaluateur initialisé avec succès")
        
        # Test du générateur de rapports
        report_gen = ReportGenerator()
        logger.info("✓ Générateur de rapports initialisé avec succès")
        
        # Test du tableau de bord
        dashboard = Dashboard()
        logger.info("✓ Tableau de bord initialisé avec succès")
        
        return {
            "status": "success",
            "message": "Phase 4 testée avec succès",
            "evaluator": "ok",
            "report_generator": "ok",
            "dashboard": "ok"
        }
    except Exception as e:
        logger.error(f"Erreur dans la Phase 4: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def main():
    """Fonction principale de test."""
    logger.info("Démarrage des tests du projet")
    
    # Création du dossier de logs si nécessaire
    os.makedirs("logs", exist_ok=True)
    
    # Test de chaque phase
    results = {
        "phase1": test_phase1(),
        "phase2": test_phase2(),
        "phase3": test_phase3(),
        "phase4": test_phase4()
    }
    
    # Affichage des résultats
    print("\nRésultats des tests:")
    print("-" * 50)
    for phase, result in results.items():
        status = "✓" if result.get("status") == "success" else "✗"
        print(f"{status} {phase}: {result.get('message', 'Test non exécuté')}")
    
    # Vérification finale
    all_success = all(result.get("status") == "success" for result in results.values())
    if all_success:
        logger.info("Tous les tests ont réussi!")
        sys.exit(0)
    else:
        logger.error("Certains tests ont échoué")
        sys.exit(1)

if __name__ == "__main__":
    main() 