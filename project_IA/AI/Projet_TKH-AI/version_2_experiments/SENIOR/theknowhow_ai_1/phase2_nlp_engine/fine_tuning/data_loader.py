"""
Module de chargement des données pour l'entraînement.
"""
import logging
import sqlite3
import json
from typing import List, Tuple, Dict
from pathlib import Path
import os
import random

class TrainingDataLoader:
    """Classe pour le chargement des données d'entraînement."""
    
    def __init__(self, config_path: str = None):
        """
        Initialise le chargeur de données.
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        self.logger = logging.getLogger(__name__)
        
        # Détermination du chemin de configuration
        if config_path is None:
            config_path = Path(__file__).parent / "data_config.json"
        
        # Chargement de la configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.logger.info(f"Configuration chargée depuis {config_path}")
        
    def load_data(self) -> List[Dict]:
        """
        Charge les données depuis la base de données.
        
        Returns:
            List[Dict]: Données chargées
        """
        try:
            data = []
            db_path = Path(__file__).parent / self.config['paths']['db_path']
            
            if not db_path.exists():
                raise FileNotFoundError(f"Base de données non trouvée : {db_path}")
                
            self.logger.info(f"Chargement des données depuis {db_path}")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, subreddit, title, body, category, 
                           medical_relevance_score, urgency_score, 
                           second_opinion_score, keywords, 
                           is_medical_related, has_symptoms, 
                           has_diagnosis, has_treatment
                    FROM posts
                    WHERE is_medical_related = 1
                    ORDER BY medical_relevance_score DESC
                    LIMIT ?
                """, (self.config['data']['max_samples'],))
                rows = cursor.fetchall()
                
                for row in rows:
                    data.append({
                        "id": row[0],
                        "subreddit": row[1],
                        "text": f"{row[2]}\n{row[3]}",  # title + body
                        "category": row[4],
                        "medical_relevance_score": row[5],
                        "urgency_score": row[6],
                        "second_opinion_score": row[7],
                        "keywords": row[8].split(',') if row[8] else [],
                        "has_symptoms": bool(row[10]),
                        "has_diagnosis": bool(row[11]),
                        "has_treatment": bool(row[12])
                    })
                    
            self.logger.info(f"{len(data)} conversations chargées avec succès")
            return data
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des données : {str(e)}")
            raise
            
    def prepare_training_pairs(self, data: List[Dict]) -> List[Tuple[str, str]]:
        """
        Prépare les paires d'entraînement à partir des données.
        
        Args:
            data: Données brutes
            
        Returns:
            List[Tuple[str, str]]: Paires (input, output) pour l'entraînement
        """
        training_pairs = []
        
        for item in data:
            # Création du prompt basé sur le contexte
            context = []
            if item["has_symptoms"]:
                context.append("symptome")
            if item["has_diagnosis"]:
                context.append("diagnostic")
            if item["has_treatment"]:
                context.append("traitement")
                
            if not context:
                context = ["question"]
                
            # Construction de la paire d'entraînement
            input_text = f"Contexte: {', '.join(context)}\nQuestion: {item['text']}"
            output_text = self._generate_expected_response(item)
            
            training_pairs.append((input_text, output_text))
            
        self.logger.info(f"{len(training_pairs)} paires d'entraînement préparées")
        return training_pairs
        
    def split_data(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Divise les données en ensembles d'entraînement, de validation et de test.
        
        Args:
            data: Données à diviser
            
        Returns:
            Dict[str, List[Dict]]: Données divisées
        """
        random.shuffle(data)
        n = len(data)
        train_end = int(n * self.config['data']['train_split'])
        val_end = train_end + int(n * self.config['data']['val_split'])
        
        return {
            'train': data[:train_end],
            'val': data[train_end:val_end],
            'test': data[val_end:]
        }
        
    def _generate_expected_response(self, item: Dict) -> str:
        """
        Génère une réponse attendue basée sur les données.
        
        Args:
            item: Données d'une conversation
            
        Returns:
            str: Réponse attendue
        """
        response_parts = []
        
        # Ajout de l'empathie
        response_parts.append("Je comprends votre situation.")
        
        # Ajout d'informations basées sur le contexte
        if item["has_symptoms"]:
            response_parts.append("Vos symptômes nécessitent une attention médicale.")
        if item["has_diagnosis"]:
            response_parts.append("Un diagnostic précis nécessite une évaluation médicale approfondie.")
        if item["has_treatment"]:
            response_parts.append("Le traitement doit être adapté à votre situation spécifique.")
            
        # Ajout de recommandations
        if item["urgency_score"] > 0.5:
            response_parts.append("Je vous conseille de consulter un professionnel de santé rapidement.")
        else:
            response_parts.append("Je vous recommande de prendre rendez-vous avec votre médecin.")
            
        return " ".join(response_parts) 