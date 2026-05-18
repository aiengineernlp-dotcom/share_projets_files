"""
Gestion de la connexion à la base de données.
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 951-1000 : connexion et initialisation DB)
"""

import os
import sqlite3
from typing import Optional
from contextlib import contextmanager
from ..config.settings import DATABASE_URL, DATA_DIR
from ..config.logging_config import logger

# Configuration du chemin de la base de données SQLite
SQLITE_DB_PATH = os.path.join(DATA_DIR, "database", "sqlite", "phase1.db")

# Création du dossier pour la base de données si nécessaire
os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)

@contextmanager
def get_db_connection():
    """
    Contexte pour établir une connexion à la base de données.
    Returns:
        sqlite3.Connection: Connexion à la base de données
    """
    conn = None
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        logger.info("Connexion à la base de données établie")
        yield conn
    except Exception as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Connexion à la base de données fermée")

def init_database():
    """
    Initialise la base de données avec les tables nécessaires.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Table des posts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT,
                url TEXT,
                created_utc REAL,
                subreddit TEXT,
                author TEXT,
                category TEXT,
                second_opinion_score REAL,
                urgency_score REAL,
                medical_relevance_score REAL,
                sentiment_score REAL,
                overall_score REAL,
                country TEXT,
                city TEXT,
                region TEXT,
                latitude REAL,
                longitude REAL
            )
            """)
            
            # Table des utilisateurs GCC
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS gcc_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT,
                country TEXT,
                city TEXT,
                region TEXT,
                latitude REAL,
                longitude REAL,
                created_at REAL,
                subreddit TEXT,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
            """)
            
            # Table des réponses
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT,
                response_text TEXT,
                sent_time REAL,
                response_status TEXT,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
            """)
            
            conn.commit()
            logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise

def execute_query(query: str, params: Optional[tuple] = None) -> list:
    """
    Exécute une requête SQL avec des paramètres optionnels.
    
    Args:
        query (str): Requête SQL à exécuter
        params (tuple, optional): Paramètres de la requête
        
    Returns:
        list: Résultats de la requête
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la requête: {e}")
        raise

def execute_many(query: str, params: list) -> None:
    """
    Exécute une requête SQL avec plusieurs jeux de paramètres.
    
    Args:
        query (str): Requête SQL à exécuter
        params (list): Liste de tuples de paramètres
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params)
            conn.commit()
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la requête multiple: {e}")
        raise

# Initialisation de la base de données au démarrage
init_database() 