"""
Script de test pour vérifier le bon fonctionnement du système.
Teste tous les composants principaux et leurs interactions.
"""

import unittest
import logging
import tempfile
import shutil
from pathlib import Path
import torch
import json

from ..preprocessing.text_processor import TextProcessor
from ..nlp_core.base_model import BaseNLPModel
from ..nlp_core.medical_model import MedicalNLPModel
from ..nlp_core.trainer import ModelTrainer
from ..validation.response_validator import ResponseValidator
from ..monitoring.performance_monitor import PerformanceMonitor
from ..config import (
    MODEL_CONFIG, PREPROCESSING_CONFIG, VALIDATION_CONFIG,
    MONITORING_CONFIG, LANGUAGE_CONFIG, MEDICAL_KEYWORDS
)

class TestSystem(unittest.TestCase):
    """Tests du système complet."""
    
    @classmethod
    def setUpClass(cls):
        """Configuration initiale pour tous les tests."""
        # Configuration du logging
        logging.basicConfig(level=logging.INFO)
        cls.logger = logging.getLogger(__name__)
        
        # Création d'un répertoire temporaire
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_path = Path(cls.temp_dir)
        
        # Données de test
        cls.test_texts = [
            "J'ai mal à la tête depuis deux jours.",
            "I have a fever and cough.",
            "أشعر بألم في الصدر"
        ]
        
    @classmethod
    def tearDownClass(cls):
        """Nettoyage après les tests."""
        shutil.rmtree(cls.temp_dir)
        
    def setUp(self):
        """Configuration avant chaque test."""
        self.text_processor = TextProcessor()
        self.validator = ResponseValidator()
        self.monitor = PerformanceMonitor(str(self.temp_path / "logs"))
        
    def test_text_processing(self):
        """Test du prétraitement de texte."""
        for text in self.test_texts:
            result = self.text_processor.process_text(text)
            
            self.assertIn("cleaned_text", result)
            self.assertIn("language", result)
            self.assertIn("tokens", result)
            self.assertIn("token_count", result)
            
            self.assertGreater(len(result["tokens"]), 0)
            self.assertIn(result["language"], LANGUAGE_CONFIG["supported_languages"])
            
    def test_medical_model(self):
        """Test du modèle médical."""
        model = MedicalNLPModel(MODEL_CONFIG["base_model"])
        
        for text in self.test_texts:
            response = model.generate_medical_response(text)
            
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
            
            # Vérification des mots-clés médicaux
            language = self.text_processor.process_text(text)["language"]
            for category, patterns in MEDICAL_KEYWORDS.items():
                pattern = patterns.get(language, patterns["en"])
                if re.search(pattern, text, re.IGNORECASE):
                    self.assertIn(category, response.lower())
                    
    def test_validation(self):
        """Test de la validation des réponses."""
        model = MedicalNLPModel(MODEL_CONFIG["base_model"])
        
        for text in self.test_texts:
            response = model.generate_medical_response(text)
            validation_results = self.validator.validate_response(text, response)
            
            self.assertIn("overall_score", validation_results)
            self.assertIn("coherence_score", validation_results)
            self.assertIn("relevance_score", validation_results)
            self.assertIn("safety_score", validation_results)
            self.assertIn("completeness_score", validation_results)
            
            self.assertGreaterEqual(validation_results["overall_score"], 0)
            self.assertLessEqual(validation_results["overall_score"], 1)
            
    def test_monitoring(self):
        """Test du monitoring des performances."""
        model = MedicalNLPModel(MODEL_CONFIG["base_model"])
        
        for text in self.test_texts:
            start_time = time.time()
            response = model.generate_medical_response(text)
            response_time = time.time() - start_time
            
            self.monitor.log_response_metrics(text, response, response_time)
            
        # Vérification des métriques
        report = self.monitor.get_performance_report()
        
        self.assertIn("system_metrics", report)
        self.assertIn("quality_metrics", report)
        
        for metric in MONITORING_CONFIG["metrics_to_track"]:
            if "usage" in metric or "time" in metric:
                self.assertIn(metric, report["system_metrics"])
            else:
                self.assertIn(metric, report["quality_metrics"])
                
    def test_training(self):
        """Test de l'entraînement du modèle."""
        # Création de données d'entraînement factices
        train_data = [
            "Patient présentant des symptômes grippaux.",
            "Patient with flu-like symptoms.",
            "مريض يعاني من أعراض تشبه الإنفلونزا"
        ] * 10  # Répétition pour avoir suffisamment de données
        
        trainer = ModelTrainer(MODEL_CONFIG["base_model"])
        train_dataset, val_dataset = trainer.prepare_data(train_data)
        
        # Vérification des datasets
        self.assertGreater(len(train_dataset), 0)
        self.assertGreater(len(val_dataset), 0)
        
        # Test d'un seul batch d'entraînement
        try:
            trainer.train(
                train_dataset,
                val_dataset,
                str(self.temp_path / "models"),
                num_epochs=1,
                batch_size=MODEL_CONFIG["batch_size"],
                learning_rate=MODEL_CONFIG["learning_rate"]
            )
        except Exception as e:
            self.fail(f"L'entraînement a échoué: {str(e)}")
            
    def test_end_to_end(self):
        """Test du flux complet."""
        # 1. Prétraitement
        processed_texts = [
            self.text_processor.process_text(text)
            for text in self.test_texts
        ]
        
        # 2. Génération de réponses
        model = MedicalNLPModel(MODEL_CONFIG["base_model"])
        responses = [
            model.generate_medical_response(text)
            for text in self.test_texts
        ]
        
        # 3. Validation
        validation_results = [
            self.validator.validate_response(text, response)
            for text, response in zip(self.test_texts, responses)
        ]
        
        # 4. Monitoring
        for text, response, results in zip(self.test_texts, responses, validation_results):
            self.monitor.log_response_metrics(
                text,
                response,
                results.get("response_time", 0)
            )
            
        # Vérification des résultats
        for results in validation_results:
            self.assertGreaterEqual(results["overall_score"], VALIDATION_CONFIG["quality_threshold"])
            
        # Vérification du monitoring
        report = self.monitor.get_performance_report()
        self.assertGreater(len(report["system_metrics"]), 0)
        self.assertGreater(len(report["quality_metrics"]), 0)

if __name__ == "__main__":
    unittest.main() 