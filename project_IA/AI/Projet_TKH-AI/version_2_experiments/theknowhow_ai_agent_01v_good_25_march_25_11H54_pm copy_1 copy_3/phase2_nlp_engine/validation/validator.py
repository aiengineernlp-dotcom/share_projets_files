"""
Module de validation pour le système NLP.
"""
import logging
from typing import Dict, List, Optional
import re
from pathlib import Path

class Validator:
    """Classe pour la validation des réponses et des modèles."""
    
    def __init__(self):
        """Initialise le validateur."""
        self.logger = logging.getLogger(__name__)
        
    def validate_response(self, 
                         input_text: str, 
                         response: str, 
                         context: Optional[Dict] = None) -> Dict[str, float]:
        """
        Valide une réponse générée.
        
        Args:
            input_text (str): Texte d'entrée
            response (str): Réponse générée
            context (Optional[Dict]): Contexte supplémentaire
            
        Returns:
            Dict[str, float]: Scores de validation
        """
        try:
            scores = {
                'coherence_score': self._check_coherence(response),
                'relevance_score': self._check_relevance(input_text, response),
                'safety_score': self._check_safety(response),
                'completeness_score': self._check_completeness(response)
            }
            
            return scores
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la validation de la réponse: {str(e)}")
            return {
                'coherence_score': 0.0,
                'relevance_score': 0.0,
                'safety_score': 0.0,
                'completeness_score': 0.0
            }
            
    def _check_coherence(self, text: str) -> float:
        """
        Vérifie la cohérence du texte.
        
        Args:
            text (str): Texte à vérifier
            
        Returns:
            float: Score de cohérence
        """
        try:
            # Vérification de la structure des phrases
            sentences = re.split(r'[.!?]+', text)
            if not sentences:
                return 0.0
                
            # Score basé sur la longueur moyenne des phrases
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            length_score = min(1.0, avg_length / 20.0)  # Normalisation
            
            # Score basé sur la ponctuation
            punctuation_score = len(re.findall(r'[.!?,;]', text)) / len(text)
            punctuation_score = min(1.0, punctuation_score * 10)
            
            return (length_score + punctuation_score) / 2
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de cohérence: {str(e)}")
            return 0.0
            
    def _check_relevance(self, input_text: str, response: str) -> float:
        """
        Vérifie la pertinence de la réponse par rapport à l'entrée.
        
        Args:
            input_text (str): Texte d'entrée
            response (str): Réponse à vérifier
            
        Returns:
            float: Score de pertinence
        """
        try:
            # Mots clés de l'entrée
            input_words = set(input_text.lower().split())
            response_words = set(response.lower().split())
            
            # Score basé sur le chevauchement des mots
            common_words = input_words.intersection(response_words)
            if not input_words:
                return 0.0
                
            overlap_score = len(common_words) / len(input_words)
            
            # Score basé sur la longueur relative
            length_ratio = len(response.split()) / len(input_text.split())
            length_score = min(1.0, length_ratio if length_ratio <= 1.0 else 1/length_ratio)
            
            return (overlap_score + length_score) / 2
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de pertinence: {str(e)}")
            return 0.0
            
    def _check_safety(self, text: str) -> float:
        """
        Vérifie la sécurité du texte.
        
        Args:
            text (str): Texte à vérifier
            
        Returns:
            float: Score de sécurité
        """
        try:
            # Liste de mots/expressions à éviter
            unsafe_patterns = [
                r'mot_sensible_1',
                r'mot_sensible_2',
                # Ajouter d'autres patterns selon les besoins
            ]
            
            # Score basé sur l'absence de contenu sensible
            text_lower = text.lower()
            matches = sum(1 for pattern in unsafe_patterns if re.search(pattern, text_lower))
            
            return 1.0 - (matches / len(unsafe_patterns))
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de sécurité: {str(e)}")
            return 0.0
            
    def _check_completeness(self, text: str) -> float:
        """
        Vérifie si la réponse est complète.
        
        Args:
            text (str): Texte à vérifier
            
        Returns:
            float: Score de complétude
        """
        try:
            # Vérification de la longueur minimale
            if len(text.split()) < 5:
                return 0.0
                
            # Score basé sur la présence de phrases complètes
            sentences = re.split(r'[.!?]+', text)
            complete_sentences = sum(1 for s in sentences if len(s.split()) >= 3)
            
            if not sentences:
                return 0.0
                
            completeness_score = complete_sentences / len(sentences)
            
            # Score basé sur la ponctuation finale
            ends_properly = text.strip().endswith(('.', '!', '?'))
            final_score = (completeness_score + (1.0 if ends_properly else 0.0)) / 2
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de complétude: {str(e)}")
            return 0.0
            
    def validate_model(self, model_path: str) -> Dict[str, bool]:
        """
        Valide un modèle sauvegardé.
        
        Args:
            model_path (str): Chemin vers le modèle
            
        Returns:
            Dict[str, bool]: Résultats de validation
        """
        try:
            model_dir = Path(model_path)
            
            # Vérification de l'existence des fichiers requis
            required_files = [
                'config.json',
                'pytorch_model.bin',
                'tokenizer.json'
            ]
            
            validation_results = {
                'model_exists': model_dir.exists(),
                'has_config': (model_dir / 'config.json').exists(),
                'has_weights': (model_dir / 'pytorch_model.bin').exists(),
                'has_tokenizer': (model_dir / 'tokenizer.json').exists()
            }
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la validation du modèle: {str(e)}")
            return {
                'model_exists': False,
                'has_config': False,
                'has_weights': False,
                'has_tokenizer': False
            } 