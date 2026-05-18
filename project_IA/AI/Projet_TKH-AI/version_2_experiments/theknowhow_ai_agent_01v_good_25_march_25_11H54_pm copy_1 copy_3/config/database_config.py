"""
Configuration de la base de données.
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 48-150 : schéma base de données et initialisation)
"""

import os
import sqlite3
from .settings import DATABASE_URL, DATA_DIR
from .logging_config import logger

# Configuration de la base de données SQLite
SQLITE_DB_PATH = os.path.join(DATA_DIR, "database", "sqlite", "phase1.db")

# Création du dossier pour la base de données si nécessaire
os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)

def get_db_connection():
    """
    Établit une connexion à la base de données.
    Returns:
        sqlite3.Connection: Connexion à la base de données
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        logger.info("Connexion à la base de données établie")
        return conn
    except Exception as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {e}")
        raise

# Schéma de la base de données
DB_SCHEMA = {
    "posts": """
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
    """,
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            country TEXT,
            is_gcc BOOLEAN,
            first_seen REAL,
            last_seen REAL
        )
    """,
    "responses": """
        CREATE TABLE IF NOT EXISTS responses (
            id TEXT PRIMARY KEY,
            post_id TEXT,
            user_id TEXT,
            message TEXT,
            response TEXT,
            timestamp REAL,
            sentiment_score REAL,
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
}

def init_database():
    """
    Initialise la base de données avec les tables nécessaires.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for table_name, schema in DB_SCHEMA.items():
            cursor.execute(schema)
            logger.info(f"Table {table_name} créée ou déjà existante")
        
        conn.commit()
        logger.info("Initialisation de la base de données terminée")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Initialisation de la base de données au démarrage
init_database() 