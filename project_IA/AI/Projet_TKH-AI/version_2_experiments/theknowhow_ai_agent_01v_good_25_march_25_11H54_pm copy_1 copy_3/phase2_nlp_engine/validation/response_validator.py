"""
Module de validation des réponses du modèle médical.
"""
import logging
from typing import Dict, List, Optional
import re
from pathlib import Path

class ResponseValidator:
    """Classe pour la validation des réponses du modèle."""
    
    def __init__(self):
        """Initialise le validateur de réponses."""
        self.logger = logging.getLogger(__name__)
        
        # Patterns de validation médicale
        self.medical_patterns = {
            'symptomes': r'(douleur|fièvre|fatigue|nausée|vertige|malaise)',
            'diagnostic': r'(diagnostic|maladie|pathologie|trouble)',
            'traitement': r'(médicament|traitement|thérapie|prescription)',
            'urgence': r'(urgence|grave|danger|immédiat)'
        }
        
        # Seuils de validation
        self.thresholds = {
            'min_length': 20,
            'max_length': 500,
            'min_medical_terms': 2,
            'min_coherence': 0.7
        }
        
    def validate_response(self, 
                         input_text: str, 
                         response: str, 
                         context: Optional[Dict] = None) -> Dict:
        """
        Valide une réponse générée.
        
        Args:
            input_text (str): Texte d'entrée
            response (str): Réponse à valider
            context (Optional[Dict]): Contexte supplémentaire
            
        Returns:
            Dict: Résultats de la validation
        """
        try:
            results = {
                'valid': True,
                'scores': {},
                'warnings': [],
                'errors': []
            }
            
            # Validation de la longueur
            length_score = self._validate_length(response)
            results['scores']['length'] = length_score
            
            if length_score < 0.5:
                results['warnings'].append("Longueur de réponse non optimale")
                
            # Validation du contenu médical
            medical_score = self._validate_medical_content(response)
            results['scores']['medical_content'] = medical_score
            
            if medical_score < self.thresholds['min_coherence']:
                results['warnings'].append("Contenu médical insuffisant")
                
            # Validation de la cohérence
            coherence_score = self._validate_coherence(input_text, response)
            results['scores']['coherence'] = coherence_score
            
            if coherence_score < self.thresholds['min_coherence']:
                results['warnings'].append("Cohérence insuffisante avec la question")
                
            # Validation de la sécurité
            safety_score = self._validate_safety(response)
            results['scores']['safety'] = safety_score
            
            if safety_score < 1.0:
                results['errors'].append("Contenu potentiellement dangereux détecté")
                results['valid'] = False
                
            # Score global
            results['scores']['global'] = self._calculate_global_score(results['scores'])
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la validation: {str(e)}")
            return {
                'valid': False,
                'scores': {},
                'warnings': [],
                'errors': [str(e)]
            }
            
    def _validate_length(self, response: str) -> float:
        """
        Valide la longueur de la réponse.
        
        Args:
            response (str): Réponse à valider
            
        Returns:
            float: Score de longueur
        """
        length = len(response.split())
        
        if length < self.thresholds['min_length']:
            return length / self.thresholds['min_length']
        elif length > self.thresholds['max_length']:
            return self.thresholds['max_length'] / length
        else:
            return 1.0
            
    def _validate_medical_content(self, response: str) -> float:
        """
        Valide le contenu médical de la réponse.
        
        Args:
            response (str): Réponse à valider
            
        Returns:
            float: Score de contenu médical
        """
        medical_terms = 0
        
        for pattern in self.medical_patterns.values():
            matches = re.findall(pattern, response, re.IGNORECASE)
            medical_terms += len(matches)
            
        return min(1.0, medical_terms / self.thresholds['min_medical_terms'])
        
    def _validate_coherence(self, input_text: str, response: str) -> float:
        """
        Valide la cohérence entre la question et la réponse.
        
        Args:
            input_text (str): Texte d'entrée
            response (str): Réponse à valider
            
        Returns:
            float: Score de cohérence
        """
        # Mots clés de la question
        input_words = set(input_text.lower().split())
        response_words = set(response.lower().split())
        
        # Score basé sur le chevauchement des mots
        common_words = input_words.intersection(response_words)
        if not input_words:
            return 0.0
            
        return len(common_words) / len(input_words)
        
    def _validate_safety(self, response: str) -> float:
        """
        Valide la sécurité de la réponse.
        
        Args:
            response (str): Réponse à valider
            
        Returns:
            float: Score de sécurité
        """
        # Patterns de contenu dangereux
        unsafe_patterns = [
            r'(mourir|mort|suicide)',
            r'(overdose|surdose)',
            r'(dangereux|nocif|toxique)',
            # Ajouter d'autres patterns selon les besoins
        ]
        
        # Vérification des patterns dangereux
        for pattern in unsafe_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return 0.0
                
        return 1.0
        
    def _calculate_global_score(self, scores: Dict[str, float]) -> float:
        """
        Calcule le score global de la validation.
        
        Args:
            scores (Dict[str, float]): Scores individuels
            
        Returns:
            float: Score global
        """
        weights = {
            'length': 0.1,
            'medical_content': 0.3,
            'coherence': 0.3,
            'safety': 0.3
        }
        
        return sum(score * weights[metric] 
                  for metric, score in scores.items() 
                  if metric in weights)
                  
    def get_validation_report(self, results: Dict) -> str:
        """
        Génère un rapport de validation formaté.
        
        Args:
            results (Dict): Résultats de la validation
            
        Returns:
            str: Rapport formaté
        """
        report = ["=== Rapport de Validation ===\n"]
        
        # Statut global
        status = "VALIDÉ" if results['valid'] else "NON VALIDÉ"
        report.append(f"Statut: {status}")
        
        # Scores
        if results['scores']:
            report.append("\nScores:")
            for metric, score in results['scores'].items():
                report.append(f"- {metric}: {score:.2f}")
                
        # Avertissements
        if results['warnings']:
            report.append("\nAvertissements:")
            for warning in results['warnings']:
                report.append(f"- {warning}")
                
        # Erreurs
        if results['errors']:
            report.append("\nErreurs:")
            for error in results['errors']:
                report.append(f"- {error}")
                
        return "\n".join(report) 