"""
Scraper pour le site Altibbi (الطبي)
"""

import asyncio
import logging
from config.websites.altibbi_config import CONFIG
from .base_web_scraper import BaseWebScraper

class AltibbiScraper(BaseWebScraper):
    def __init__(self):
        super().__init__(CONFIG)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation du scraper Altibbi")

    async def parse_article(self, soup, url):
        """Surcharge de la méthode pour extraire les réponses aux questions"""
        article = await super().parse_article(soup, url)
        
        # Extraction des réponses
        answers = []
        for answer_div in soup.select(CONFIG['SELECTORS']['answers']):
            answer = {
                'content': answer_div.get_text(strip=True),
                'author': answer_div.find_previous(CONFIG['SELECTORS']['answer_author']).get_text(strip=True) if answer_div.find_previous(CONFIG['SELECTORS']['answer_author']) else None,
                'date': answer_div.find_previous(CONFIG['SELECTORS']['answer_date']).get_text(strip=True) if answer_div.find_previous(CONFIG['SELECTORS']['answer_date']) else None
            }
            answers.append(answer)
        
        article['answers'] = answers
        return article

async def main():
    scraper = AltibbiScraper()
    await scraper.scrape_articles()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 