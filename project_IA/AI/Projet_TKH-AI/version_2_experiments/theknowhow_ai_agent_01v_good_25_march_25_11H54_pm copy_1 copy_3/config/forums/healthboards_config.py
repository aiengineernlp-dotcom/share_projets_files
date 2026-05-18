"""
Configuration spécifique pour le scraper HealthBoards.
"""

import os

# Configuration de base
BASE_CONFIG = {
    "base_url": "https://www.healthboards.com",
    "min_post_length": 50,
    "default_language": "en",
    "request_delay": 3,
    "max_retries": 3,
    "retry_delay": 7,
    "batch_size": 60,
    "max_pages_per_board": 20
}

# Configuration des boards à scraper
BOARDS = [
    {
        "name": "allergies",
        "url_slug": "allergies",
        "category": "immune",
        "priority": 2,
        "sub_boards": ["food-allergies", "seasonal-allergies"]
    },
    {
        "name": "cancer",
        "url_slug": "cancer",
        "category": "oncology",
        "priority": 1,
        "sub_boards": ["breast-cancer", "lung-cancer", "skin-cancer"]
    },
    {
        "name": "diabetes",
        "url_slug": "diabetes",
        "category": "endocrine",
        "priority": 1,
        "sub_boards": ["type-1", "type-2", "gestational"]
    },
    {
        "name": "heart",
        "url_slug": "heart-cardiovascular",
        "category": "cardiovascular",
        "priority": 1,
        "sub_boards": ["heart-disease", "blood-pressure", "cholesterol"]
    },
    {
        "name": "mental-health",
        "url_slug": "mental-health",
        "category": "psychiatric",
        "priority": 1,
        "sub_boards": ["anxiety", "depression", "bipolar"]
    },
    {
        "name": "pain-management",
        "url_slug": "pain-management",
        "category": "pain",
        "priority": 2,
        "sub_boards": ["chronic-pain", "back-pain", "fibromyalgia"]
    },
    {
        "name": "skin",
        "url_slug": "skin-hair",
        "category": "dermatology",
        "priority": 2,
        "sub_boards": ["acne", "eczema", "psoriasis"]
    },
    {
        "name": "weight-loss",
        "url_slug": "weight-loss",
        "category": "lifestyle",
        "priority": 3,
        "sub_boards": ["diet", "exercise", "obesity"]
    }
]

# Options de tri et filtrage
SORT_OPTIONS = {
    "newest": {
        "param": "sort=newest",
        "priority": 1
    },
    "most-viewed": {
        "param": "sort=views",
        "priority": 2
    },
    "most-replied": {
        "param": "sort=replies",
        "priority": 2
    }
}

# Configuration de la base de données
DB_CONFIG = {
    "db_path": os.getenv("HEALTHBOARDS_DB_PATH", os.path.join("data", "raw", "forums", "healthboards.db")),
    "table_name": "healthboards_posts",
    "batch_size": 60,
    "vacuum_frequency": 600  # Nombre d'insertions avant VACUUM
}

# Headers HTTP spécifiques
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.healthboards.com",
    "Referer": "https://www.healthboards.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache"
}

# Mots-clés spécifiques à HealthBoards
KEYWORDS = {
    "medical_terms": [
        "symptoms", "diagnosis", "treatment", "medication", "doctor",
        "specialist", "prescription", "therapy", "test", "exam"
    ],
    "conditions": [
        "allergy", "cancer", "diabetes", "heart disease",
        "mental illness", "chronic pain", "skin condition"
    ],
    "status_indicators": [
        "resolved", "unresolved", "ongoing", "chronic",
        "acute", "improving", "worsening", "stable"
    ],
    "urgency_indicators": [
        "emergency", "urgent", "immediate", "severe", "critical",
        "life-threatening", "acute", "serious", "help needed"
    ]
}

# Configuration des timeouts et limites
TIMEOUT_CONFIG = {
    "connect": 10,  # Timeout de connexion en secondes
    "read": 30,     # Timeout de lecture en secondes
    "max_retries": 3,
    "backoff_factor": 2
}

# Configuration de l'analyse des posts
ANALYSIS_CONFIG = {
    "min_relevance_score": 0.3,   # Score minimum de pertinence médicale
    "min_urgency_score": 0.2,     # Score minimum d'urgence
    "max_post_age_days": 90,      # Âge maximum des posts à collecter
    "required_fields": [          # Champs requis pour un post valide
        "title",
        "body",
        "author",
        "created_at",
        "board_name",
        "sub_board"
    ],
    "resolution_tracking": True,   # Suivi de la résolution des problèmes
    "resolution_keywords": [       # Mots-clés indiquant une résolution
        "solved",
        "resolved",
        "fixed",
        "cured",
        "better",
        "improved"
    ]
}

# Configuration du suivi des discussions
THREAD_CONFIG = {
    "max_replies_to_fetch": 50,    # Nombre maximum de réponses à collecter par discussion
    "min_replies_threshold": 2,    # Nombre minimum de réponses pour considérer une discussion
    "track_user_history": True,    # Suivi de l'historique des utilisateurs
    "track_solution_posts": True   # Identification des posts contenant des solutions
} 