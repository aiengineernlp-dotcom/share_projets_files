"""
Configuration pour le scraper Vidal
"""

SITE_NAME = "Vidal"
BASE_URL = "https://www.vidal.fr"
DB_PATH_ENV = "VIDAL_DB_PATH"
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
    'medicaments': {
        'name': 'Médicaments',
        'url': '/medicaments'
    },
    'maladies': {
        'name': 'Maladies',
        'url': '/maladies'
    },
    'interactions': {
        'name': 'Interactions',
        'url': '/interactions'
    },
    'actualites': {
        'name': 'Actualités',
        'url': '/actualites'
    },
    'dossiers': {
        'name': 'Dossiers',
        'url': '/dossiers'
    },
    'recherche': {
        'name': 'Recherche',
        'url': '/recherche'
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
    'médicament', 'maladie', 'symptôme', 'traitement',
    'diagnostic', 'thérapie', 'prévention', 'interaction',
    'effet secondaire', 'contre-indication', 'posologie',
    'pharmacie', 'ordonnance', 'prescription', 'générique',
    'brevet', 'laboratoire', 'substance active', 'forme galénique'
]

# Configuration du logging
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
} 