"""
Configuration pour le scraper Twitter.
"""

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

TWITTER_CONFIG = {
    "api_key": os.getenv("TWITTER_API_KEY"),
    "api_key_secret": os.getenv("TWITTER_API_KEY_SECRET"),
    "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    "bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
    "client_id": os.getenv("TWITTER_CLIENT_ID"),
    "client_secret": os.getenv("TWITTER_CLIENT_SECRET"),
    "db_path": os.getenv("TWITTER_DB_PATH", "phase1_data_collection/data/raw/social_media/twitter/sqlite/twitter.db"),
    "json_storage_path": os.getenv("TWITTER_JSON_STORAGE_PATH", "phase1_data_collection/data/raw/social_media/twitter/json"),
    "csv_storage_path": os.getenv("TWITTER_CSV_STORAGE_PATH", "phase1_data_collection/data/raw/social_media/twitter/csv"),
    "posts_table": "twitter_posts",
    "batch_size": int(os.getenv("BATCH_SIZE", 32))
}

# Configuration des hashtags médicaux à suivre
MEDICAL_HASHTAGS = [
    "#medical",
    "#health",
    "#doctor",
    "#healthcare",
    "#medicaladvice",
    "#askdoctor",
    "#medicalhelp",
    "#diagnosis"
]

# Configuration des mots-clés médicaux pour le filtrage
MEDICAL_KEYWORDS = [
    "symptoms",
    "diagnosis",
    "treatment",
    "doctor",
    "hospital",
    "medicine",
    "pain",
    "disease",
    "condition",
    "medical"
]

# Paramètres de recherche
SEARCH_PARAMS = {
    "max_results_per_query": int(os.getenv("MAX_POSTS_PER_QUERY", 100)),
    "max_queries_per_hashtag": 2,
    "min_tweet_length": 50,
    "language": "en",
    "delay_between_queries": int(os.getenv("SCRAPING_DELAY", 2)),
    "max_retries": int(os.getenv("MAX_RETRIES", 3))
}

# Configuration du logging
LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "file": os.getenv("LOG_FILE", "./logs/theknowhow.log")
} 