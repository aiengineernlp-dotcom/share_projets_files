"""
Scraper spécifique pour WebTeb.
"""

import asyncio
import logging
import os
import sqlite3
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)

class WebTebScraper:
    """Scraper spécifique pour WebTeb."""
    
    def __init__(self):
        """Initialisation du scraper."""
        self.base_url = "https://www.webteb.com"
        self.db_path = os.getenv("WEBTEB_DB_PATH", "data/raw/websites/webteb/sqlite/webteb.db")
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3'
        }
        self._init_db()
        logger.info("Initialisation du scraper WebTeb")

    def _init_db(self):
        """Initialisation de la base de données spécifique à WebTeb."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Table des articles
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS webteb_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    author TEXT,
                    date TEXT,
                    category TEXT,
                    url TEXT UNIQUE,
                    tags TEXT,
                    views INTEGER,
                    likes INTEGER,
                    share_count INTEGER
                )
            ''')
            
            # Table des commentaires
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS webteb_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER,
                    content TEXT,
                    author TEXT,
                    date TEXT,
                    likes INTEGER,
                    FOREIGN KEY (article_id) REFERENCES webteb_articles (id)
                )
            ''')
            
            # Table des auteurs
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS webteb_authors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    title TEXT,
                    speciality TEXT,
                    article_count INTEGER DEFAULT 0,
                    last_article_date TEXT
                )
            ''')
            
            self.conn.commit()
            logger.info("Base de données WebTeb initialisée")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur d'initialisation de la base de données: {e}")
            raise

    async def _init_session(self):
        """Initialisation de la session HTTP."""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def _fetch_page(self, url: str) -> str:
        """Récupération d'une page avec gestion des erreurs."""
        await self._init_session()
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de {url}: {e}")
            raise

    async def parse_article(self, url: str) -> dict:
        """Parse un article du site."""
        html = await self._fetch_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        article_data = {
            'title': self._extract_text(soup, 'h1.article-title'),
            'content': self._extract_text(soup, 'div.article-content'),
            'author': self._extract_text(soup, 'span.author-name'),
            'date': self._extract_text(soup, 'span.publish-date'),
            'category': self._extract_text(soup, 'div.article-category'),
            'url': url,
            'tags': self._extract_tags(soup, 'div.article-tags a'),
            'views': self._extract_number(soup, 'span.view-count'),
            'likes': self._extract_number(soup, 'span.like-count'),
            'share_count': self._extract_number(soup, 'span.share-count'),
            'comments': []
        }
        
        # Extraction des commentaires
        comment_elements = soup.select('div.comment')
        for comment in comment_elements:
            comment_data = {
                'content': self._extract_text(comment, 'div.comment-content'),
                'author': self._extract_text(comment, 'span.comment-author'),
                'date': self._extract_text(comment, 'span.comment-date'),
                'likes': self._extract_number(comment, 'span.comment-likes')
            }
            article_data['comments'].append(comment_data)
        
        return article_data

    def _extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """Extrait le texte d'un élément."""
        element = soup.select_one(selector)
        return element.text.strip() if element else ""

    def _extract_tags(self, soup: BeautifulSoup, selector: str) -> list:
        """Extrait les tags d'un article."""
        tags = soup.select(selector)
        return [tag.text.strip() for tag in tags]

    def _extract_number(self, soup: BeautifulSoup, selector: str) -> int:
        """Extrait un nombre d'un élément."""
        text = self._extract_text(soup, selector)
        try:
            return int(''.join(filter(str.isdigit, text)))
        except ValueError:
            return 0

    def _save_article(self, article_data: dict):
        """Sauvegarde un article et ses commentaires."""
        try:
            # Sauvegarde de l'article
            self.cursor.execute('''
                INSERT OR REPLACE INTO webteb_articles 
                (title, content, author, date, category, url, tags, views, likes, share_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_data['title'], article_data['content'],
                article_data['author'], article_data['date'],
                article_data['category'], article_data['url'],
                ','.join(article_data['tags']), article_data['views'],
                article_data['likes'], article_data['share_count']
            ))
            article_id = self.cursor.lastrowid
            
            # Sauvegarde des commentaires
            for comment in article_data['comments']:
                self.cursor.execute('''
                    INSERT INTO webteb_comments 
                    (article_id, content, author, date, likes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (article_id, comment['content'], comment['author'],
                      comment['date'], comment['likes']))
            
            # Mise à jour des statistiques auteur
            self.cursor.execute('''
                INSERT OR REPLACE INTO webteb_authors 
                (name, article_count, last_article_date)
                VALUES (?, 
                    COALESCE((SELECT article_count + 1 FROM webteb_authors WHERE name = ?), 1),
                    ?)
            ''', (article_data['author'], article_data['author'], article_data['date']))
            
            self.conn.commit()
            logger.info(f"Article sauvegardé: {article_data['title']}")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            self.conn.rollback()

    async def scrape_site(self):
        """Scrape le site WebTeb."""
        categories = {
            'diseases': '/medical-articles/diseases',
            'symptoms': '/medical-articles/symptoms',
            'treatments': '/medical-articles/treatments',
            'medications': '/medical-articles/medications',
            'nutrition': '/medical-articles/nutrition',
            'fitness': '/medical-articles/fitness',
            'mental-health': '/medical-articles/mental-health'
        }
        
        try:
            for category_name, category_path in categories.items():
                logger.info(f"Scraping de la catégorie: {category_name}")
                category_url = f"{self.base_url}{category_path}"
                
                try:
                    html = await self._fetch_page(category_url)
                    soup = BeautifulSoup(html, 'html.parser')
                    article_links = soup.select('div.article-list a.article-link')
                    
                    for link in article_links[:50]:  # Limite à 50 articles par catégorie
                        article_url = link.get('href')
                        if not article_url.startswith('http'):
                            article_url = f"{self.base_url}{article_url}"
                        
                        try:
                            article_data = await self.parse_article(article_url)
                            self._save_article(article_data)
                            await asyncio.sleep(2)  # Délai entre les requêtes
                        except Exception as e:
                            logger.error(f"Erreur lors du scraping de l'article {article_url}: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Erreur lors du scraping de la catégorie {category_name}: {e}")
                    continue
                    
        finally:
            await self.close()

    async def close(self):
        """Ferme les connexions."""
        if self.session:
            await self.session.close()
        if hasattr(self, 'conn'):
            self.conn.close()

async def main():
    """Fonction principale."""
    scraper = WebTebScraper()
    await scraper.scrape_site()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 