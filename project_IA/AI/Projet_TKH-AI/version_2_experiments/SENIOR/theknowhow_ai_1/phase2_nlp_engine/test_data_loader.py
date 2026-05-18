"""
Script de test pour le data_loader.
"""
import sys
from pathlib import Path
import logging
import json

# Ajout du répertoire parent au PYTHONPATH
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from phase2_nlp_engine.fine_tuning.data_loader import TrainingDataLoader
from phase2_nlp_engine.nlp_core.trainer import MedicalModelTrainer as ModelTrainer
from phase2_nlp_engine.config import load_config

def main():
    """Fonction principale du test."""
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Début des tests du data_loader")
        
        # Chargement de la configuration
        config = load_config()
        
        # Initialisation du data loader
        data_loader = TrainingDataLoader(config)
        
        # Chargement des données
        conversations = data_loader.load_data()
        
        # Affichage des statistiques
        logger.info(f"Nombre total de conversations : {len(conversations)}")
        
        # Répartition par langue
        logger.info("Répartition par langue :")
        lang_counts = {}
        for conv in conversations:
            lang = conv['language']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        for lang, count in lang_counts.items():
            logger.info(f"- {lang}: {count}")
        
        # Répartition par source
        logger.info("Répartition par source :")
        source_counts = {}
        for conv in conversations:
            source = conv['source']
            source_counts[source] = source_counts.get(source, 0) + 1
        for source, count in source_counts.items():
            logger.info(f"- {source}: {count}")
        
        # Préparation des données d'entraînement
        training_pairs = data_loader.prepare_training_pairs(conversations)
        logger.info(f"Données préparées pour l'entraînement : {len(training_pairs)} paires")
        
        # Test des données par langue
        for lang in ['fr', 'en', 'ar']:
            lang_pairs = data_loader.get_language_data(conversations, lang)
            logger.info(f"Données pour la langue {lang}: {len(lang_pairs)} paires")
        
        logger.info("Tests terminés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors du test : {str(e)}")
        logger.error("Tests terminés avec des erreurs")
        raise

if __name__ == "__main__":
    main() 