"""
Scraper autonome pour MedHelp

RÔLE PRINCIPAL :
---------------
Ce module implémente un scraper asynchrone pour le forum MedHelp, collectant les posts médicaux
et leurs réponses d'experts. Il utilise aiohttp pour les requêtes HTTP asynchrones et BeautifulSoup
pour le parsing HTML.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Dépend de :
  * config/forums/medhelp_config.py (configuration du scraper)
  * logs/medhelp_scraper.log (fichier de logs)
  * data/database/sqlite/* (base de données)
  * scrapers/forums/base_scraper.py (classe de base)

STRUCTURE DU CONTENU :
--------------------
1. Imports et configuration
2. Classe MedHelpScraper :
   - Initialisation et configuration
   - Gestion de la base de données
   - Requêtes HTTP asynchrones
   - Parsing des pages
   - Sauvegarde des données

FONCTIONS PRINCIPALES :
---------------------
- __init__() : Initialise le scraper et la base de données
- _init_database() : Configure la base de données SQLite
- init_session() : Initialise la session HTTP asynchrone
- make_request() : Effectue des requêtes HTTP avec retries
- scrape_forum() : Scrape un forum spécifique
- _parse_posts_page() : Parse une page de posts
- scrape_posts() : Point d'entrée principal du scraping

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il est le composant principal de collecte de données MedHelp
- Il implémente le scraping asynchrone efficace
- Il gère la persistance des données
- Il assure la collecte des réponses d'experts
"""

import asyncio
import logging
import sqlite3
import os
import sys
from datetime import datetime
from typing import Optional, Dict, List, Any
from bs4 import BeautifulSoup
import aiohttp
import random

# Ajout du chemin racine au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from config.forums.medhelp_config import (
    BASE_URL,
    MAX_PAGES_PER_FORUM,
    BATCH_SIZE,
    REQUEST_DELAY,
    RANDOM_DELAY,
    MAX_RETRIES,
    RETRY_DELAY,
    DB_PATH,
    TABLE_NAME,
    SELECTORS,
    FORUM_CATEGORIES,
    HTTP_HEADERS,
    LOG_CONFIG
)

