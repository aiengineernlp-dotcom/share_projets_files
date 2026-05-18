"""
Script de test pour évaluer les performances du modèle médical.
"""
import logging
import json
from typing import Dict, List
import numpy as np
from pathlib import Path
import sys

from phase2_nlp_engine.nlp_core.medical_model import MedicalNLPModel
from phase2_nlp_engine.nlp_core.trainer import MedicalModelTrainer

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_results.log')
    ]
)

class ModelTester:
    """Classe pour tester les performances du modèle."""
    
    def __init__(self, model_name: str = "microsoft/BioGPT-large"):
        """
        Initialise le testeur.
        
        Args:
            model_name: Nom du modèle à tester
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialisation du testeur avec le modèle {model_name}")
        
        try:
            self.model = MedicalNLPModel(model_name)
            self.trainer = MedicalModelTrainer(model_name, "models/test")
            self.logger.info("Modèle et trainer initialisés avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation: {str(e)}")
            raise
            
    def load_test_data(self, data_path: str) -> List[Dict]:
        """
        Charge les données de test.
        
        Args:
            data_path: Chemin vers les données de test
            
        Returns:
            List[Dict]: Données de test
        """
        try:
            self.logger.info(f"Chargement des données de test depuis {data_path}")
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"{len(data)} échantillons chargés avec succès")
            return data
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des données: {str(e)}")
            return []
            
    def test_detection(self, test_data: List[Dict]) -> Dict:
        """
        Teste la détection de contexte médical.
        
        Args:
            test_data: Données de test
            
        Returns:
            Dict: Résultats des tests
        """
        self.logger.info("Début des tests de détection")
        results = {
            'total': len(test_data),
            'correct': 0,
            'incorrect': 0,
            'by_context': {}
        }
        
        for i, item in enumerate(test_data, 1):
            text = item['text']
            expected_context = item['context']
            
            try:
                # Analyse du texte
                analysis = self.model.analyze_medical_text(text)
                detected_context = analysis['context']
                
                # Mise à jour des résultats
                if detected_context == expected_context:
                    results['correct'] += 1
                    self.logger.debug(f"Test {i}/{len(test_data)}: Détection correcte ({expected_context})")
                else:
                    results['incorrect'] += 1
                    self.logger.debug(f"Test {i}/{len(test_data)}: Détection incorrecte (attendu: {expected_context}, obtenu: {detected_context})")
                    
                # Statistiques par contexte
                if expected_context not in results['by_context']:
                    results['by_context'][expected_context] = {'total': 0, 'correct': 0}
                results['by_context'][expected_context]['total'] += 1
                if detected_context == expected_context:
                    results['by_context'][expected_context]['correct'] += 1
                    
            except Exception as e:
                self.logger.error(f"Erreur lors du test {i}: {str(e)}")
                continue
                
        # Calcul des pourcentages
        results['accuracy'] = results['correct'] / results['total'] * 100
        for context in results['by_context']:
            total = results['by_context'][context]['total']
            correct = results['by_context'][context]['correct']
            results['by_context'][context]['accuracy'] = correct / total * 100
            
        self.logger.info(f"Tests de détection terminés - Précision globale: {results['accuracy']:.2f}%")
        return results
        
    def test_generation(self, test_data: List[Dict]) -> Dict:
        """
        Teste la génération de réponses.
        
        Args:
            test_data: Données de test
            
        Returns:
            Dict: Résultats des tests
        """
        self.logger.info("Début des tests de génération")
        results = {
            'total': len(test_data),
            'by_context': {}
        }
        
        for i, item in enumerate(test_data, 1):
            text = item['text']
            context = item['context']
            
            try:
                # Génération de la réponse
                response = self.model.generate_medical_response(text, context)
                
                # Évaluation de la réponse
                if context not in results['by_context']:
                    results['by_context'][context] = {
                        'total': 0,
                        'length': [],
                        'templates_used': {}
                    }
                results['by_context'][context]['total'] += 1
                results['by_context'][context]['length'].append(len(response.split()))
                
                # Suivi des templates utilisés
                template = self._identify_template(response, context)
                if template not in results['by_context'][context]['templates_used']:
                    results['by_context'][context]['templates_used'][template] = 0
                results['by_context'][context]['templates_used'][template] += 1
                
                self.logger.debug(f"Test {i}/{len(test_data)}: Réponse générée pour le contexte {context}")
                
            except Exception as e:
                self.logger.error(f"Erreur lors du test {i}: {str(e)}")
                continue
                
        # Calcul des statistiques
        for context in results['by_context']:
            lengths = results['by_context'][context]['length']
            results['by_context'][context]['avg_length'] = np.mean(lengths)
            results['by_context'][context]['std_length'] = np.std(lengths)
            
        self.logger.info("Tests de génération terminés")
        return results
        
    def _identify_template(self, response: str, context: str) -> str:
        """
        Identifie le template utilisé pour une réponse.
        
        Args:
            response: Réponse générée
            context: Contexte de la réponse
            
        Returns:
            str: Template identifié
        """
        try:
            templates = self.model.response_templates[context]
            for i, template in enumerate(templates):
                if response.startswith(template.split()[0]):
                    return f"template_{i}"
            return "unknown"
        except Exception as e:
            self.logger.error(f"Erreur lors de l'identification du template: {str(e)}")
            return "error"
        
    def run_tests(self, data_path: str) -> Dict:
        """
        Exécute tous les tests.
        
        Args:
            data_path: Chemin vers les données de test
            
        Returns:
            Dict: Résultats complets des tests
        """
        self.logger.info("Début de la série de tests")
        
        try:
            # Chargement des données
            test_data = self.load_test_data(data_path)
            if not test_data:
                self.logger.error("Aucune donnée de test chargée")
                return {}
                
            # Exécution des tests
            detection_results = self.test_detection(test_data)
            generation_results = self.test_generation(test_data)
            
            # Compilation des résultats
            results = {
                'detection': detection_results,
                'generation': generation_results,
                'summary': {
                    'detection_accuracy': detection_results['accuracy'],
                    'avg_response_length': np.mean([
                        np.mean(context['length'])
                        for context in generation_results['by_context'].values()
                        if 'length' in context
                    ])
                }
            }
            
            self.logger.info("Tous les tests terminés avec succès")
            return results
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution des tests: {str(e)}")
            return {}
        
    def save_results(self, results: Dict, output_path: str) -> None:
        """
        Sauvegarde les résultats des tests.
        
        Args:
            results: Résultats à sauvegarder
            output_path: Chemin de sortie
        """
        try:
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            
            with open(output_path / "test_results.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Résultats sauvegardés dans {output_path}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des résultats: {str(e)}")
            
if __name__ == "__main__":
    try:
        # Création du testeur
        tester = ModelTester()
        
        # Exécution des tests
        results = tester.run_tests("phase2_nlp_engine/data/test_data.json")
        
        # Sauvegarde des résultats
        if results:
            tester.save_results(results, "phase2_nlp_engine/results")
        else:
            logging.error("Aucun résultat à sauvegarder")
            
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution du script: {str(e)}")
        sys.exit(1) 