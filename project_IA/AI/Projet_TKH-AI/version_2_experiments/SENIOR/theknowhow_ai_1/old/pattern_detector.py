"""Module de détection de patterns pour la phase 3."""

import numpy as np
from sklearn.cluster import DBSCAN
from typing import List, Dict, Any
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class PatternDetector:
    """Détecteur de patterns dans les données médicales."""
    
    def __init__(self):
        """Initialise le détecteur de patterns."""
        self.model = DBSCAN(
            eps=0.3,
            min_samples=2,
            metric='euclidean'
        )
        logger.info("PatternDetector initialisé")
    
    def detect_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Détecte les patterns dans les données.
        
        Args:
            data (List[Dict[str, Any]]): Données à analyser
            
        Returns:
            Dict[str, Any]: Patterns détectés
        """
        try:
            # Extraction des features
            features = self._extract_features(data)
            
            # Clustering
            clusters = self.model.fit_predict(features)
            
            # Analyse des clusters
            patterns = self._analyze_clusters(data, clusters)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection des patterns: {e}")
            return {}
    
    def _extract_features(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Extrait les features des données."""
        features = []
        
        for item in data:
            feature_vector = [
                item.get("score", 0.0),
                1 if item.get("category") == "Urgent" else 0,
                len(item.get("text", "").split()),
                item.get("created_utc", 0)
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def _analyze_clusters(self, data: List[Dict[str, Any]], clusters: np.ndarray) -> Dict[str, Any]:
        """Analyse les clusters pour extraire les patterns."""
        patterns = defaultdict(list)
        
        for i, cluster_id in enumerate(clusters):
            if cluster_id != -1:  # Ignore les points de bruit
                patterns[f"cluster_{cluster_id}"].append(data[i])
        
        # Analyse des patterns
        results = {
            "clusters": len(set(clusters)) - (1 if -1 in clusters else 0),
            "patterns": {}
        }
        
        for cluster_id, items in patterns.items():
            pattern_analysis = {
                "size": len(items),
                "avg_score": np.mean([item.get("score", 0.0) for item in items]),
                "urgent_ratio": sum(1 for item in items if item.get("category") == "Urgent") / len(items),
                "common_keywords": self._extract_common_keywords(items)
            }
            results["patterns"][cluster_id] = pattern_analysis
        
        return results
    
    def _extract_common_keywords(self, items: List[Dict[str, Any]]) -> List[str]:
        """Extrait les mots-clés communs dans un cluster."""
        from collections import Counter
        
        # Concatène tous les textes
        all_text = " ".join(item.get("text", "").lower() for item in items)
        
        # Compte les mots
        words = all_text.split()
        word_counts = Counter(words)
        
        # Retourne les 5 mots les plus fréquents
        return [word for word, _ in word_counts.most_common(5)]
    
    def detect_temporal_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Détecte les patterns temporels dans les données."""
        try:
            # Tri par date
            sorted_data = sorted(data, key=lambda x: x.get("created_utc", 0))
            
            # Analyse des tendances
            trends = self._analyze_trends(sorted_data)
            
            # Analyse des périodicités
            periodicities = self._analyze_periodicities(sorted_data)
            
            return {
                "trends": trends,
                "periodicities": periodicities
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection des patterns temporels: {e}")
            return {}
    
    def _analyze_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les tendances dans les données."""
        scores = [item.get("score", 0.0) for item in data]
        categories = [item.get("category", "Non-Urgent") for item in data]
        
        return {
            "score_trend": np.mean(np.diff(scores)),
            "urgent_trend": sum(1 for cat in categories if cat == "Urgent") / len(categories)
        }
    
    def _analyze_periodicities(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les périodicités dans les données."""
        # Groupement par heure de la journée
        hourly_distribution = defaultdict(int)
        for item in data:
            hour = datetime.fromtimestamp(item.get("created_utc", 0)).hour
            hourly_distribution[hour] += 1
        
        return {
            "hourly_distribution": dict(hourly_distribution),
            "peak_hours": sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        } 