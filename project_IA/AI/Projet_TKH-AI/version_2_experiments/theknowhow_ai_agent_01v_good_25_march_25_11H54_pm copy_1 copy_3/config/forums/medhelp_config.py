"""
Configuration pour le scraping MedHelp
"""

import os

# Configuration de base
BASE_URL = "https://www.medhelp.org"
MAX_PAGES_PER_FORUM = 10
BATCH_SIZE = 25
REQUEST_DELAY = 10
RANDOM_DELAY = 5
MAX_RETRIES = 5
RETRY_DELAY = 20
DB_PATH = os.getenv("MEDHELP_DB_PATH", os.path.join("data", "raw", "forums", "medhelp", "sqlite", "medhelp.db"))
TABLE_NAME = "posts"

# Sélecteurs CSS
SELECTORS = {
    "post": ".post-thread",
    "author": ".author",
    "title": ".thread-title",
    "content": ".thread-content",
    "link": ".thread-link",
    "expert_reply": ".expert-response",
    "views": ".views-count",
    "replies": ".replies-count",
    "date": ".post-date"
}

# Catégories de forums
FORUM_CATEGORIES = {
    "general_health": {
        "name": "General Health",
        "url": "/forums/list/General-Health",
        "subcategories": [
            "General Health Questions",
            "Health News",
            "Health Insurance",
            "Alternative Medicine"
        ]
    },
    "conditions": {
        "name": "Conditions",
        "url": "/forums/list/Conditions",
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
        "url": "/forums/list/Medications",
        "subcategories": [
            "Prescription Drugs",
            "Over-the-Counter",
            "Side Effects",
            "Drug Interactions"
        ]
    },
    "procedures": {
        "name": "Procedures",
        "url": "/forums/list/Procedures",
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

# Configuration de la base de données
DB_CONFIG = {
    "db_path": DB_PATH,
    "table_name": TABLE_NAME,
    "batch_size": 100,
    "vacuum_frequency": 1000
}

# Headers HTTP
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

# Options de tri et filtrage
SORT_OPTIONS = {
    "date": {
        "param": "sort=date",
        "priority": 1
    },
    "responses": {
        "param": "sort=responses",
        "priority": 2
    },
    "views": {
        "param": "sort=views",
        "priority": 3
    }
}

# Mots-clés spécifiques à MedHelp
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
        "forum_name"
    ],
    "expert_response_weight": 1.5  # Multiplicateur de score pour les réponses d'experts
} 