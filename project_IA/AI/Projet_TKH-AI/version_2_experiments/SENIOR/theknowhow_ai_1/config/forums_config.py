"""
Configuration pour les scrapers de forums médicaux.
"""

import os
from typing import Dict, List

# Configuration générale pour tous les forums
COMMON_CONFIG = {
    "max_retries": 3,  # Nombre maximum de tentatives en cas d'erreur
    "retry_delay": 5,  # Délai en secondes entre les tentatives
    "batch_size": 100,  # Nombre de posts à sauvegarder par lot
    "min_post_length": 50,  # Longueur minimale d'un post pour être considéré
    "default_language": "en",  # Langue par défaut pour le filtrage
    "request_delay": 2,  # Délai en secondes entre les requêtes
    "max_pages_per_category": 10,  # Nombre maximum de pages à scraper par catégorie
}

# Configuration spécifique pour HealthUnlocked
HEALTHUNLOCKED_CONFIG = {
    "base_url": "https://healthunlocked.com",
    "api_endpoint": "https://api.healthunlocked.com/v2",
    "communities": [
        "anxiety-support-group",
        "depression-support",
        "diabetes-support",
        "heart-disease-support",
        "cancer-support",
        "chronic-pain",
        "mental-health-support",
        "weight-loss-support"
    ],
    "post_types": ["question", "discussion", "story"],
    "sort_options": ["recent", "popular", "unanswered"]
}

# Configuration spécifique pour MedHelp
MEDHELP_CONFIG = {
    "base_url": "https://www.medhelp.org",
    "forums": [
        "general-medicine",
        "cardiology",
        "dermatology",
        "neurology",
        "oncology",
        "pediatrics",
        "psychology",
        "womens-health"
    ],
    "sort_options": ["date", "responses", "views"]
}

# Configuration spécifique pour Patient.info
PATIENT_INFO_CONFIG = {
    "base_url": "https://patient.info/forums",
    "categories": [
        "general-health",
        "mental-health",
        "pregnancy",
        "medicines",
        "wellbeing",
        "children-s-health",
        "skin-conditions",
        "cancer"
    ],
    "sort_by": ["latest", "popular", "unanswered"]
}

# Configuration spécifique pour HealthBoards
HEALTHBOARDS_CONFIG = {
    "base_url": "https://www.healthboards.com",
    "boards": [
        "allergies",
        "cancer",
        "diabetes",
        "heart",
        "mental-health",
        "pain-management",
        "skin",
        "weight-loss"
    ],
    "sort_options": ["newest", "most-viewed", "most-replied"]
}

# Configuration spécifique pour WebMD
WEBMD_CONFIG = {
    "base_url": "https://exchanges.webmd.com",
    "communities": [
        "general-medicine",
        "heart-disease",
        "diabetes",
        "cancer",
        "mental-health",
        "pain-management",
        "skin-problems",
        "weight-management"
    ],
    "sort_by": ["recent", "popular", "expert-replied"]
}

# Mots-clés médicaux pour le filtrage
MEDICAL_KEYWORDS = [
    # Symptômes généraux
    "pain", "fever", "fatigue", "headache", "nausea", "dizziness",
    
    # Conditions médicales
    "diabetes", "cancer", "arthritis", "depression", "anxiety",
    "hypertension", "asthma", "infection", "inflammation",
    
    # Termes médicaux
    "diagnosis", "treatment", "medication", "surgery", "therapy",
    "prescription", "doctor", "hospital", "clinic", "specialist",
    
    # Urgence médicale
    "emergency", "urgent", "severe", "acute", "chronic",
    "critical", "immediate", "life-threatening",
    
    # Examens et procédures
    "test", "scan", "x-ray", "mri", "blood-test", "biopsy",
    "examination", "screening", "analysis"
]

# Configuration des bases de données
DB_CONFIG = {
    "healthunlocked": {
        "db_path": os.path.join("data", "database", "sqlite", "healthunlocked.db"),
        "table_name": "healthunlocked_posts"
    },
    "medhelp": {
        "db_path": os.path.join("data", "database", "sqlite", "medhelp.db"),
        "table_name": "medhelp_posts"
    },
    "patient_info": {
        "db_path": os.path.join("data", "database", "sqlite", "patient_info.db"),
        "table_name": "patient_info_posts"
    },
    "healthboards": {
        "db_path": os.path.join("data", "database", "sqlite", "healthboards.db"),
        "table_name": "healthboards_posts"
    },
    "webmd": {
        "db_path": os.path.join("data", "database", "sqlite", "webmd.db"),
        "table_name": "webmd_posts"
    }
}

# Configuration des headers HTTP communs
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
} 