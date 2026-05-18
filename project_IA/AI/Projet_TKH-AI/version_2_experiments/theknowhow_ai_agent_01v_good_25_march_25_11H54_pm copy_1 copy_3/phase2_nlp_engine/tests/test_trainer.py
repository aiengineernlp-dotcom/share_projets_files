"""
Tests pour le trainer de modèle.
"""
import unittest
import logging
from pathlib import Path
import torch

from fine_tuning.trainer import ModelTrainer
from fine_tuning.training_config import TrainingConfig
from fine_tuning.data_loader import TrainingDataLoader

class TestModelTrainer(unittest.TestCase):
    """Tests pour la classe ModelTrainer."""
    
    def setUp(self):
        """Configuration des tests."""
        logging.basicConfig(level=logging.INFO)
        
        # Configuration minimale pour les tests
        self.config = TrainingConfig(
            model_name="microsoft/BioGPT-base",  # Version plus petite pour les tests
            num_epochs=1,
            batch_size=2,
            output_dir="tests/output",
            logging_dir="tests/logs",
            cache_dir="tests/cache"
        )
        
        # Chargement des données
        self.data_loader = TrainingDataLoader("fine_tuning/data/training_data.json")
        self.data = self.data_loader.load_data()
        self.train_data = self.data_loader.prepare_training_data(self.data)
        
        # Initialisation du trainer
        self.trainer = ModelTrainer(self.config)
        
    def test_init(self):
        """Test de l'initialisation du trainer."""
        self.assertIsNotNone(self.trainer.tokenizer)
        self.assertIsNotNone(self.trainer.model)
        self.assertTrue(Path(self.config.output_dir).exists())
        self.assertTrue(Path(self.config.logging_dir).exists())
        self.assertTrue(Path(self.config.cache_dir).exists())
        
    def test_prepare_dataset(self):
        """Test de la préparation du dataset."""
        dataset = self.trainer._prepare_dataset(*self.train_data)
        self.assertGreater(len(dataset), 0)
        self.assertIn("input_ids", dataset.features)
        self.assertIn("attention_mask", dataset.features)
        
    def test_train(self):
        """Test de l'entraînement du modèle."""
        # Utilisation d'un sous-ensemble des données pour les tests
        train_inputs = self.train_data[0][:2]
        train_outputs = self.train_data[1][:2]
        
        self.trainer.train((train_inputs, train_outputs))
        
        # Vérification que le modèle a été sauvegardé
        self.assertTrue(Path(self.config.output_dir).exists())
        self.assertTrue((Path(self.config.output_dir) / "pytorch_model.bin").exists())
        
    def test_evaluate(self):
        """Test de l'évaluation du modèle."""
        # Utilisation d'un sous-ensemble des données pour les tests
        eval_inputs = self.train_data[0][:2]
        eval_outputs = self.train_data[1][:2]
        
        metrics = self.trainer.evaluate((eval_inputs, eval_outputs))
        
        self.assertIsInstance(metrics, dict)
        self.assertIn("eval_loss", metrics)
        
    def tearDown(self):
        """Nettoyage après les tests."""
        # Suppression des répertoires de test
        import shutil
        for directory in ["tests/output", "tests/logs", "tests/cache"]:
            if Path(directory).exists():
                shutil.rmtree(directory)

if __name__ == '__main__':
    unittest.main() 