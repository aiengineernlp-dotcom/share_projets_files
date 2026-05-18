"""
Script principal pour l'exécution de la phase 2 du projet.
"""
import os
import sys
from pathlib import Path

# Ajout du répertoire racine au PYTHONPATH
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.append(project_root)

import logging
import json
from typing import Dict, List

from transformers import AutoTokenizer, AutoModelForCausalLM
from phase2_nlp_engine.nlp_core.trainer import MedicalModelTrainer
from phase2_nlp_engine.fine_tuning.data_loader import TrainingDataLoader

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('phase2_nlp_engine.log')
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str = "config.json") -> Dict:
    """Charge la configuration depuis un fichier JSON."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Fichier de configuration {config_path} non trouvé")
        raise
    except json.JSONDecodeError:
        logger.error(f"Erreur de décodage JSON dans {config_path}")
        raise

def setup_directories(config: Dict):
    """Crée les répertoires nécessaires."""
    paths = config['paths']
    for path in paths.values():
        if path.endswith('.json'):
            path = os.path.dirname(path)
        os.makedirs(path, exist_ok=True)

def main():
    """Fonction principale."""
    try:
        # Chargement de la configuration
        config = load_config()
        setup_directories(config)
        
        # Chargement et transformation des données
        logger.info("Début du chargement et de la transformation des données")
        data_loader = TrainingDataLoader()
        data = data_loader.load_data()
        
        # Division des données
        logger.info("Division des données en ensembles d'entraînement, validation et test")
        split_data = data_loader.split_data(data)
        
        # Préparation des paires d'entraînement
        logger.info("Préparation des paires d'entraînement")
        training_pairs = data_loader.prepare_training_pairs(split_data['train'])
        val_pairs = data_loader.prepare_training_pairs(split_data['val'])
        test_pairs = data_loader.prepare_training_pairs(split_data['test'])
        
        # Initialisation du modèle
        model_name = config['model']['name']
        logger.info(f"Initialisation du modèle {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Initialisation du trainer
        trainer = MedicalModelTrainer(
            model_name=model_name,
            output_dir=config['paths']['model_dir']
        )
        
        # Entraînement du modèle
        logger.info("Début de l'entraînement")
        trainer.train(training_pairs)
        
        # Évaluation sur l'ensemble de test
        logger.info("Évaluation sur l'ensemble de test")
        test_results = trainer.evaluate(test_pairs)
        logger.info(f"Résultats du test : {test_results}")
        
        # Sauvegarde du modèle
        logger.info("Sauvegarde du modèle")
        trainer.save_model()
        
        logger.info("Phase 2 terminée avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la phase 2 : {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 