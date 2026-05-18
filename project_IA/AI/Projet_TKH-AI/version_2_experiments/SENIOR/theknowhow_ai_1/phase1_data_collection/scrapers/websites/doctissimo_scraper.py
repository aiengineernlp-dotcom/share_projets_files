"""
Scraper pour le site Doctissimo
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Ajout du chemin racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from phase1_data_collection.scrapers.websites.base_web_scraper import BaseWebScraper
from config.websites.doctissimo_config import (
    SITE_NAME, BASE_URL, DB_PATH_ENV, DEFAULT_LANGUAGE,
    MAX_PAGES_PER_CATEGORY, REQUEST_DELAY, RANDOM_DELAY,
    MAX_RETRIES, RETRY_DELAY, SELECTORS, CATEGORIES,
    HTTP_HEADERS, KEYWORDS, LOG_CONFIG, CONFIG
)

# Configuration du logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=LOG_CONFIG["level"],
    format=LOG_CONFIG["format"],
    handlers=[
        logging.FileHandler('logs/doctissimo_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DoctissimoScraper(BaseWebScraper):
    """Scraper spécifique pour le site Doctissimo."""
    
    def __init__(self):
        """Initialise le scraper Doctissimo."""
        super().__init__(CONFIG)
        logger.info("Initialisation du scraper Doctissimo")
        
    async def parse_article(self, html: str, url: str) -> Dict[str, Any]:
        """Parse le contenu HTML d'un article Doctissimo."""
        article = await super().parse_article(html, url)
        if article:
            # Ajout de la logique spécifique à Doctissimo si nécessaire
            article['source'] = 'Doctissimo'
            article['is_official'] = True
            # Extraction des commentaires si présents
            article['has_comments'] = 'commentaires' in html.lower()
        return article

async def main():
    """Point d'entrée principal."""
    scraper = DoctissimoScraper()
    await scraper.scrape_articles()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main()) 