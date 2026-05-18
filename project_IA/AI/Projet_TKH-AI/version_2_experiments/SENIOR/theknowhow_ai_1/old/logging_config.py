"""
Configuration de la journalisation pour l'application.
"""

import os
import logging
import logging.handlers
from datetime import datetime

def configure_logging(log_level=logging.INFO, log_file=None):
    """
    Configure la journalisation pour l'application.
    
    Args:
        log_level (int): Niveau de journalisation (par défaut: logging.INFO).
        log_file (str): Chemin vers le fichier de journalisation (par défaut: None).
    """
    # Créer le répertoire de logs s'il n'existe pas
    if log_file is None:
        log_dir = os.path.join("data", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"medical_ai_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Configurer le formatteur
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurer le gestionnaire de fichier
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 Mo
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Configurer le gestionnaire de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurer le logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Supprimer les gestionnaires existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Ajouter les nouveaux gestionnaires
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configurer les loggers spécifiques
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('praw').setLevel(logging.WARNING)
    logging.getLogger('prawcore').setLevel(logging.WARNING)
    
    logging.info(f"Journalisation configurée avec le niveau {logging.getLevelName(log_level)}")
    logging.info(f"Les logs sont enregistrés dans {log_file}")
    
    return root_logger 