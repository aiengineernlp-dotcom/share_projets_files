"""Module de visualisation pour la phase 3."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Visualizer:
    """Visualiseur de données pour l'analyse médicale."""
    
    def __init__(self):
        """Initialise le visualiseur."""
        plt.style.use('seaborn')
        logger.info("Visualizer initialisé")
    
    def plot_temporal_distribution(self, data: List[Dict[str, Any]], save_path: str = None):
        """Visualise la distribution temporelle des posts.
        
        Args:
            data (List[Dict[str, Any]]): Données à visualiser
            save_path (str, optional): Chemin pour sauvegarder le graphique
        """
        try:
            # Conversion en DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['created_utc'], unit='s')
            
            # Création du graphique
            plt.figure(figsize=(12, 6))
            sns.histplot(data=df, x='date', bins=30)
            plt.title('Distribution temporelle des posts')
            plt.xlabel('Date')
            plt.ylabel('Nombre de posts')
            
            if save_path:
                plt.savefig(save_path)
            plt.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de la visualisation de la distribution temporelle: {e}")
    
    def plot_category_distribution(self, data: List[Dict[str, Any]], save_path: str = None):
        """Visualise la distribution des catégories.
        
        Args:
            data (List[Dict[str, Any]]): Données à visualiser
            save_path (str, optional): Chemin pour sauvegarder le graphique
        """
        try:
            # Comptage des catégories
            categories = pd.Series([item.get('category', 'Non-Urgent') for item in data]).value_counts()
            
            # Création du graphique
            plt.figure(figsize=(8, 6))
            plt.pie(categories, labels=categories.index, autopct='%1.1f%%')
            plt.title('Distribution des catégories')
            
            if save_path:
                plt.savefig(save_path)
            plt.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de la visualisation de la distribution des catégories: {e}")
    
    def plot_score_distribution(self, data: List[Dict[str, Any]], save_path: str = None):
        """Visualise la distribution des scores.
        
        Args:
            data (List[Dict[str, Any]]): Données à visualiser
            save_path (str, optional): Chemin pour sauvegarder le graphique
        """
        try:
            scores = [item.get('score', 0.0) for item in data]
            
            # Création du graphique
            plt.figure(figsize=(10, 6))
            sns.histplot(scores, bins=20)
            plt.title('Distribution des scores')
            plt.xlabel('Score')
            plt.ylabel('Nombre de posts')
            
            if save_path:
                plt.savefig(save_path)
            plt.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de la visualisation de la distribution des scores: {e}")
    
    def plot_trends(self, data: List[Dict[str, Any]], save_path: str = None):
        """Visualise les tendances temporelles.
        
        Args:
            data (List[Dict[str, Any]]): Données à visualiser
            save_path (str, optional): Chemin pour sauvegarder le graphique
        """
        try:
            # Conversion en DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['created_utc'], unit='s')
            
            # Création du graphique
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Tendance des scores
            sns.lineplot(data=df, x='date', y='score', ax=ax1)
            ax1.set_title('Tendance des scores')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Score')
            
            # Tendance des catégories urgentes
            df['is_urgent'] = df['category'] == 'Urgent'
            sns.lineplot(data=df, x='date', y='is_urgent', ax=ax2)
            ax2.set_title('Tendance des posts urgents')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Proportion de posts urgents')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path)
            plt.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de la visualisation des tendances: {e}")
    
    def plot_hourly_distribution(self, data: List[Dict[str, Any]], save_path: str = None):
        """Visualise la distribution par heure.
        
        Args:
            data (List[Dict[str, Any]]): Données à visualiser
            save_path (str, optional): Chemin pour sauvegarder le graphique
        """
        try:
            # Extraction des heures
            hours = [datetime.fromtimestamp(item.get('created_utc', 0)).hour for item in data]
            
            # Création du graphique
            plt.figure(figsize=(12, 6))
            sns.histplot(hours, bins=24)
            plt.title('Distribution par heure')
            plt.xlabel('Heure')
            plt.ylabel('Nombre de posts')
            
            if save_path:
                plt.savefig(save_path)
            plt.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de la visualisation de la distribution horaire: {e}")
    
    def generate_dashboard(self, data: List[Dict[str, Any]], output_dir: str):
        """Génère un tableau de bord complet.
        
        Args:
            data (List[Dict[str, Any]]): Données à visualiser
            output_dir (str): Répertoire de sortie pour les graphiques
        """
        try:
            # Création des différents graphiques
            self.plot_temporal_distribution(data, f"{output_dir}/temporal_distribution.png")
            self.plot_category_distribution(data, f"{output_dir}/category_distribution.png")
            self.plot_score_distribution(data, f"{output_dir}/score_distribution.png")
            self.plot_trends(data, f"{output_dir}/trends.png")
            self.plot_hourly_distribution(data, f"{output_dir}/hourly_distribution.png")
            
            logger.info(f"Tableau de bord généré dans {output_dir}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du tableau de bord: {e}") 