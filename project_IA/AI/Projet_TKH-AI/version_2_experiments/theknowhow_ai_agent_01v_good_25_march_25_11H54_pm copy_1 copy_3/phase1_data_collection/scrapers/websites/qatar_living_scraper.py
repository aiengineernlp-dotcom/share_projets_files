"""
Scraper pour le site Qatar Living
"""

import asyncio
import logging
from config.websites.qatar_living_config import CONFIG
from .base_web_scraper import BaseWebScraper

class QatarLivingScraper(BaseWebScraper):
    def __init__(self):
        super().__init__(CONFIG)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation du scraper Qatar Living")

    async def parse_article(self, soup, url):
        """Surcharge de la méthode pour extraire les réponses aux threads"""
        article = await super().parse_article(soup, url)
        
        # Extraction des réponses
        replies = []
        for reply_div in soup.select(CONFIG['SELECTORS']['replies']):
            reply = {
                'content': reply_div.get_text(strip=True),
                'author': reply_div.find_previous(CONFIG['SELECTORS']['reply_author']).get_text(strip=True) if reply_div.find_previous(CONFIG['SELECTORS']['reply_author']) else None,
                'date': reply_div.find_previous(CONFIG['SELECTORS']['reply_date']).get_text(strip=True) if reply_div.find_previous(CONFIG['SELECTORS']['reply_date']) else None
            }
            replies.append(reply)
        
        article['replies'] = replies
        return article

async def main():
    scraper = QatarLivingScraper()
    await scraper.scrape_articles()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 