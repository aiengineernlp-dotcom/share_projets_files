"""
Configuration pour le scraping du site Ameli
"""

import os

# Configuration de base
SITE_NAME = "ameli"
BASE_URL = "https://www.ameli.fr"
DB_PATH_ENV = "AMELI_DB_PATH"
DEFAULT_LANGUAGE = "fr"
MAX_PAGES_PER_CATEGORY = 20
REQUEST_DELAY = 3
RANDOM_DELAY = 2
MAX_RETRIES = 3
RETRY_DELAY = 5

# Sélecteurs CSS
SELECTORS = {
    "title": "h1.article-title",
    "content": "div.article-content",
    "author": "span.article-author",
    "date": "time.article-date",
    "category": "span.article-category",
    "tags": "div.article-tags a",
    "article_link": "div.article-list a.article-link"
}

# Catégories d'articles
CATEGORIES = {
    "assurance_maladie": {
        "name": "Assurance maladie",
        "url": "/assure/actualites"
    },
    "remboursements": {
        "name": "Remboursements",
        "url": "/assure/remboursements"
    },
    "prestations": {
        "name": "Prestations",
        "url": "/assure/prestations"
    },
    "droits_demarches": {
        "name": "Droits et démarches",
        "url": "/assure/droits-demarches"
    },
    "sante": {
        "name": "Santé",
        "url": "/assure/sante"
    }
}

# Headers HTTP
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Mots-clés médicaux
KEYWORDS = {
    "medical_terms": [
        "maladie", "santé", "traitement", "médicament", "médecin",
        "spécialiste", "ordonnance", "thérapie", "examen", "diagnostic",
        "symptôme", "pathologie", "prévention", "soins", "hospitalisation",
        "remboursement", "assurance", "mutuelle", "CPAM", "Sécurité sociale"
    ]
}

# Configuration des logs
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
} 