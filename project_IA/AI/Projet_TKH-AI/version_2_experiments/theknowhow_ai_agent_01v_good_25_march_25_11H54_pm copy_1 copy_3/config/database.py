import os
import sqlite3
from typing import Dict, Any
from .settings import DATABASE_CONFIG, logger

def init_db() -> None:
    """
    Initialise la base de données avec les tables nécessaires
    """
    try:
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(DATABASE_CONFIG["path"]), exist_ok=True)

        with sqlite3.connect(DATABASE_CONFIG["path"]) as conn:
            cursor = conn.cursor()
            
            # Créer les tables
            for table_name, table_schema in DATABASE_CONFIG["tables"].items():
                cursor.execute(table_schema)
            
            conn.commit()
            logger.info("Base de données initialisée avec succès")
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise

def get_db_connection() -> sqlite3.Connection:
    """
    Retourne une connexion à la base de données
    """
    return sqlite3.connect(DATABASE_CONFIG["path"]) 