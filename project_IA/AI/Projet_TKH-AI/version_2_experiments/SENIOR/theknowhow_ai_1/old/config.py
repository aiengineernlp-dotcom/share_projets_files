"""
Module de gestion de la configuration.
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Charge la configuration depuis un fichier YAML ou JSON.
    
    Args:
        config_path (str): Chemin vers le fichier de configuration.
        
    Returns:
        Dict[str, Any]: Configuration chargée ou dictionnaire vide en cas d'erreur.
    """
    if not config_path or not os.path.exists(config_path):
        logger.warning(f"Fichier de configuration non trouvé: {config_path}")
        return {}
    
    try:
        _, ext = os.path.splitext(config_path)
        
        if ext.lower() in ['.yaml', '.yml']:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
                
        elif ext.lower() == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        else:
            logger.warning(f"Format de configuration non pris en charge: {ext}")
            return {}
            
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration {config_path}: {e}")
        return {}

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Sauvegarde la configuration dans un fichier YAML ou JSON.
    
    Args:
        config (Dict[str, Any]): Configuration à sauvegarder.
        config_path (str): Chemin vers le fichier de configuration.
        
    Returns:
        bool: True si la sauvegarde a réussi, False sinon.
    """
    try:
        # Créer le dossier parent si nécessaire
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        _, ext = os.path.splitext(config_path)
        
        if ext.lower() in ['.yaml', '.yml']:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                
        elif ext.lower() == '.json':
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        else:
            logger.warning(f"Format de configuration non pris en charge: {ext}")
            return False
            
        logger.info(f"Configuration sauvegardée dans {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la configuration {config_path}: {e}")
        return False

def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Récupère une valeur dans la configuration en utilisant un chemin de clés.
    
    Args:
        config (Dict[str, Any]): Configuration.
        key_path (str): Chemin de clés séparées par des points (ex: "database.host").
        default (Any, optional): Valeur par défaut si la clé n'existe pas.
        
    Returns:
        Any: Valeur trouvée ou valeur par défaut.
    """
    if not config:
        return default
        
    keys = key_path.split('.')
    current = config
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
            
    return current

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne deux configurations, avec la seconde qui écrase la première.
    
    Args:
        base_config (Dict[str, Any]): Configuration de base.
        override_config (Dict[str, Any]): Configuration qui écrase la base.
        
    Returns:
        Dict[str, Any]: Configuration fusionnée.
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
            
    return result 