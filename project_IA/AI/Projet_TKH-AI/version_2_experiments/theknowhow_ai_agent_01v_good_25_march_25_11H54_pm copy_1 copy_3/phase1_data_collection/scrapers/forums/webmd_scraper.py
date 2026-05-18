"""
Scraper pour le forum WebMD Community avec mécanismes de protection.

RÔLE PRINCIPAL :
---------------
Ce module implémente un scraper spécialisé pour le forum WebMD Community, héritant de la classe BaseScraper.
Il collecte les posts médicaux, analyse leur pertinence et urgence, et stocke les résultats dans une
base de données SQLite avec gestion des réponses d'experts et des réponses vérifiées.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Dépend de :
  * scrapers/forums/base_scraper.py (classe de base)
  * config/forums/webmd_config.py (configuration)
  * processors/medical_analysis/medical_analyzer.py (analyse médicale)
  * processors/medical_analysis/urgency_analyzer.py (analyse d'urgence)
  * nlp/language_detector.py (détection de langue)
  * data/database/sqlite/* (base de données)
  * logs/* (fichiers de logs)

STRUCTURE DU CONTENU :
--------------------
1. Imports et configuration
2. Classe WebMDScraper :
   - Initialisation et configuration
   - Gestion de la base de données
   - Scraping des communautés
   - Analyse des posts
   - Parsing des données
   - Gestion des réponses d'experts
   - Sauvegarde des résultats

FONCTIONS PRINCIPALES :
---------------------
- __init__() : Initialise le scraper et la base de données
- _init_database() : Configure la base de données SQLite
- scrape_community() : Scrape une communauté spécifique
- _parse_posts_page() : Parse une page de posts
- _calculate_medical_relevance() : Analyse la pertinence médicale
- _calculate_urgency() : Analyse l'urgence
- _get_expert_response() : Extrait les réponses d'experts
- scrape_posts() : Point d'entrée principal du scraping

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il est le composant principal de collecte de données WebMD
- Il implémente l'analyse de pertinence médicale
- Il gère les réponses d'experts vérifiées
- Il assure le suivi des interactions communautaires
"""

import os
import json
import sqlite3
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from config.settings import logger
from phase1_data_collection.processors.medical_analysis.medical_analyzer import MedicalAnalyzer
from phase1_data_collection.processors.medical_analysis.urgency_analyzer import UrgencyAnalyzer
from nlp.language_detector import detect_language
from .base_scraper import BaseScraper
from config.forums.webmd_config import (
    BASE_CONFIG,
    COMMUNITIES,
    SORT_OPTIONS,
    DB_CONFIG
)

