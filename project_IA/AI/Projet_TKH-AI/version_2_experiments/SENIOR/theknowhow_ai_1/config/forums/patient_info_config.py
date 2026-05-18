"""
Configuration pour le scraping Patient.info
"""

import os

# Configuration de base
BASE_URL = "https://patient.info/forums"
MIN_POST_LENGTH = 50
DEFAULT_LANGUAGE = "en"
REQUEST_DELAY = 2.5
MAX_RETRIES = 3
RETRY_DELAY = 8
BATCH_SIZE = 75
MAX_PAGES_PER_CATEGORY = 12
DB_PATH = os.getenv("PATIENT_INFO_DB_PATH", os.path.join("data", "raw", "forums", "patient_info", "sqlite", "patient_info.db"))
TABLE_NAME = "patient_info_posts"

# Catégories de forums
FORUM_CATEGORIES = {
    "general_health": {
        "name": "General Health",
        "url": "/discuss/browse/general-health",
        "subcategories": [
            "General Health Questions",
            "Health News",
            "Health Insurance",
            "Alternative Medicine"
        ]
    },
    "conditions": {
        "name": "Conditions",
        "url": "/discuss/browse/conditions",
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
        "url": "/discuss/browse/medications",
        "subcategories": [
            "Prescription Drugs",
            "Over-the-Counter",
            "Side Effects",
            "Drug Interactions"
        ]
    },
    "procedures": {
        "name": "Procedures",
        "url": "/discuss/browse/procedures",
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
    "latest": {
        "param": "sort=latest",
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",  # Spécifique au UK
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://patient.info",
    "Referer": "https://patient.info",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache"
}

# Mots-clés spécifiques à Patient.info
KEYWORDS = {
    "medical_terms": [
        "symptoms", "diagnosis", "treatment", "medication", "doctor",
        "GP", "NHS", "consultant", "prescription", "referral"  # Termes UK
    ],
    "conditions": [
        "anxiety", "depression", "pregnancy", "skin condition",
        "cancer", "infection", "chronic", "acute", "allergy"
    ],
    "professional_indicators": [
        "doctor's reply", "GP advice", "consultant's opinion",
        "medical professional", "healthcare provider", "specialist"
    ],
    "urgency_indicators": [
        "emergency", "urgent", "immediate", "severe", "critical",
        "999", "A&E", "NHS 111", "serious", "life-threatening"  # Termes UK
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
    "max_post_age_days": 60,      # Âge maximum des posts à collecter
    "required_fields": [          # Champs requis pour un post valide
        "title",
        "body",
        "author",
        "created_at",
        "category"
    ],
    "professional_response_weight": 1.4  # Multiplicateur de score pour les réponses professionnelles
}

# Configuration spécifique au Royaume-Uni
UK_SPECIFIC = {
    "nhs_keywords": [
        "NHS", "GP", "A&E", "999", "111",
        "surgery", "clinic", "hospital", "trust",
        "CCG", "health centre", "practice"
    ],
    "location_tracking": True,  # Pour filtrer les posts par région du UK
    "regions": [
        "England",
        "Scotland",
        "Wales",
        "Northern Ireland"
    ]
} 