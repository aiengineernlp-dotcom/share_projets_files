"""
Script pour lancer le scraping de Reddit
"""
import asyncio
import sys
import os
from pathlib import Path

# Ajout du chemin racine au PYTHONPATH
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from app.scraping.social_media.reddit import RedditScraper
from app.utils.logger import setup_logger

logger = setup_logger("reddit_scraper")

async def main():
    # Initialisation du scraper
    reddit_scraper = RedditScraper()
    
    try:
        # Connexion à Reddit
        await reddit_scraper.connect()
        
        # Lancement du scraping
        data = await reddit_scraper.fetch_data()
        
        # Les données sont automatiquement sauvegardées dans data/raw/reddit/
        # et data/processed/reddit/ par le scraper
        
        logger.info(f"Scraping terminé. {len(data)} éléments collectés.")
        
    except Exception as e:
        logger.error(f"Erreur lors du scraping: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 