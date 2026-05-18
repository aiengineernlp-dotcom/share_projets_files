"""
Configuration pour le scraping HealthUnlocked
"""

import os

# Configuration de base
BASE_URL = "https://healthunlocked.com"
API_ENDPOINT = "https://api.healthunlocked.com/v2"
MIN_POST_LENGTH = 50
DEFAULT_LANGUAGE = "en"
REQUEST_DELAY = 2
MAX_RETRIES = 3
RETRY_DELAY = 5
BATCH_SIZE = 100
MAX_PAGES_PER_CATEGORY = 10
DB_PATH = os.getenv("HEALTHUNLOCKED_DB_PATH", os.path.join("data", "raw", "forums", "healthunlocked", "sqlite", "healthunlocked.db"))
TABLE_NAME = "healthunlocked_posts"

# Catégories de forums
FORUM_CATEGORIES = {
    "general_health": {
        "name": "General Health",
        "url": "/communities/general-health",
        "subcategories": [
            "General Health Questions",
            "Health News",
            "Health Insurance",
            "Alternative Medicine"
        ]
    },
    "conditions": {
        "name": "Conditions",
        "url": "/communities/conditions",
        "subcategories": [
            "Allergies",
            "Arthritis",
            "Asthma",
            "Cancer",
            "Diabetes",
            "Heart Disease",
            "High Blood Pressure",
            "Mental Health",
            "Pain Management"
        ]
    },
    "medications": {
        "name": "Medications",
        "url": "/communities/medications",
        "subcategories": [
            "Prescription Drugs",
            "Over-the-Counter",
            "Side Effects",
            "Drug Interactions"
        ]
    },
    "procedures": {
        "name": "Procedures",
        "url": "/communities/procedures",
        "subcategories": [
            "Surgery",
            "Tests",
            "Treatments",
            "Recovery"
        ]
    }
}

# Configuration des logs
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Options de tri et filtrage
SORT_OPTIONS = {
    "recent": {
        "param": "sort=recent",
        "priority": 1
    },
    "popular": {
        "param": "sort=popular",
        "priority": 2
    },
    "unanswered": {
        "param": "filter=unanswered",
        "priority": 1
    }
}

# Headers HTTP spécifiques
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://healthunlocked.com",
    "Referer": "https://healthunlocked.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache"
}

# Mots-clés spécifiques à HealthUnlocked
KEYWORDS = {
    "medical_terms": [
        "symptoms", "diagnosis", "treatment", "medication", "doctor",
        "specialist", "prescription", "therapy", "test", "exam"
    ],
    "conditions": [
        "heart disease", "skin condition", "neurological", "cancer",
        "pediatric", "psychological", "women's health", "infection"
    ],
    "expert_indicators": [
        "doctor's response", "expert reply", "physician's answer",
        "medical opinion", "professional advice", "specialist's view"
    ],
    "urgency_indicators": [
        "emergency", "urgent", "immediate", "severe", "critical",
        "life-threatening", "acute", "serious", "help needed"
    ]
}

# Configuration des timeouts et limites
TIMEOUT_CONFIG = {
    "connect": 15,  # Timeout de connexion en secondes
    "read": 45,     # Timeout de lecture en secondes
    "max_retries": 3,
    "backoff_factor": 3  # Facteur de délai exponentiel entre les tentatives
}

# Configuration de l'analyse des posts
ANALYSIS_CONFIG = {
    "min_relevance_score": 0.4,  # Score minimum de pertinence médicale
    "min_urgency_score": 0.3,    # Score minimum d'urgence
    "max_post_age_days": 45,     # Âge maximum des posts à collecter
    "required_fields": [         # Champs requis pour un post valide
        "title",
        "body",
        "author",
        "created_at",
        "community_name"
    ],
    "expert_response_weight": 1.5  # Multiplicateur de score pour les réponses d'experts
} 