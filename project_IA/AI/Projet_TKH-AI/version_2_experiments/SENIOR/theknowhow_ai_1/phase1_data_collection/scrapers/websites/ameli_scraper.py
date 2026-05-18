"""
Scraper pour le site Ameli
"""

import asyncio
import logging
from config.websites.ameli_config import CONFIG
from .base_web_scraper import BaseWebScraper

logger = logging.getLogger(__name__)

class AmeliScraper(BaseWebScraper):
    """Scraper spécifique pour le site Ameli."""
    
    def __init__(self):
        """Initialise le scraper Ameli."""
        super().__init__(CONFIG)
        logger.info("Initialisation du scraper Ameli")

async def main():
    """Point d'entrée principal."""
    scraper = AmeliScraper()
    await scraper.scrape_articles()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main()) 