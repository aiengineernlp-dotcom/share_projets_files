"""
Scraper de base pour les sites web médicaux
"""

import asyncio
import logging
import os
import random
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import spacy

# Chargement des variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)

class BaseWebScraper:
    """Classe de base pour les scrapers de sites web médicaux."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialise le scraper avec la configuration fournie."""
        self.config = config
        self.base_url = config['BASE_URL']
        self.db_path = os.getenv(config['DB_PATH_ENV'])
        self.session = None
        self.soup = None
        self.nlp = spacy.load('en_core_web_sm')
        logger.info("Modèle NLP en_core_web_sm chargé avec succès")
        
        # Initialisation de la base de données
        self._init_db()
    
    def _init_db(self):
        """Initialise la base de données SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info("Connexion à la base de données établie")

            # Création des tables si elles n'existent pas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    author TEXT,
                    date TEXT,
                    category TEXT,
                    url TEXT UNIQUE,
                    tags TEXT,
                    medical_relevance REAL
                )
            ''')
            logger.info("Table posts créée ou déjà existante")

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    post_count INTEGER DEFAULT 0,
                    last_post_date TEXT
                )
            ''')
            logger.info("Table users créée ou déjà existante")

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    content TEXT,
                    author TEXT,
                    date TEXT,
                    FOREIGN KEY (post_id) REFERENCES posts (id)
                )
            ''')
            logger.info("Table responses créée ou déjà existante")

            self.conn.commit()
            logger.info("Initialisation de la base de données terminée")

        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            raise
    
    async def _init_session(self):
        """Initialise la session HTTP."""
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.config['HTTP_HEADERS'])
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _fetch_page(self, url: str) -> str:
        """Récupère une page web avec gestion des erreurs et retry."""
        await self._init_session()
        
        # Ajout d'un délai aléatoire si configuré
        if self.config['RANDOM_DELAY']:
            delay = self.config['REQUEST_DELAY'] * (1 + random.random())
        else:
            delay = self.config['REQUEST_DELAY']
        
        await asyncio.sleep(delay)
        
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    
    def _calculate_medical_relevance(self, text: str) -> float:
        """
        Calcule la pertinence médicale d'un texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            float: Score de pertinence médicale entre 0 et 1
        """
        doc = self.nlp(text)
        medical_terms = set(self.config['KEYWORDS'])
        text_terms = set(token.text.lower() for token in doc)
        
        intersection = medical_terms.intersection(text_terms)
        if not medical_terms:
            return 0.0
            
        return len(intersection) / len(medical_terms)
    
    async def parse_article(self, article_url: str) -> dict:
        """
        Parse une page d'article et extrait les informations.
        
        Args:
            article_url: URL de l'article à parser
            
        Returns:
            dict: Données extraites de l'article
        """
        html = await self._fetch_page(article_url)
        self.soup = BeautifulSoup(html, 'html.parser')
        
        title = self.soup.select_one(self.config['SELECTORS']['title'])
        content = self.soup.select_one(self.config['SELECTORS']['content'])
        author = self.soup.select_one(self.config['SELECTORS']['author'])
        date = self.soup.select_one(self.config['SELECTORS']['date'])
        category = self.soup.select_one(self.config['SELECTORS']['category'])
        tags = self.soup.select(self.config['SELECTORS']['tags'])
        
        article_data = {
            'title': title.text.strip() if title else '',
            'content': content.text.strip() if content else '',
            'author': author.text.strip() if author else '',
            'date': date.text.strip() if date else '',
            'category': category.text.strip() if category else '',
            'url': article_url,
            'tags': [tag.text.strip() for tag in tags] if tags else []
        }
        
        article_data['medical_relevance'] = self._calculate_medical_relevance(
            f"{article_data['title']} {article_data['content']}"
        )
        
        return article_data
    
    async def scrape_articles(self):
        """Scrape les articles de toutes les catégories."""
        try:
            for category_name, category_path in self.config['CATEGORIES'].items():
                logger.info(f"Scraping de la catégorie: {category_name}")
                category_url = f"{self.base_url}{category_path}"
                
                html = await self._fetch_page(category_url)
                self.soup = BeautifulSoup(html, 'html.parser')
                
                article_links = self.soup.select(self.config['SELECTORS']['article_links'])
                for link in article_links[:self.config['MAX_PAGES_PER_CATEGORY']]:
                    article_url = link.get('href')
                    if not article_url.startswith('http'):
                        article_url = f"{self.base_url}{article_url}"
                        
                    try:
                        article_data = await self.parse_article(article_url)
                        self._save_article(article_data)
                        await asyncio.sleep(self.config['REQUEST_DELAY'])
                    except Exception as e:
                        logger.error(f"Erreur lors du scraping de l'article {article_url}: {e}")
                        continue
        finally:
            await self.close()
    
    async def close(self):
        """Ferme les connexions."""
        if self.session:
            await self.session.close()
        if hasattr(self, 'conn'):
            self.conn.close() 