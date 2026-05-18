"""
Scraper pour le site Santé Magazine
"""

import asyncio
import logging
from config.websites.sante_magazine_config import CONFIG
from .base_web_scraper import BaseWebScraper

logger = logging.getLogger(__name__)

class SanteMagazineScraper(BaseWebScraper):
    """Scraper spécifique pour le site Santé Magazine."""
    
    def __init__(self):
        """Initialise le scraper Santé Magazine."""
        super().__init__(CONFIG)
        logger.info("Initialisation du scraper Santé Magazine")

async def main():
    """Point d'entrée principal."""
    scraper = SanteMagazineScraper()
    await scraper.scrape_articles()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main()) 