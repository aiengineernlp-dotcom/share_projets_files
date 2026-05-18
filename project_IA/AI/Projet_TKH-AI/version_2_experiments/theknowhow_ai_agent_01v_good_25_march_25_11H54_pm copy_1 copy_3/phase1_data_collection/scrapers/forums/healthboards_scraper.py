"""
Scraper pour le forum HealthBoards avec mécanismes de protection.

RÔLE PRINCIPAL :
---------------
Ce module implémente un scraper spécialisé pour le forum HealthBoards, héritant de la classe BaseScraper.
Il collecte les posts médicaux, analyse leur pertinence et urgence, et stocke les résultats dans une
base de données SQLite avec gestion des sous-boards et des statuts de résolution.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Dépend de :
  * scrapers/forums/base_scraper.py (classe de base)
  * config/forums/healthboards_config.py (configuration)
  * data/database/sqlite/* (base de données)
  * logs/* (fichiers de logs)

STRUCTURE DU CONTENU :
--------------------
1. Imports et configuration
2. Classe HealthBoardsScraper :
   - Initialisation et configuration
   - Gestion de la base de données
   - Scraping des boards et sous-boards
   - Analyse des posts
   - Parsing des données
   - Sauvegarde des résultats

FONCTIONS PRINCIPALES :
---------------------
- __init__() : Initialise le scraper et la base de données
- _init_database() : Configure la base de données SQLite
- scrape_board() : Scrape un board spécifique
- _parse_posts_page() : Parse une page de posts
- _calculate_medical_relevance() : Analyse la pertinence médicale
- _calculate_urgency() : Analyse l'urgence
- scrape_posts() : Point d'entrée principal du scraping

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il est le composant principal de collecte de données HealthBoards
- Il implémente l'analyse de pertinence médicale
- Il gère la structure hiérarchique des boards
- Il assure le suivi des résolutions
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Any
from bs4 import BeautifulSoup

from phase1_data_collection.scrapers.forums.base_scraper import BaseScraper
from config.forums.healthboards_config import (
    BASE_CONFIG,
    BOARDS,
    SORT_OPTIONS,
    DB_CONFIG
)

class HealthBoardsScraper(BaseScraper):
    """Scraper pour HealthBoards avec protections intégrées."""
    
    def __init__(self):
        """Initialise le scraper HealthBoards."""
        super().__init__("healthboards")
        self.base_url = BASE_CONFIG["base_url"]
        self.db_connection = self._init_database()

    def _init_database(self) -> sqlite3.Connection:
        """Initialise la base de données SQLite."""
        connection = sqlite3.connect(DB_CONFIG["db_path"])
        cursor = connection.cursor()
        
        # Création de la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS healthboards_posts (
                post_id TEXT PRIMARY KEY,
                author_id TEXT,
                board_name TEXT,
                sub_board TEXT,
                title TEXT,
                body TEXT,
                created_at TIMESTAMP,
                url TEXT,
                medical_relevance_score FLOAT,
                urgency_score FLOAT,
                resolution_status TEXT,
                resolution_date TIMESTAMP,
                views_count INTEGER,
                replies_count INTEGER,
                last_reply_at TIMESTAMP,
                language TEXT,
                scraped_at TIMESTAMP
            )
        """)
        
        # Création des index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_board ON healthboards_posts(board_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sub_board ON healthboards_posts(sub_board)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON healthboards_posts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_medical_score ON healthboards_posts(medical_relevance_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urgency ON healthboards_posts(urgency_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resolution ON healthboards_posts(resolution_status)")
        
        connection.commit()
        return connection

    async def scrape_board(self, board: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape les posts d'un board spécifique.
        
        Args:
            board: Configuration du board à scraper
            
        Returns:
            List[Dict[str, Any]]: Liste des posts scrapés
        """
        posts = []
        for sub_board in board.get('sub_boards', ['']):  # Liste vide par défaut pour gérer les boards sans sous-catégories
            for sort_option in SORT_OPTIONS.values():
                page = 1
                while page <= BASE_CONFIG["max_pages_per_board"]:
                    url = f"{self.base_url}/{board['url_slug']}"
                    if sub_board:
                        url += f"/{sub_board}"
                    
                    params = {
                        "page": page,
                        "sort": sort_option["param"]
                    }
                    
                    response = await self.make_request(url, params=params)
                    if not response:
                        break
                    
                    new_posts = self._parse_posts_page(response.text, board["name"], sub_board)
                    if not new_posts:
                        break
                    
                    posts.extend(new_posts)
                    page += 1
                    
                    # Vérification du nombre de posts
                    if len(posts) >= BASE_CONFIG["batch_size"]:
                        break
        
        return posts

    def _parse_posts_page(self, html: str, board_name: str, sub_board: str) -> List[Dict[str, Any]]:
        """
        Parse une page de posts.
        
        Args:
            html: Contenu HTML de la page
            board_name: Nom du board
            sub_board: Nom du sous-board
            
        Returns:
            List[Dict[str, Any]]: Liste des posts parsés
        """
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        for post_element in soup.select('.thread-item'):  # Sélecteur CSS à adapter
            try:
                post = {
                    'post_id': post_element.get('data-thread-id'),
                    'author_id': post_element.select_one('.author').get('data-user-id'),
                    'board_name': board_name,
                    'sub_board': sub_board,
                    'title': post_element.select_one('.thread-title').text.strip(),
                    'body': post_element.select_one('.thread-content').text.strip(),
                    'created_at': self._parse_date(post_element.select_one('.post-date').text.strip()),
                    'url': self.base_url + post_element.select_one('.thread-link')['href'],
                    'medical_relevance_score': self._calculate_medical_relevance(post_element.text),
                    'urgency_score': self._calculate_urgency(post_element.text),
                    'resolution_status': self._get_resolution_status(post_element),
                    'resolution_date': self._get_resolution_date(post_element),
                    'views_count': self._parse_views_count(post_element),
                    'replies_count': self._parse_replies_count(post_element),
                    'last_reply_at': self._parse_last_reply_date(post_element),
                    'language': 'en',  # À améliorer avec détection de langue
                    'scraped_at': datetime.now()
                }
                posts.append(post)
            except Exception as e:
                self.logger.error(f"Erreur lors du parsing d'un post: {str(e)}")
                continue
        
        return posts

    def _calculate_medical_relevance(self, text: str) -> float:
        """Calcule le score de pertinence médicale."""
        # À implémenter avec NLP
        return 0.5

    def _calculate_urgency(self, text: str) -> float:
        """Calcule le score d'urgence."""
        # À implémenter avec NLP
        return 0.3

    def _parse_date(self, date_str: str) -> datetime:
        """Parse une date depuis une chaîne."""
        # À adapter selon le format de date de HealthBoards
        return datetime.now()  # Temporaire

    def _get_resolution_status(self, post_element) -> Optional[str]:
        """Extrait le statut de résolution si présent."""
        status_elem = post_element.select_one('.resolution-status')
        return status_elem.text.strip() if status_elem else None

    def _get_resolution_date(self, post_element) -> Optional[datetime]:
        """Extrait la date de résolution si présente."""
        date_elem = post_element.select_one('.resolution-date')
        return self._parse_date(date_elem.text.strip()) if date_elem else None

    def _parse_views_count(self, post_element) -> int:
        """Parse le nombre de vues."""
        views_elem = post_element.select_one('.views-count')
        try:
            return int(views_elem.text.strip().split()[0]) if views_elem else 0
        except (ValueError, IndexError):
            return 0

    def _parse_replies_count(self, post_element) -> int:
        """Parse le nombre de réponses."""
        replies_elem = post_element.select_one('.replies-count')
        try:
            return int(replies_elem.text.strip().split()[0]) if replies_elem else 0
        except (ValueError, IndexError):
            return 0

    def _parse_last_reply_date(self, post_element) -> Optional[datetime]:
        """Parse la date de la dernière réponse."""
        date_elem = post_element.select_one('.last-reply-date')
        return self._parse_date(date_elem.text.strip()) if date_elem else None

    async def scrape_posts(self):
        """Scrape tous les posts des boards configurés."""
        try:
            for board in BOARDS:
                self.logger.info(f"Scraping du board: {board['name']}")
                posts = await self.scrape_board(board)
                
                # Sauvegarde des posts dans la base de données
                cursor = self.db_connection.cursor()
                for post in posts:
                    cursor.execute("""
                        INSERT OR REPLACE INTO healthboards_posts
                        (post_id, author_id, board_name, sub_board, title, body,
                         created_at, url, medical_relevance_score, urgency_score,
                         resolution_status, resolution_date, views_count,
                         replies_count, last_reply_at, language, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        post['post_id'], post['author_id'], post['board_name'],
                        post['sub_board'], post['title'], post['body'],
                        post['created_at'], post['url'],
                        post['medical_relevance_score'], post['urgency_score'],
                        post['resolution_status'], post['resolution_date'],
                        post['views_count'], post['replies_count'],
                        post['last_reply_at'], post['language'], post['scraped_at']
                    ))
                
                self.db_connection.commit()
                
                # Vacuum périodique de la base
                if self.request_count % DB_CONFIG["vacuum_frequency"] == 0:
                    self.db_connection.execute("VACUUM")
        
        except Exception as e:
            self.logger.error(f"Erreur lors du scraping: {str(e)}")
            raise
        
        finally:
            self.close()

    def close(self):
        """Ferme proprement le scraper et la connexion à la base de données."""
        super().close()
        if hasattr(self, 'db_connection'):
            self.db_connection.close()

if __name__ == "__main__":
    import asyncio
    scraper = HealthBoardsScraper()
    asyncio.run(scraper.scrape_posts()) 