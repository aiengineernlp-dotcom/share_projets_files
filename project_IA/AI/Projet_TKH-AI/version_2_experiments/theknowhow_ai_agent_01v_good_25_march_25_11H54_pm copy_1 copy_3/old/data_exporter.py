"""Module d'exportation des données pour la phase 4."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging
from datetime import datetime
import json
import csv
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class DataExporter:
    """Exportateur de données pour l'analyse médicale."""
    
    def __init__(self):
        """Initialise l'exportateur de données."""
        logger.info("DataExporter initialisé")
    
    def export_to_csv(self, data: List[Dict[str, Any]], output_path: str):
        """Exporte les données au format CSV.
        
        Args:
            data (List[Dict[str, Any]]): Données à exporter
            output_path (str): Chemin du fichier de sortie
        """
        try:
            # Conversion en DataFrame
            df = pd.DataFrame(data)
            
            # Ajout de la colonne date si nécessaire
            if 'created_utc' in df.columns:
                df['date'] = pd.to_datetime(df['created_utc'], unit='s')
            
            # Export en CSV
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Données exportées en CSV: {output_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export CSV: {e}")
    
    def export_to_excel(self, data: List[Dict[str, Any]], output_path: str):
        """Exporte les données au format Excel.
        
        Args:
            data (List[Dict[str, Any]]): Données à exporter
            output_path (str): Chemin du fichier de sortie
        """
        try:
            # Conversion en DataFrame
            df = pd.DataFrame(data)
            
            # Ajout de la colonne date si nécessaire
            if 'created_utc' in df.columns:
                df['date'] = pd.to_datetime(df['created_utc'], unit='s')
            
            # Export en Excel
            df.to_excel(output_path, index=False)
            logger.info(f"Données exportées en Excel: {output_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export Excel: {e}")
    
    def export_to_json(self, data: List[Dict[str, Any]], output_path: str):
        """Exporte les données au format JSON.
        
        Args:
            data (List[Dict[str, Any]]): Données à exporter
            output_path (str): Chemin du fichier de sortie
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Données exportées en JSON: {output_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export JSON: {e}")
    
    def export_aggregated_data(self, data: List[Dict[str, Any]], output_dir: str):
        """Exporte les données agrégées dans différents formats.
        
        Args:
            data (List[Dict[str, Any]]): Données à exporter
            output_dir (str): Répertoire de sortie
        """
        try:
            # Création du répertoire de sortie
            os.makedirs(output_dir, exist_ok=True)
            
            # Conversion en DataFrame
            df = pd.DataFrame(data)
            
            # Agrégation par date
            daily_stats = df.groupby(pd.to_datetime(df['created_utc'], unit='s').dt.date).agg({
                'score': ['count', 'mean', 'std'],
                'category': lambda x: (x == 'Urgent').mean()
            }).round(2)
            
            # Agrégation par catégorie
            category_stats = df.groupby('category').agg({
                'score': ['count', 'mean', 'std']
            }).round(2)
            
            # Export des statistiques agrégées
            daily_stats.to_csv(os.path.join(output_dir, 'daily_stats.csv'))
            category_stats.to_csv(os.path.join(output_dir, 'category_stats.csv'))
            
            # Export des données brutes dans différents formats
            self.export_to_csv(data, os.path.join(output_dir, 'raw_data.csv'))
            self.export_to_excel(data, os.path.join(output_dir, 'raw_data.xlsx'))
            self.export_to_json(data, os.path.join(output_dir, 'raw_data.json'))
            
            logger.info(f"Données agrégées exportées dans {output_dir}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export des données agrégées: {e}")
    
    def export_evaluation_results(self, evaluation_results: Dict[str, Any], output_dir: str):
        """Exporte les résultats d'évaluation.
        
        Args:
            evaluation_results (Dict[str, Any]): Résultats à exporter
            output_dir (str): Répertoire de sortie
        """
        try:
            # Création du répertoire de sortie
            os.makedirs(output_dir, exist_ok=True)
            
            # Export en JSON
            output_path = os.path.join(output_dir, 'evaluation_results.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(evaluation_results, f, indent=4, ensure_ascii=False)
            
            # Export en CSV pour les métriques principales
            metrics_data = []
            
            # Métriques de classification
            if 'classifier_metrics' in evaluation_results:
                metrics_data.append({
                    'type': 'classification',
                    'metric': 'accuracy',
                    'value': evaluation_results['classifier_metrics'].get('accuracy', 0)
                })
                metrics_data.append({
                    'type': 'classification',
                    'metric': 'precision',
                    'value': evaluation_results['classifier_metrics'].get('precision', 0)
                })
                metrics_data.append({
                    'type': 'classification',
                    'metric': 'recall',
                    'value': evaluation_results['classifier_metrics'].get('recall', 0)
                })
                metrics_data.append({
                    'type': 'classification',
                    'metric': 'f1',
                    'value': evaluation_results['classifier_metrics'].get('f1', 0)
                })
            
            # Métriques de détection de patterns
            if 'pattern_metrics' in evaluation_results:
                metrics_data.append({
                    'type': 'pattern',
                    'metric': 'average_similarity',
                    'value': evaluation_results['pattern_metrics'].get('average_similarity', 0)
                })
                metrics_data.append({
                    'type': 'pattern',
                    'metric': 'detection_rate',
                    'value': evaluation_results['pattern_metrics'].get('pattern_detection_rate', 0)
                })
            
            # Export des métriques en CSV
            metrics_df = pd.DataFrame(metrics_data)
            metrics_df.to_csv(os.path.join(output_dir, 'metrics.csv'), index=False)
            
            logger.info(f"Résultats d'évaluation exportés dans {output_dir}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export des résultats d'évaluation: {e}")
    
    def export_visualization_data(self, data: List[Dict[str, Any]], output_dir: str):
        """Exporte les données pour la visualisation.
        
        Args:
            data (List[Dict[str, Any]]): Données à exporter
            output_dir (str): Répertoire de sortie
        """
        try:
            # Création du répertoire de sortie
            os.makedirs(output_dir, exist_ok=True)
            
            # Conversion en DataFrame
            df = pd.DataFrame(data)
            
            # Préparation des données pour la visualisation
            viz_data = {
                "temporal": {
                    "dates": df['created_utc'].tolist(),
                    "scores": df['score'].tolist(),
                    "categories": df['category'].tolist()
                },
                "categories": df['category'].value_counts().to_dict(),
                "scores": {
                    "values": df['score'].tolist(),
                    "bins": np.histogram(df['score'], bins=20)[0].tolist()
                }
            }
            
            # Export des données de visualisation
            output_path = os.path.join(output_dir, 'visualization_data.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(viz_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Données de visualisation exportées dans {output_dir}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export des données de visualisation: {e}")
    
    def create_export_package(self, data: List[Dict[str, Any]], 
                            evaluation_results: Dict[str, Any],
                            output_dir: str):
        """Crée un package complet d'export.
        
        Args:
            data (List[Dict[str, Any]]): Données à exporter
            evaluation_results (Dict[str, Any]): Résultats d'évaluation
            output_dir (str): Répertoire de sortie
        """
        try:
            # Création du répertoire de sortie
            os.makedirs(output_dir, exist_ok=True)
            
            # Création des sous-répertoires
            subdirs = ['raw_data', 'aggregated_data', 'evaluation', 'visualization']
            for subdir in subdirs:
                os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)
            
            # Export des données brutes
            self.export_to_csv(data, os.path.join(output_dir, 'raw_data', 'data.csv'))
            self.export_to_excel(data, os.path.join(output_dir, 'raw_data', 'data.xlsx'))
            self.export_to_json(data, os.path.join(output_dir, 'raw_data', 'data.json'))
            
            # Export des données agrégées
            self.export_aggregated_data(data, os.path.join(output_dir, 'aggregated_data'))
            
            # Export des résultats d'évaluation
            self.export_evaluation_results(evaluation_results, os.path.join(output_dir, 'evaluation'))
            
            # Export des données de visualisation
            self.export_visualization_data(data, os.path.join(output_dir, 'visualization'))
            
            # Création d'un fichier README
            self._create_readme(output_dir)
            
            logger.info(f"Package d'export créé dans {output_dir}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du package d'export: {e}")
    
    def _create_readme(self, output_dir: str):
        """Crée un fichier README pour le package d'export."""
        try:
            readme_content = """# Package d'export d'analyse médicale

Ce package contient les données et résultats de l'analyse médicale.

## Structure du package

- `raw_data/`: Données brutes dans différents formats
  - `data.csv`: Données au format CSV
  - `data.xlsx`: Données au format Excel
  - `data.json`: Données au format JSON

- `aggregated_data/`: Données agrégées et statistiques
  - `daily_stats.csv`: Statistiques quotidiennes
  - `category_stats.csv`: Statistiques par catégorie
  - `raw_data.*`: Données brutes dans différents formats

- `evaluation/`: Résultats de l'évaluation
  - `evaluation_results.json`: Résultats complets
  - `metrics.csv`: Métriques principales

- `visualization/`: Données pour la visualisation
  - `visualization_data.json`: Données préparées pour la visualisation

## Date de génération
{date}

## Notes
Ce package a été généré automatiquement par le système d'analyse médicale.
""".format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            with open(os.path.join(output_dir, 'README.md'), 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du README: {e}") 