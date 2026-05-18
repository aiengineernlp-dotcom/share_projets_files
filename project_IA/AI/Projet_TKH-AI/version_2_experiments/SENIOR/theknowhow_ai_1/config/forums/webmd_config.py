"""
Configuration spécifique pour le scraper WebMD Community.
"""

import os

# Configuration de base
BASE_URL = "https://messageboards.webmd.com"
MIN_POST_LENGTH = 50
DEFAULT_LANGUAGE = "en"
REQUEST_DELAY = 3.5
MAX_RETRIES = 3
RETRY_DELAY = 8
BATCH_SIZE = 50
MAX_PAGES_PER_COMMUNITY = 15
DB_PATH = os.getenv("WEBMD_DB_PATH", os.path.join("data", "raw", "forums", "webmd", "sqlite", "webmd.db"))
TABLE_NAME = "webmd_posts"

# Configuration des communautés à scraper
COMMUNITIES = [
    {
        "name": "diabetes",
        "url_slug": "diabetes",
        "category": "endocrine",
        "priority": 1,
        "has_experts": True
    },
    {
        "name": "heart-disease",
        "url_slug": "heart-disease",
        "category": "cardiovascular",
        "priority": 1,
        "has_experts": True
    },
    {
        "name": "cancer",
        "url_slug": "cancer",
        "category": "oncology",
        "priority": 1,
        "has_experts": True
    },
    {
        "name": "anxiety-and-panic",
        "url_slug": "anxiety-and-panic-disorders",
        "category": "mental-health",
        "priority": 1,
        "has_experts": True
    },
    {
        "name": "depression",
        "url_slug": "depression",
        "category": "mental-health",
        "priority": 1,
        "has_experts": True
    },
    {
        "name": "pain-management",
        "url_slug": "pain-management",
        "category": "pain",
        "priority": 2,
        "has_experts": True
    },
    {
        "name": "add-adhd",
        "url_slug": "add-adhd",
        "category": "mental-health",
        "priority": 2,
        "has_experts": True
    },
    {
        "name": "multiple-sclerosis",
        "url_slug": "multiple-sclerosis",
        "category": "neurology",
        "priority": 2,
        "has_experts": True
    }
]

# Configuration de la base de données
DB_CONFIG = {
    "db_path": DB_PATH,
    "table_name": TABLE_NAME,
    "batch_size": BATCH_SIZE,
    "vacuum_frequency": 1000  # Nombre d'insertions avant VACUUM
}

# Headers HTTP spécifiques
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://messageboards.webmd.com",
    "Referer": "https://messageboards.webmd.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

# Mots-clés spécifiques à WebMD
KEYWORDS = {
    "medical_terms": [
        "symptoms", "diagnosis", "treatment", "medication", "doctor",
        "specialist", "prescription", "therapy", "test", "exam",
        "side effects", "dosage", "prognosis"
    ],
    "conditions": [
        "diabetes", "heart disease", "cancer", "anxiety",
        "depression", "chronic pain", "adhd", "multiple sclerosis"
    ],
    "expert_indicators": [
        "doctor", "physician", "specialist", "md", "expert",
        "professional", "clinician", "healthcare provider"
    ],
    "urgency_indicators": [
        "emergency", "urgent", "immediate", "severe", "critical",
        "life-threatening", "acute", "serious", "help needed"
    ]
}

# Configuration des timeouts et limites
TIMEOUT_CONFIG = {
    "connect": 12,  # Timeout de connexion en secondes
    "read": 35,     # Timeout de lecture en secondes
    "max_retries": 3,
    "backoff_factor": 2.5
}

# Configuration de l'analyse des posts
ANALYSIS_CONFIG = {
    "min_relevance_score": 0.35,  # Score minimum de pertinence médicale
    "min_urgency_score": 0.25,    # Score minimum d'urgence
    "max_post_age_days": 120,     # Âge maximum des posts à collecter
    "required_fields": [          # Champs requis pour un post valide
        "title",
        "body",
        "author",
        "created_at",
        "community_name",
        "has_expert_reply"
    ],
    "expert_reply_tracking": True,  # Suivi des réponses d'experts
    "expert_keywords": [           # Mots-clés indiquant une réponse d'expert
        "as a doctor",
        "as a physician",
        "in my medical opinion",
        "in my practice",
        "medical professional here"
    ]
}

# Configuration du suivi des discussions
THREAD_CONFIG = {
    "max_replies_to_fetch": 75,    # Nombre maximum de réponses à collecter par discussion
    "min_replies_threshold": 1,    # Nombre minimum de réponses pour considérer une discussion
    "prioritize_expert_replies": True,  # Donner la priorité aux réponses d'experts
    "track_user_roles": True,      # Suivi des rôles des utilisateurs (expert, membre régulier)
    "track_verified_answers": True  # Identification des réponses vérifiées par la communauté
} 