# Configuration du logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=LOG_CONFIG["level"],
    format=LOG_CONFIG["format"],
    handlers=[
        logging.FileHandler('logs/medhelp_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MedHelpScraper:
    """Scraper pour MedHelp."""
    
    def __init__(self):
        """Initialise le scraper."""
        self.base_url = BASE_URL
        self.session = None
        # Création du dossier de la base de données s'il n'existe pas
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.db_connection = self._init_database()

    def _init_database(self) -> sqlite3.Connection:
        """Initialise la base de données SQLite."""
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id TEXT PRIMARY KEY,
                author_id TEXT,
                forum_name TEXT,
                title TEXT,
                body TEXT,
                created_at TIMESTAMP,
                url TEXT,
                medical_relevance_score FLOAT,
                urgency_score FLOAT,
                has_expert_reply BOOLEAN,
                expert_id TEXT,
                expert_response TEXT,
                expert_response_date TIMESTAMP,
                views_count INTEGER,
                replies_count INTEGER,
                language TEXT,
                scraped_at TIMESTAMP
            )
        """)
        
        # Création des index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_forum ON posts(forum_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON posts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_medical_score ON posts(medical_relevance_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urgency ON posts(urgency_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expert ON posts(has_expert_reply)")
        
        connection.commit()
        return connection

    async def init_session(self):
        """Initialise la session HTTP."""
        self.session = aiohttp.ClientSession(headers=HTTP_HEADERS)

    async def close(self):
        """Ferme les connexions."""
        if self.session:
            await self.session.close()
        if self.db_connection:
            self.db_connection.close()

    async def make_request(self, url: str, params: dict = None) -> Optional[str]:
        """Fait une requête HTTP avec gestion des erreurs et retries."""
        for attempt in range(MAX_RETRIES):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 522:
                        logger.warning(f"Erreur 522 (serveur indisponible) pour {url}, tentative {attempt + 1}/{MAX_RETRIES}")
                    else:
                        logger.error(f"Erreur {response.status} pour {url}")
                        return None
                    
            except Exception as e:
                logger.error(f"Erreur lors de la requête vers {url}: {str(e)}")
            
            # Attente avant retry
            await asyncio.sleep(RETRY_DELAY)
        
        return None

    async def scrape_forum(self, forum: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape un forum spécifique."""
        posts = []
        page = 1
        
        while page <= MAX_PAGES_PER_FORUM:
            url = f"{self.base_url}/{forum['url_slug']}"
            params = {"page": page}
            
            html = await self.make_request(url, params)
            if not html:
                break
            
            new_posts = self._parse_posts_page(html, forum["name"])
            if not new_posts:
                break
            
            posts.extend(new_posts)
            logger.info(f"Page {page} scrapée: {len(new_posts)} posts trouvés")
            
            if len(posts) >= BATCH_SIZE:
                break
            
            # Délai aléatoire entre les requêtes
            delay = REQUEST_DELAY + (random.random() * RANDOM_DELAY)
            await asyncio.sleep(delay)
            
            page += 1
        
        return posts

    def _parse_posts_page(self, html: str, forum_name: str) -> List[Dict[str, Any]]:
        """Parse une page de posts."""
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        for post_element in soup.select(SELECTORS["post"]):
            try:
                post = {
                    'post_id': post_element.get('data-thread-id', ''),
                    'author_id': post_element.select_one(SELECTORS["author"]).get('data-user-id', ''),
                    'forum_name': forum_name,
                    'title': post_element.select_one(SELECTORS["title"]).text.strip(),
                    'body': post_element.select_one(SELECTORS["content"]).text.strip(),
                    'created_at': datetime.now(),  # À adapter selon le format de date
                    'url': self.base_url + post_element.select_one(SELECTORS["link"])['href'],
                    'medical_relevance_score': 0.5,  # À implémenter
                    'urgency_score': 0.3,  # À implémenter
                    'has_expert_reply': bool(post_element.select_one(SELECTORS["expert_reply"])),
                    'expert_id': None,
                    'expert_response': None,
                    'expert_response_date': None,
                    'views_count': 0,
                    'replies_count': 0,
                    'language': 'en',
                    'scraped_at': datetime.now()
                }
                posts.append(post)
            except Exception as e:
                logger.error(f"Erreur lors du parsing d'un post: {str(e)}")
                continue
        
        return posts

    async def scrape_posts(self):
        """Point d'entrée principal pour le scraping."""
        try:
            await self.init_session()
            
            for category_id, category in FORUM_CATEGORIES.items():
                logger.info(f"Scraping de la catégorie: {category['name']}")
                forum = {
                    'name': category['name'],
                    'url_slug': category['url'].lstrip('/')
                }
                posts = await self.scrape_forum(forum)
                
                # Sauvegarde dans la base de données
                cursor = self.db_connection.cursor()
                for post in posts:
                    cursor.execute("""
                        INSERT OR REPLACE INTO posts
                        (post_id, author_id, forum_name, title, body, created_at,
                         url, medical_relevance_score, urgency_score, has_expert_reply,
                         expert_id, expert_response, expert_response_date,
                         views_count, replies_count, language, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        post['post_id'], post['author_id'], post['forum_name'],
                        post['title'], post['body'], post['created_at'], post['url'],
                        post['medical_relevance_score'], post['urgency_score'],
                        post['has_expert_reply'], post['expert_id'],
                        post['expert_response'], post['expert_response_date'],
                        post['views_count'], post['replies_count'],
                        post['language'], post['scraped_at']
                    ))
                
                self.db_connection.commit()
                if len(posts) % DB_CONFIG["vacuum_frequency"] == 0:
                    self.db_connection.execute("VACUUM")
                logger.info(f"{len(posts)} posts sauvegardés pour {category['name']}")
        
        except Exception as e:
            logger.error(f"Erreur lors du scraping: {str(e)}")
            raise
        
        finally:
            await self.close()

async def main():
    """Point d'entrée du script."""
    scraper = MedHelpScraper()
    await scraper.scrape_posts()

if __name__ == "__main__":
    asyncio.run(main()) 