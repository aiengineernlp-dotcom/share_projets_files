"""
Système de logging.
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 1901-1950 : utilitaires de logging)
"""

import logging
import sys
from typing import Optional
from pathlib import Path
from datetime import datetime

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Configure un logger avec les paramètres spécifiés.
    
    Args:
        name (str): Nom du logger
        level (int): Niveau de logging
        log_file (Optional[str]): Chemin du fichier de log
        format_string (Optional[str]): Format des messages de log
        
    Returns:
        logging.Logger: Logger configuré
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour le fichier si spécifié
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Récupère un logger existant ou en crée un nouveau.
    
    Args:
        name (str): Nom du logger
        
    Returns:
        logging.Logger: Logger
    """
    return logging.getLogger(name)

def set_log_level(logger: logging.Logger, level: int) -> None:
    """Définit le niveau de logging.
    
    Args:
        logger (logging.Logger): Logger à configurer
        level (int): Niveau de logging
    """
    logger.setLevel(level)

def add_file_handler(
    logger: logging.Logger,
    log_file: str,
    level: Optional[int] = None,
    format_string: Optional[str] = None
) -> None:
    """Ajoute un handler de fichier au logger.
    
    Args:
        logger (logging.Logger): Logger à configurer
        log_file (str): Chemin du fichier de log
        level (Optional[int]): Niveau de logging
        format_string (Optional[str]): Format des messages de log
    """
    if level is None:
        level = logger.level
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def add_console_handler(
    logger: logging.Logger,
    level: Optional[int] = None,
    format_string: Optional[str] = None
) -> None:
    """Ajoute un handler console au logger.
    
    Args:
        logger (logging.Logger): Logger à configurer
        level (Optional[int]): Niveau de logging
        format_string (Optional[str]): Format des messages de log
    """
    if level is None:
        level = logger.level
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def remove_handlers(logger: logging.Logger) -> None:
    """Supprime tous les handlers du logger.
    
    Args:
        logger (logging.Logger): Logger à configurer
    """
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

def create_rotating_file_handler(
    logger: logging.Logger,
    log_file: str,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    level: Optional[int] = None,
    format_string: Optional[str] = None
) -> None:
    """Crée un handler de fichier avec rotation.
    
    Args:
        logger (logging.Logger): Logger à configurer
        log_file (str): Chemin du fichier de log
        max_bytes (int): Taille maximale du fichier
        backup_count (int): Nombre de fichiers de backup
        level (Optional[int]): Niveau de logging
        format_string (Optional[str]): Format des messages de log
    """
    from logging.handlers import RotatingFileHandler
    
    if level is None:
        level = logger.level
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def create_timed_rotating_file_handler(
    logger: logging.Logger,
    log_file: str,
    when: str = 'midnight',
    interval: int = 1,
    backup_count: int = 7,
    level: Optional[int] = None,
    format_string: Optional[str] = None
) -> None:
    """Crée un handler de fichier avec rotation temporelle.
    
    Args:
        logger (logging.Logger): Logger à configurer
        log_file (str): Chemin du fichier de log
        when (str): Moment de la rotation
        interval (int): Intervalle de rotation
        backup_count (int): Nombre de fichiers de backup
        level (Optional[int]): Niveau de logging
        format_string (Optional[str]): Format des messages de log
    """
    from logging.handlers import TimedRotatingFileHandler
    
    if level is None:
        level = logger.level
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = TimedRotatingFileHandler(
        log_file,
        when=when,
        interval=interval,
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def log_exception(logger: logging.Logger, exc: Exception, context: Optional[str] = None) -> None:
    """Log une exception avec son contexte.
    
    Args:
        logger (logging.Logger): Logger à utiliser
        exc (Exception): Exception à logger
        context (Optional[str]): Contexte de l'exception
    """
    if context:
        logger.error(f"{context}: {str(exc)}", exc_info=True)
    else:
        logger.error(str(exc), exc_info=True)

def log_performance(logger: logging.Logger, operation: str, duration: float) -> None:
    """Log les performances d'une opération.
    
    Args:
        logger (logging.Logger): Logger à utiliser
        operation (str): Nom de l'opération
        duration (float): Durée en secondes
    """
    logger.info(f"Performance - {operation}: {duration:.3f}s")

def log_memory_usage(logger: logging.Logger, operation: str, memory_usage: float) -> None:
    """Log l'utilisation de la mémoire.
    
    Args:
        logger (logging.Logger): Logger à utiliser
        operation (str): Nom de l'opération
        memory_usage (float): Utilisation de la mémoire en MB
    """
    logger.info(f"Memory Usage - {operation}: {memory_usage:.2f}MB")

def log_api_call(
    logger: logging.Logger,
    endpoint: str,
    method: str,
    status_code: int,
    duration: float
) -> None:
    """Log un appel API.
    
    Args:
        logger (logging.Logger): Logger à utiliser
        endpoint (str): Endpoint appelé
        method (str): Méthode HTTP
        status_code (int): Code de statut HTTP
        duration (float): Durée en secondes
    """
    logger.info(
        f"API Call - {method} {endpoint} - Status: {status_code} - Duration: {duration:.3f}s"
    )

def log_data_validation(
    logger: logging.Logger,
    data_type: str,
    is_valid: bool,
    details: Optional[str] = None
) -> None:
    """Log la validation de données.
    
    Args:
        logger (logging.Logger): Logger à utiliser
        data_type (str): Type de données validé
        is_valid (bool): Si les données sont valides
        details (Optional[str]): Détails de la validation
    """
    if is_valid:
        logger.info(f"Data Validation - {data_type}: Valid")
    else:
        logger.warning(f"Data Validation - {data_type}: Invalid - {details}")

def log_model_prediction(
    logger: logging.Logger,
    model_name: str,
    prediction: str,
    confidence: float
) -> None:
    """Log une prédiction de modèle.
    
    Args:
        logger (logging.Logger): Logger à utiliser
        model_name (str): Nom du modèle
        prediction (str): Prédiction
        confidence (float): Score de confiance
    """
    logger.info(
        f"Model Prediction - {model_name}: {prediction} (Confidence: {confidence:.2f})"
    ) 