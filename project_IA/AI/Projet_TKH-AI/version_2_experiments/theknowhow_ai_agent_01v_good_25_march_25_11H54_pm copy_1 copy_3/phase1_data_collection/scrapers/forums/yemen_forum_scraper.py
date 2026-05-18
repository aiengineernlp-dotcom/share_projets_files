"""
Scraper spécifique pour Yemen Forum.
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

class YemenForumScraper:
    """Scraper spécifique pour Yemen Forum."""
    
    def __init__(self):
        """Initialisation du scraper."""
        self.base_url = "https://www.yemenforum.net"
        self.db_path = os.getenv("YEMEN_FORUM_DB_PATH")
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3'
        }
        self._init_db()
        logger.info("Initialisation du scraper Yemen Forum")

    def _init_db(self):
        """Initialisation de la base de données spécifique à Yemen Forum."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Table des discussions
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS yemen_forum_threads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    author TEXT,
                    date TEXT,
                    category TEXT,
                    url TEXT UNIQUE,
                    views INTEGER,
                    reply_count INTEGER
                )
            ''')
            
            # Table des réponses
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS yemen_forum_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id INTEGER,
                    content TEXT,
                    author TEXT,
                    date TEXT,
                    FOREIGN KEY (thread_id) REFERENCES yemen_forum_threads (id)
                )
            ''')
            
            # Table des utilisateurs
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS yemen_forum_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    post_count INTEGER DEFAULT 0,
                    join_date TEXT,
                    last_active TEXT,
                    location TEXT
                )
            ''')
            
            self.conn.commit()
            logger.info("Base de données Yemen Forum initialisée")
            
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

    async def parse_thread(self, url: str) -> dict:
        """Parse une discussion du forum."""
        html = await self._fetch_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        thread_data = {
            'title': self._extract_text(soup, 'h1.thread-title'),
            'content': self._extract_text(soup, 'div.thread-content'),
            'author': self._extract_text(soup, 'span.thread-author'),
            'date': self._extract_text(soup, 'span.thread-date'),
            'category': self._extract_text(soup, 'div.thread-category'),
            'url': url,
            'views': self._extract_number(soup, 'span.view-count'),
            'reply_count': self._extract_number(soup, 'span.reply-count'),
            'replies': []
        }
        
        # Extraction des réponses
        reply_elements = soup.select('div.reply')
        for reply in reply_elements:
            reply_data = {
                'content': self._extract_text(reply, 'div.reply-content'),
                'author': self._extract_text(reply, 'span.reply-author'),
                'date': self._extract_text(reply, 'span.reply-date')
            }
            thread_data['replies'].append(reply_data)
        
        return thread_data

    def _extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """Extrait le texte d'un élément."""
        element = soup.select_one(selector)
        return element.text.strip() if element else ""

    def _extract_number(self, soup: BeautifulSoup, selector: str) -> int:
        """Extrait un nombre d'un élément."""
        text = self._extract_text(soup, selector)
        try:
            return int(''.join(filter(str.isdigit, text)))
        except ValueError:
            return 0

    def _save_thread(self, thread_data: dict):
        """Sauvegarde une discussion et ses réponses."""
        try:
            # Sauvegarde de la discussion
            self.cursor.execute('''
                INSERT OR REPLACE INTO yemen_forum_threads 
                (title, content, author, date, category, url, views, reply_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                thread_data['title'], thread_data['content'],
                thread_data['author'], thread_data['date'],
                thread_data['category'], thread_data['url'],
                thread_data['views'], thread_data['reply_count']
            ))
            thread_id = self.cursor.lastrowid
            
            # Sauvegarde des réponses
            for reply in thread_data['replies']:
                self.cursor.execute('''
                    INSERT INTO yemen_forum_replies 
                    (thread_id, content, author, date)
                    VALUES (?, ?, ?, ?)
                ''', (thread_id, reply['content'], reply['author'], reply['date']))
            
            # Mise à jour des statistiques utilisateur
            self.cursor.execute('''
                INSERT OR REPLACE INTO yemen_forum_users 
                (username, post_count, last_active)
                VALUES (?, 
                    COALESCE((SELECT post_count + 1 FROM yemen_forum_users WHERE username = ?), 1),
                    ?)
            ''', (thread_data['author'], thread_data['author'], thread_data['date']))
            
            self.conn.commit()
            logger.info(f"Discussion sauvegardée: {thread_data['title']}")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            self.conn.rollback()

    async def scrape_forum(self):
        """Scrape le forum Yemen Forum."""
        categories = {
            'health': '/health',
            'doctors': '/doctors',
            'hospitals': '/hospitals',
            'medical_insurance': '/medical-insurance',
            'medicine': '/medicine'
        }
        
        try:
            for category_name, category_path in categories.items():
                logger.info(f"Scraping de la catégorie: {category_name}")
                category_url = f"{self.base_url}{category_path}"
                
                try:
                    html = await self._fetch_page(category_url)
                    soup = BeautifulSoup(html, 'html.parser')
                    thread_links = soup.select('div.thread-list a.thread-link')
                    
                    for link in thread_links[:50]:  # Limite à 50 discussions par catégorie
                        thread_url = link.get('href')
                        if not thread_url.startswith('http'):
                            thread_url = f"{self.base_url}{thread_url}"
                        
                        try:
                            thread_data = await self.parse_thread(thread_url)
                            self._save_thread(thread_data)
                            await asyncio.sleep(2)  # Délai entre les requêtes
                        except Exception as e:
                            logger.error(f"Erreur lors du scraping de la discussion {thread_url}: {e}")
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
    scraper = YemenForumScraper()
    await scraper.scrape_forum()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 