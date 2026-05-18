"""
Tests pour le chargeur de données d'entraînement.
"""
import unittest
import logging
from pathlib import Path
from fine_tuning.data_loader import TrainingDataLoader

class TestTrainingDataLoader(unittest.TestCase):
    """Tests pour la classe TrainingDataLoader."""
    
    def setUp(self):
        """Configuration des tests."""
        logging.basicConfig(level=logging.INFO)
        self.data_path = Path("fine_tuning/data/training_data.json")
        self.loader = TrainingDataLoader(str(self.data_path))
        
    def test_load_data(self):
        """Test du chargement des données."""
        data = self.loader.load_data()
        self.assertIsInstance(data, dict)
        self.assertIn('conversations', data)
        self.assertGreater(len(data['conversations']), 0)
        
    def test_prepare_training_data(self):
        """Test de la préparation des données d'entraînement."""
        data = self.loader.load_data()
        inputs, outputs = self.loader.prepare_training_data(data)
        
        self.assertEqual(len(inputs), len(outputs))
        self.assertGreater(len(inputs), 0)
        self.assertIsInstance(inputs[0], str)
        self.assertIsInstance(outputs[0], str)
        
    def test_get_context_data(self):
        """Test de l'extraction des données par contexte."""
        data = self.loader.load_data()
        contexts = ['symptome', 'diagnostic', 'traitement', 'urgence']
        
        for context in contexts:
            inputs, outputs = self.loader.get_context_data(data, context)
            self.assertEqual(len(inputs), len(outputs))
            if len(inputs) > 0:
                self.assertIsInstance(inputs[0], str)
                self.assertIsInstance(outputs[0], str)
                
    def test_get_language_data(self):
        """Test de l'extraction des données par langue."""
        data = self.loader.load_data()
        inputs, outputs = self.loader.get_language_data(data, 'fr')
        
        self.assertEqual(len(inputs), len(outputs))
        self.assertGreater(len(inputs), 0)
        self.assertIsInstance(inputs[0], str)
        self.assertIsInstance(outputs[0], str)

if __name__ == '__main__':
    unittest.main() 