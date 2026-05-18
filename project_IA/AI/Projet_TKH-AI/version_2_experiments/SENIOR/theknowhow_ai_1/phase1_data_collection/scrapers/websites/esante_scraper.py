"""
Scraper pour le site e-santé
"""

import asyncio
import logging
from config.websites.esante_config import CONFIG
from .base_web_scraper import BaseWebScraper

logger = logging.getLogger(__name__)

class ESanteScraper(BaseWebScraper):
    """Scraper spécifique pour le site e-santé."""
    
    def __init__(self):
        """Initialise le scraper e-santé."""
        super().__init__(CONFIG)
        logger.info("Initialisation du scraper e-santé")

async def main():
    """Point d'entrée principal."""
    scraper = ESanteScraper()
    await scraper.scrape_articles()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main()) 