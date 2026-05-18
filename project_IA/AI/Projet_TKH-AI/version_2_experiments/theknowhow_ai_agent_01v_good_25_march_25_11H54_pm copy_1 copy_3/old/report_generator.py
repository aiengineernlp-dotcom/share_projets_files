"""Module de génération de rapports pour la phase 4."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging
from datetime import datetime
import json
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import os

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Générateur de rapports d'analyse médicale."""
    
    def __init__(self):
        """Initialise le générateur de rapports."""
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        logger.info("ReportGenerator initialisé")
    
    def generate_report(self, data: List[Dict[str, Any]], 
                       evaluation_results: Dict[str, Any],
                       output_dir: str):
        """Génère un rapport complet.
        
        Args:
            data (List[Dict[str, Any]]): Données à analyser
            evaluation_results (Dict[str, Any]): Résultats de l'évaluation
            output_dir (str): Répertoire de sortie
        """
        try:
            # Création du répertoire de sortie
            os.makedirs(output_dir, exist_ok=True)
            
            # Conversion en DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['created_utc'], unit='s')
            
            # Génération des graphiques
            self._generate_plots(df, output_dir)
            
            # Génération des statistiques
            stats = self._generate_statistics(df, evaluation_results)
            
            # Génération du rapport HTML
            self._generate_html_report(stats, output_dir)
            
            logger.info(f"Rapport généré dans {output_dir}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
    
    def _generate_plots(self, df: pd.DataFrame, output_dir: str):
        """Génère les graphiques pour le rapport."""
        try:
            # Distribution temporelle
            plt.figure(figsize=(12, 6))
            sns.histplot(data=df, x='date', bins=30)
            plt.title('Distribution temporelle des posts')
            plt.xlabel('Date')
            plt.ylabel('Nombre de posts')
            plt.savefig(os.path.join(output_dir, 'temporal_distribution.png'))
            plt.close()
            
            # Distribution des catégories
            plt.figure(figsize=(8, 6))
            df['category'].value_counts().plot(kind='pie', autopct='%1.1f%%')
            plt.title('Distribution des catégories')
            plt.savefig(os.path.join(output_dir, 'category_distribution.png'))
            plt.close()
            
            # Distribution des scores
            plt.figure(figsize=(10, 6))
            sns.histplot(data=df, x='score', bins=20)
            plt.title('Distribution des scores')
            plt.xlabel('Score')
            plt.ylabel('Nombre de posts')
            plt.savefig(os.path.join(output_dir, 'score_distribution.png'))
            plt.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des graphiques: {e}")
    
    def _generate_statistics(self, df: pd.DataFrame, 
                           evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les statistiques pour le rapport."""
        try:
            stats = {
                "general": {
                    "total_posts": len(df),
                    "urgent_posts": len(df[df['category'] == 'Urgent']),
                    "avg_score": df['score'].mean(),
                    "score_std": df['score'].std()
                },
                "temporal": {
                    "date_range": {
                        "start": df['date'].min().strftime('%Y-%m-%d'),
                        "end": df['date'].max().strftime('%Y-%m-%d')
                    },
                    "posts_per_day": len(df) / (df['date'].max() - df['date'].min()).days
                },
                "categories": df['category'].value_counts().to_dict(),
                "evaluation": evaluation_results
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des statistiques: {e}")
            return {}
    
    def _generate_html_report(self, stats: Dict[str, Any], output_dir: str):
        """Génère le rapport HTML."""
        try:
            # Chargement du template
            template_path = os.path.join(self.template_dir, 'report_template.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = Template(f.read())
            
            # Préparation des données pour le template
            report_data = {
                "generation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "stats": stats,
                "plots": {
                    "temporal_distribution": "temporal_distribution.png",
                    "category_distribution": "category_distribution.png",
                    "score_distribution": "score_distribution.png"
                }
            }
            
            # Génération du HTML
            html_content = template.render(**report_data)
            
            # Sauvegarde du rapport
            output_path = os.path.join(output_dir, 'report.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport HTML: {e}")
    
    def generate_summary_report(self, data: List[Dict[str, Any]], 
                              evaluation_results: Dict[str, Any],
                              output_path: str):
        """Génère un rapport sommaire en format JSON.
        
        Args:
            data (List[Dict[str, Any]]): Données à analyser
            evaluation_results (Dict[str, Any]): Résultats de l'évaluation
            output_path (str): Chemin du fichier de sortie
        """
        try:
            # Conversion en DataFrame
            df = pd.DataFrame(data)
            
            # Génération du résumé
            summary = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_posts": len(df),
                    "urgent_posts": len(df[df['category'] == 'Urgent']),
                    "avg_score": float(df['score'].mean()),
                    "model_accuracy": evaluation_results.get('classifier_metrics', {}).get('accuracy', 0),
                    "pattern_detection_rate": evaluation_results.get('pattern_metrics', {}).get('pattern_detection_rate', 0)
                },
                "evaluation_results": evaluation_results
            }
            
            # Sauvegarde du résumé
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=4)
            
            logger.info(f"Rapport sommaire généré: {output_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport sommaire: {e}")
    
    def generate_excel_report(self, data: List[Dict[str, Any]], 
                            evaluation_results: Dict[str, Any],
                            output_path: str):
        """Génère un rapport détaillé en format Excel.
        
        Args:
            data (List[Dict[str, Any]]): Données à analyser
            evaluation_results (Dict[str, Any]): Résultats de l'évaluation
            output_path (str): Chemin du fichier de sortie
        """
        try:
            # Création du writer Excel
            with pd.ExcelWriter(output_path) as writer:
                # Données brutes
                pd.DataFrame(data).to_excel(writer, sheet_name='Données brutes', index=False)
                
                # Statistiques générales
                stats_df = pd.DataFrame({
                    'Métrique': [
                        'Total des posts',
                        'Posts urgents',
                        'Score moyen',
                        'Précision du modèle',
                        'Taux de détection des patterns'
                    ],
                    'Valeur': [
                        len(data),
                        len([d for d in data if d['category'] == 'Urgent']),
                        np.mean([d['score'] for d in data]),
                        evaluation_results.get('classifier_metrics', {}).get('accuracy', 0),
                        evaluation_results.get('pattern_metrics', {}).get('pattern_detection_rate', 0)
                    ]
                })
                stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
                
                # Métriques d'évaluation
                if 'classifier_metrics' in evaluation_results:
                    pd.DataFrame([evaluation_results['classifier_metrics']]).to_excel(
                        writer, sheet_name='Métriques de classification'
                    )
                
                if 'pattern_metrics' in evaluation_results:
                    pd.DataFrame([evaluation_results['pattern_metrics']]).to_excel(
                        writer, sheet_name='Métriques des patterns'
                    )
                
                if 'temporal_metrics' in evaluation_results:
                    pd.DataFrame([evaluation_results['temporal_metrics']]).to_excel(
                        writer, sheet_name='Métriques temporelles'
                    )
            
            logger.info(f"Rapport Excel généré: {output_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport Excel: {e}") 