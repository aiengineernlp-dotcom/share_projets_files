"""
Configuration pour le scraper E-santé
"""

SITE_NAME = "E-santé"
BASE_URL = "https://www.e-sante.fr"
DB_PATH_ENV = "ESANTE_DB_PATH"
DEFAULT_LANGUAGE = "fr"

# Paramètres de scraping
MAX_PAGES_PER_CATEGORY = 50
REQUEST_DELAY = 2  # secondes
RANDOM_DELAY = True
MAX_RETRIES = 3
RETRY_DELAY = 5  # secondes

# Sélecteurs CSS
SELECTORS = {
    'title': 'h1.article-title',
    'content': 'div.article-content',
    'author': 'span.author-name',
    'date': 'time.published-date',
    'category': 'span.article-category',
    'tags': 'div.article-tags a',
    'article_links': 'div.article-list a.article-link'
}

# Catégories d'articles
CATEGORIES = {
    'actualites': {
        'name': 'Actualités',
        'url': '/actualites'
    },
    'dossiers': {
        'name': 'Dossiers',
        'url': '/dossiers'
    },
    'maladies': {
        'name': 'Maladies',
        'url': '/maladies'
    },
    'traitements': {
        'name': 'Traitements',
        'url': '/traitements'
    },
    'prevention': {
        'name': 'Prévention',
        'url': '/prevention'
    },
    'bien-etre': {
        'name': 'Bien-être',
        'url': '/bien-etre'
    },
    'nutrition': {
        'name': 'Nutrition',
        'url': '/nutrition'
    },
    'sexualite': {
        'name': 'Sexualité',
        'url': '/sexualite'
    },
    'psychologie': {
        'name': 'Psychologie',
        'url': '/psychologie'
    }
}

# Headers HTTP
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Mots-clés médicaux
KEYWORDS = [
    'santé', 'médecin', 'maladie', 'symptôme', 'traitement',
    'diagnostic', 'thérapie', 'médicament', 'prévention',
    'nutrition', 'bien-être', 'psychologie', 'sexualité',
    'grossesse', 'bébé', 'médecine douce', 'homéopathie',
    'phytothérapie', 'ostéopathie', 'acupuncture'
]

# Configuration du logging
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
} 