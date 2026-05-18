"""
Tests d'intégration pour le LLM.
"""
import unittest
import time
from typing import List, Dict
import json
from pathlib import Path
import logging

from phase2_nlp_engine.nlp_core.ollama_model import OllamaMedicalModel

class TestLLMIntegration(unittest.TestCase):
    """Tests d'intégration pour le LLM."""
    
    def setUp(self):
        """Initialisation des tests."""
        self.model = OllamaMedicalModel()
        self.test_cases = self._load_test_cases()
        
    def _load_test_cases(self) -> List[Dict]:
        """Charge les cas de test depuis un fichier JSON."""
        test_file = Path(__file__).parent / "data" / "llm_test_cases.json"
        with open(test_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def test_response_time(self):
        """Test du temps de réponse."""
        max_response_time = 5.0  # secondes
        
        for case in self.test_cases:
            start_time = time.time()
            response = self.model.generate_response(case['prompt'], case.get('context'))
            end_time = time.time()
            
            response_time = end_time - start_time
            self.assertLess(response_time, max_response_time,
                          f"Temps de réponse trop long pour le cas: {case['prompt']}")
            
    def test_response_quality(self):
        """Test de la qualité des réponses."""
        for case in self.test_cases:
            response = self.model.generate_response(case['prompt'], case.get('context'))
            
            # Vérification de la longueur de la réponse
            self.assertGreater(len(response), 10,
                             f"Réponse trop courte pour le cas: {case['prompt']}")
            
            # Vérification de la présence de mots-clés attendus
            if 'expected_keywords' in case:
                for keyword in case['expected_keywords']:
                    self.assertIn(keyword.lower(), response.lower(),
                                f"Mot-clé '{keyword}' manquant dans la réponse pour le cas: {case['prompt']}")
                    
    def test_error_handling(self):
        """Test de la gestion des erreurs."""
        # Test avec un prompt vide
        response = self.model.generate_response("")
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 0)
        
        # Test avec un prompt invalide
        response = self.model.generate_response("a" * 10000)  # Prompt très long
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 0)
        
    def test_context_handling(self):
        """Test de la gestion du contexte."""
        for case in self.test_cases:
            if 'context' in case:
                response_with_context = self.model.generate_response(case['prompt'], case['context'])
                response_without_context = self.model.generate_response(case['prompt'])
                
                # Les réponses devraient être différentes avec et sans contexte
                self.assertNotEqual(response_with_context, response_without_context,
                                  f"Le contexte n'a pas influencé la réponse pour le cas: {case['prompt']}")
                
    def test_conversation_flow(self):
        """Test du flux de conversation."""
        conversation = [
            ("Bonjour, je ne me sens pas bien.", None),
            ("J'ai de la fièvre depuis hier.", "symptome"),
            ("Est-ce que c'est grave ?", "urgence")
        ]
        
        previous_responses = []
        for prompt, context in conversation:
            response = self.model.generate_response(prompt, context)
            previous_responses.append(response)
            
            # Vérification de la cohérence de la conversation
            if previous_responses:
                # La réponse devrait faire référence aux messages précédents
                self.assertTrue(any(prev.lower() in response.lower() for prev in previous_responses),
                              f"La réponse ne fait pas référence aux messages précédents pour le cas: {prompt}")
                
if __name__ == '__main__':
    unittest.main() 