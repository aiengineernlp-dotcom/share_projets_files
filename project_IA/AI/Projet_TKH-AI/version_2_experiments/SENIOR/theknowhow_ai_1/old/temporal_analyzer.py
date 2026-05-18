"""Module d'analyse temporelle pour la phase 3."""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class TemporalAnalyzer:
    """Analyseur temporel pour les données médicales."""
    
    def __init__(self):
        """Initialise l'analyseur temporel."""
        logger.info("TemporalAnalyzer initialisé")
    
    def analyze_temporal_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns temporels dans les données.
        
        Args:
            data (List[Dict[str, Any]]): Données à analyser
            
        Returns:
            Dict[str, Any]: Résultats de l'analyse temporelle
        """
        try:
            # Tri par date
            sorted_data = sorted(data, key=lambda x: x.get("created_utc", 0))
            
            # Analyse des différentes dimensions temporelles
            results = {
                "hourly_analysis": self._analyze_hourly_patterns(sorted_data),
                "daily_analysis": self._analyze_daily_patterns(sorted_data),
                "weekly_analysis": self._analyze_weekly_patterns(sorted_data),
                "trends": self._analyze_trends(sorted_data)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse temporelle: {e}")
            return {}
    
    def _analyze_hourly_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns par heure."""
        hourly_stats = defaultdict(lambda: {
            "count": 0,
            "urgent_count": 0,
            "avg_score": 0.0,
            "total_score": 0.0
        })
        
        for item in data:
            hour = datetime.fromtimestamp(item.get("created_utc", 0)).hour
            stats = hourly_stats[hour]
            
            stats["count"] += 1
            if item.get("category") == "Urgent":
                stats["urgent_count"] += 1
            stats["total_score"] += item.get("score", 0.0)
            stats["avg_score"] = stats["total_score"] / stats["count"]
        
        return {
            "hourly_distribution": dict(hourly_stats),
            "peak_hours": sorted(hourly_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:3]
        }
    
    def _analyze_daily_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns par jour."""
        daily_stats = defaultdict(lambda: {
            "count": 0,
            "urgent_count": 0,
            "avg_score": 0.0,
            "total_score": 0.0
        })
        
        for item in data:
            date = datetime.fromtimestamp(item.get("created_utc", 0)).date()
            stats = daily_stats[date]
            
            stats["count"] += 1
            if item.get("category") == "Urgent":
                stats["urgent_count"] += 1
            stats["total_score"] += item.get("score", 0.0)
            stats["avg_score"] = stats["total_score"] / stats["count"]
        
        return {
            "daily_distribution": dict(daily_stats),
            "peak_days": sorted(daily_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:3]
        }
    
    def _analyze_weekly_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns par semaine."""
        weekly_stats = defaultdict(lambda: {
            "count": 0,
            "urgent_count": 0,
            "avg_score": 0.0,
            "total_score": 0.0
        })
        
        for item in data:
            date = datetime.fromtimestamp(item.get("created_utc", 0))
            week_start = date - timedelta(days=date.weekday())
            stats = weekly_stats[week_start]
            
            stats["count"] += 1
            if item.get("category") == "Urgent":
                stats["urgent_count"] += 1
            stats["total_score"] += item.get("score", 0.0)
            stats["avg_score"] = stats["total_score"] / stats["count"]
        
        return {
            "weekly_distribution": dict(weekly_stats),
            "peak_weeks": sorted(weekly_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:3]
        }
    
    def _analyze_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les tendances temporelles."""
        if not data:
            return {}
        
        # Calcul des tendances sur différentes périodes
        trends = {
            "score_trend": self._calculate_trend([item.get("score", 0.0) for item in data]),
            "urgent_trend": self._calculate_trend([1 if item.get("category") == "Urgent" else 0 for item in data]),
            "volume_trend": self._calculate_volume_trend(data)
        }
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calcule la tendance d'une série de valeurs."""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        return slope
    
    def _calculate_volume_trend(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcule la tendance du volume de posts."""
        # Groupe les posts par jour
        daily_counts = defaultdict(int)
        for item in data:
            date = datetime.fromtimestamp(item.get("created_utc", 0)).date()
            daily_counts[date] += 1
        
        # Calcule la tendance
        dates = sorted(daily_counts.keys())
        counts = [daily_counts[date] for date in dates]
        
        if len(counts) < 2:
            return {"slope": 0.0, "intercept": 0.0}
        
        x = np.arange(len(counts))
        slope, intercept = np.polyfit(x, counts, 1)
        
        return {
            "slope": slope,
            "intercept": intercept
        } 