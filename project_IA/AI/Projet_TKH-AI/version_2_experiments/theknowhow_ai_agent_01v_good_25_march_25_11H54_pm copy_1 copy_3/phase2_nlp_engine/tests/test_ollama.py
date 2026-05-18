"""
Tests pour le modèle médical Ollama.
"""
import logging
import json
from pathlib import Path
from typing import Dict, List
import numpy as np

from phase2_nlp_engine.nlp_core.ollama_model import OllamaMedicalModel

class OllamaModelTester:
    """Classe pour tester les performances du modèle Ollama."""
    
    def __init__(self):
        """Initialise le testeur."""
        self.logger = logging.getLogger(__name__)
        self.model = OllamaMedicalModel()
        
    def load_test_data(self, data_path: str) -> List[Dict]:
        """
        Charge les données de test.
        
        Args:
            data_path: Chemin vers le fichier de test
            
        Returns:
            List[Dict]: Données de test
        """
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"{len(data)} échantillons chargés avec succès")
            return data
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des données: {str(e)}")
            return []
            
    def test_generation(self, test_data: List[Dict]) -> Dict:
        """
        Teste la génération de réponses.
        
        Args:
            test_data: Données de test
            
        Returns:
            Dict: Résultats des tests
        """
        results = {
            'total': len(test_data),
            'success': 0,
            'errors': 0,
            'responses': []
        }
        
        for sample in test_data:
            try:
                response = self.model.generate_response(
                    sample['text'],
                    sample.get('context')
                )
                
                results['responses'].append({
                    'input': sample['text'],
                    'output': response,
                    'context': sample.get('context')
                })
                results['success'] += 1
                
            except Exception as e:
                self.logger.error(f"Erreur lors du test: {str(e)}")
                results['errors'] += 1
                
        self.logger.info(f"Tests de génération terminés - Succès: {results['success']}/{results['total']}")
        return results
        
    def run_tests(self, data_path: str) -> Dict:
        """
        Exécute tous les tests.
        
        Args:
            data_path: Chemin vers les données de test
            
        Returns:
            Dict: Résultats complets
        """
        self.logger.info("Début de la série de tests")
        
        try:
            # Chargement des données
            test_data = self.load_test_data(data_path)
            if not test_data:
                self.logger.error("Aucune donnée de test chargée")
                return {}
                
            # Exécution des tests
            results = self.test_generation(test_data)
            
            # Sauvegarde des résultats
            output_dir = Path("phase2_nlp_engine/results")
            output_dir.mkdir(exist_ok=True)
            
            with open(output_dir / "ollama_test_results.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            self.logger.info("Tous les tests terminés avec succès")
            return results
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution des tests: {str(e)}")
            return {}
            
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Exécution des tests
    tester = OllamaModelTester()
    tester.run_tests("phase2_nlp_engine/data/test_data.json") 