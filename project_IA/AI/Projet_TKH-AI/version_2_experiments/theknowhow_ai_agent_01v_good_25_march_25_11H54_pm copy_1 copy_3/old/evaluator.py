"""Module d'évaluation des performances pour la phase 4."""

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
from typing import List, Dict, Any, Tuple
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Évaluateur des performances des modèles."""
    
    def __init__(self):
        """Initialise l'évaluateur."""
        logger.info("ModelEvaluator initialisé")
    
    def evaluate_classifier(self, y_true: List[str], y_pred: List[str]) -> Dict[str, float]:
        """Évalue les performances du classificateur.
        
        Args:
            y_true (List[str]): Labels réels
            y_pred (List[str]): Labels prédits
            
        Returns:
            Dict[str, float]: Métriques de performance
        """
        try:
            metrics = {
                "accuracy": accuracy_score(y_true, y_pred),
                "precision": precision_score(y_true, y_pred, pos_label="Urgent"),
                "recall": recall_score(y_true, y_pred, pos_label="Urgent"),
                "f1": f1_score(y_true, y_pred, pos_label="Urgent")
            }
            
            # Matrice de confusion
            cm = confusion_matrix(y_true, y_pred)
            metrics["confusion_matrix"] = cm.tolist()
            
            # Rapport de classification détaillé
            report = classification_report(y_true, y_pred, output_dict=True)
            metrics["classification_report"] = report
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation du classificateur: {e}")
            return {}
    
    def evaluate_pattern_detection(self, true_patterns: List[Dict[str, Any]], 
                                 detected_patterns: List[Dict[str, Any]]) -> Dict[str, float]:
        """Évalue la détection de patterns.
        
        Args:
            true_patterns (List[Dict[str, Any]]): Patterns réels
            detected_patterns (List[Dict[str, Any]]): Patterns détectés
            
        Returns:
            Dict[str, Any]: Métriques de performance
        """
        try:
            # Calcul de la similarité entre les patterns
            similarity_scores = []
            for true_pattern in true_patterns:
                max_similarity = 0
                for detected_pattern in detected_patterns:
                    similarity = self._calculate_pattern_similarity(true_pattern, detected_pattern)
                    max_similarity = max(max_similarity, similarity)
                similarity_scores.append(max_similarity)
            
            metrics = {
                "average_similarity": np.mean(similarity_scores),
                "pattern_detection_rate": len(detected_patterns) / len(true_patterns) if true_patterns else 0,
                "similarity_scores": similarity_scores
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de la détection de patterns: {e}")
            return {}
    
    def _calculate_pattern_similarity(self, pattern1: Dict[str, Any], 
                                   pattern2: Dict[str, Any]) -> float:
        """Calcule la similarité entre deux patterns."""
        try:
            # Comparaison des attributs communs
            common_attributes = set(pattern1.keys()) & set(pattern2.keys())
            if not common_attributes:
                return 0.0
            
            similarities = []
            for attr in common_attributes:
                if isinstance(pattern1[attr], (int, float)) and isinstance(pattern2[attr], (int, float)):
                    # Similarité pour les valeurs numériques
                    max_val = max(pattern1[attr], pattern2[attr])
                    if max_val > 0:
                        similarities.append(1 - abs(pattern1[attr] - pattern2[attr]) / max_val)
                elif isinstance(pattern1[attr], list) and isinstance(pattern2[attr], list):
                    # Similarité pour les listes (ex: mots-clés)
                    common_elements = set(pattern1[attr]) & set(pattern2[attr])
                    if pattern1[attr] or pattern2[attr]:
                        similarities.append(len(common_elements) / max(len(pattern1[attr]), len(pattern2[attr])))
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la similarité des patterns: {e}")
            return 0.0
    
    def evaluate_temporal_analysis(self, true_trends: Dict[str, Any], 
                                 predicted_trends: Dict[str, Any]) -> Dict[str, float]:
        """Évalue l'analyse temporelle.
        
        Args:
            true_trends (Dict[str, Any]): Tendances réelles
            predicted_trends (Dict[str, Any]): Tendances prédites
            
        Returns:
            Dict[str, float]: Métriques de performance
        """
        try:
            metrics = {}
            
            # Évaluation des tendances
            for trend_type in ["score_trend", "urgent_trend", "volume_trend"]:
                if trend_type in true_trends and trend_type in predicted_trends:
                    true_value = true_trends[trend_type]
                    pred_value = predicted_trends[trend_type]
                    
                    if isinstance(true_value, (int, float)) and isinstance(pred_value, (int, float)):
                        metrics[f"{trend_type}_error"] = abs(true_value - pred_value)
                        metrics[f"{trend_type}_relative_error"] = (
                            abs(true_value - pred_value) / abs(true_value) if true_value != 0 else 0
                        )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de l'analyse temporelle: {e}")
            return {}
    
    def generate_evaluation_report(self, results: Dict[str, Any], output_path: str):
        """Génère un rapport d'évaluation complet.
        
        Args:
            results (Dict[str, Any]): Résultats de l'évaluation
            output_path (str): Chemin pour sauvegarder le rapport
        """
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "summary": self._generate_summary(results)
            }
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=4)
            
            logger.info(f"Rapport d'évaluation généré: {output_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport d'évaluation: {e}")
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un résumé des résultats d'évaluation."""
        summary = {}
        
        # Résumé des métriques de classification
        if "classifier_metrics" in results:
            metrics = results["classifier_metrics"]
            summary["classification"] = {
                "accuracy": metrics.get("accuracy", 0),
                "f1_score": metrics.get("f1", 0)
            }
        
        # Résumé de la détection de patterns
        if "pattern_metrics" in results:
            metrics = results["pattern_metrics"]
            summary["pattern_detection"] = {
                "average_similarity": metrics.get("average_similarity", 0),
                "detection_rate": metrics.get("pattern_detection_rate", 0)
            }
        
        # Résumé de l'analyse temporelle
        if "temporal_metrics" in results:
            metrics = results["temporal_metrics"]
            summary["temporal_analysis"] = {
                "average_error": np.mean([v for k, v in metrics.items() if k.endswith("_error")]),
                "average_relative_error": np.mean([v for k, v in metrics.items() if k.endswith("_relative_error")])
            }
        
        return summary 