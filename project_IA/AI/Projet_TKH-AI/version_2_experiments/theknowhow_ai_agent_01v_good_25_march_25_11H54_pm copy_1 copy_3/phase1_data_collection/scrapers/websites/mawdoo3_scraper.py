"""
Scraper pour le site Mawdoo3 (موضوع)
"""

import asyncio
import logging
from config.websites.mawdoo3_config import CONFIG
from .base_web_scraper import BaseWebScraper

class Mawdoo3Scraper(BaseWebScraper):
    def __init__(self):
        super().__init__(CONFIG)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation du scraper Mawdoo3")

    async def parse_article(self, soup, url):
        """Surcharge de la méthode pour extraire les commentaires"""
        article = await super().parse_article(soup, url)
        
        # Extraction des commentaires
        comments = []
        for comment_div in soup.select(CONFIG['SELECTORS']['comments']):
            comment = {
                'content': comment_div.get_text(strip=True),
                'author': comment_div.find_previous(CONFIG['SELECTORS']['comment_author']).get_text(strip=True) if comment_div.find_previous(CONFIG['SELECTORS']['comment_author']) else None,
                'date': comment_div.find_previous(CONFIG['SELECTORS']['comment_date']).get_text(strip=True) if comment_div.find_previous(CONFIG['SELECTORS']['comment_date']) else None
            }
            comments.append(comment)
        
        article['comments'] = comments
        return article

async def main():
    scraper = Mawdoo3Scraper()
    await scraper.scrape_articles()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 