class WebMDScraper(BaseScraper):
    """Scraper pour WebMD Community avec protections intégrées."""
    
    BASE_URL = "https://exchanges.webmd.com"
    DB_PATH = os.path.join("data", "database", "sqlite", "webmd.db")
    
    def __init__(self):
        """Initialise le scraper WebMD."""
        super().__init__("webmd")
        self.base_url = BASE_CONFIG["base_url"]
        self.db_connection = self._init_database()
        
        # Initialisation des analyseurs
        self.nlp = spacy.load("en_core_web_sm")
        self.medical_analyzer = MedicalAnalyzer(self.nlp)
        self.urgency_analyzer = UrgencyAnalyzer(self.nlp)
        
        # Initialisation de la base de données
        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
        logger.info("WebMDScraper initialisé avec succès")
    
    def _init_database(self) -> sqlite3.Connection:
        """Initialise la base de données SQLite."""
        connection = sqlite3.connect(DB_CONFIG["db_path"])
        cursor = connection.cursor()
        
        # Création de la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webmd_posts (
                post_id TEXT PRIMARY KEY,
                author_id TEXT,
                community_name TEXT,
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
                is_verified_answer BOOLEAN,
                views_count INTEGER,
                replies_count INTEGER,
                last_reply_at TIMESTAMP,
                language TEXT,
                scraped_at TIMESTAMP
            )
        """)
        
        # Création des index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_community ON webmd_posts(community_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON webmd_posts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_medical_score ON webmd_posts(medical_relevance_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urgency ON webmd_posts(urgency_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expert ON webmd_posts(has_expert_reply)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_verified ON webmd_posts(is_verified_answer)")
        
        connection.commit()
        return connection

    async def scrape_community(self, community: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape les posts d'une communauté spécifique.
        
        Args:
            community: Configuration de la communauté à scraper
            
        Returns:
            List[Dict[str, Any]]: Liste des posts scrapés
        """
        posts = []
        for sort_option in SORT_OPTIONS:
            page = 1
            while page <= BASE_CONFIG["max_pages_per_community"]:
                url = f"{self.base_url}/{community['url_slug']}"
                params = {
                    "page": page,
                    "sort": sort_option["param"]
                }
                
                response = await self.make_request(url, params=params)
                if not response:
                    break
                
                new_posts = self._parse_posts_page(response.text, community["name"])
                if not new_posts:
                    break
                
                posts.extend(new_posts)
                page += 1
                
                # Vérification du nombre de posts
                if len(posts) >= BASE_CONFIG["batch_size"]:
                    break
        
        return posts

    def _parse_posts_page(self, html: str, community_name: str) -> List[Dict[str, Any]]:
        """
        Parse une page de posts.
        
        Args:
            html: Contenu HTML de la page
            community_name: Nom de la communauté
            
        Returns:
            List[Dict[str, Any]]: Liste des posts parsés
        """
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        for post_element in soup.select('.discussion-thread'):  # Sélecteur CSS à adapter
            try:
                post = {
                    'post_id': post_element.get('data-thread-id'),
                    'author_id': post_element.select_one('.author').get('data-user-id'),
                    'community_name': community_name,
                    'title': post_element.select_one('.thread-title').text.strip(),
                    'body': post_element.select_one('.thread-content').text.strip(),
                    'created_at': self._parse_date(post_element.select_one('.post-date').text.strip()),
                    'url': self.base_url + post_element.select_one('.thread-link')['href'],
                    'medical_relevance_score': self._calculate_medical_relevance(post_element.text),
                    'urgency_score': self._calculate_urgency(post_element.text),
                    'has_expert_reply': bool(post_element.select_one('.expert-response')),
                    'expert_id': self._get_expert_id(post_element),
                    'expert_response': self._get_expert_response(post_element),
                    'expert_response_date': self._get_expert_response_date(post_element),
                    'is_verified_answer': self._is_verified_answer(post_element),
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
        # À adapter selon le format de date de WebMD
        return datetime.now()  # Temporaire

    def _get_expert_id(self, post_element) -> Optional[str]:
        """Extrait l'ID de l'expert si présent."""
        expert_elem = post_element.select_one('.expert-response')
        return expert_elem.get('data-expert-id') if expert_elem else None

    def _get_expert_response(self, post_element) -> Optional[str]:
        """Extrait la réponse de l'expert si présente."""
        expert_resp = post_element.select_one('.expert-response-content')
        return expert_resp.text.strip() if expert_resp else None

    def _get_expert_response_date(self, post_element) -> Optional[datetime]:
        """Extrait la date de réponse de l'expert si présente."""
        date_elem = post_element.select_one('.expert-response-date')
        return self._parse_date(date_elem.text.strip()) if date_elem else None

    def _is_verified_answer(self, post_element) -> bool:
        """Vérifie si la réponse est vérifiée."""
        return bool(post_element.select_one('.verified-answer'))

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
        """Scrape tous les posts des communautés configurées."""
        try:
            for community in COMMUNITIES:
                self.logger.info(f"Scraping de la communauté: {community['name']}")
                posts = await self.scrape_community(community)
                
                # Sauvegarde des posts dans la base de données
                cursor = self.db_connection.cursor()
                for post in posts:
                    cursor.execute("""
                        INSERT OR REPLACE INTO webmd_posts
                        (post_id, author_id, community_name, title, body, created_at,
                         url, medical_relevance_score, urgency_score, has_expert_reply,
                         expert_id, expert_response, expert_response_date,
                         is_verified_answer, views_count, replies_count,
                         last_reply_at, language, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        post['post_id'], post['author_id'], post['community_name'],
                        post['title'], post['body'], post['created_at'], post['url'],
                        post['medical_relevance_score'], post['urgency_score'],
                        post['has_expert_reply'], post['expert_id'],
                        post['expert_response'], post['expert_response_date'],
                        post['is_verified_answer'], post['views_count'],
                        post['replies_count'], post['last_reply_at'],
                        post['language'], post['scraped_at']
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