"""
Configuration du système de logging pour le projet.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Configure et retourne un logger personnalisé.
    
    Args:
        name: Nom du logger
        log_level: Niveau de logging (default: logging.INFO)
    
    Returns:
        logging.Logger: Logger configuré
    """
    # Création du dossier logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)
    
    # Création du logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Format du log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour fichier avec rotation
    log_file = f"logs/{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Ajout des handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger existant ou en crée un nouveau.
    
    Args:
        name: Nom du logger
    
    Returns:
        logging.Logger: Logger existant ou nouveau
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        return setup_logger(name)
    
    return logger 