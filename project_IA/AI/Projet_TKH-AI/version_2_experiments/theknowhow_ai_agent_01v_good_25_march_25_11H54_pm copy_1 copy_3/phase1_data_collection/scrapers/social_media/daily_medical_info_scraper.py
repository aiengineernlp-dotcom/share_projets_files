"""
Scraper pour DailyMedicalInfo - Site médical en arabe
"""
import sys
import os
from pathlib import Path

# Ajout du répertoire racine au PYTHONPATH
project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.append(project_root)

import logging
import requests
import sqlite3
import spacy
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional, Any
from config.websites.dailymedicalinfo_config import CONFIG
from storage.models.post import Post, PostCreate
from phase1_data_collection.processors.medical_analysis.medical_analyzer import MedicalAnalyzer
from nlp.analysis import TextAnalyzer
from tqdm import tqdm
import time
import random

# Configuration du logging
logger = logging.getLogger("theknowhow_ai")

class DailyMedicalInfoScraper:
    def __init__(self):
        # Configuration du scraper
        self.config = CONFIG
        self.base_url = self.config['BASE_URL']
        self.headers = self.config['HTTP_HEADERS']
        
        # Initialisation du modèle NLP pour l'arabe
        try:
            self.nlp = spacy.load("xx_ent_wiki_sm")  # Modèle multilingue
            logger.info("Modèle NLP chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle spaCy: {e}")
            raise
            
        # Initialisation de l'analyseur médical
        self.medical_analyzer = MedicalAnalyzer(self.nlp)
        
        # Initialisation de la base de données
        self.init_db()
        logger.info("Scraper DailyMedicalInfo initialisé")

    def init_db(self):
        """Initialise la base de données SQLite"""
        db_path = os.getenv(self.config['DB_PATH_ENV'], 'data/daily_medical_info.db')
        db_path = os.path.join(project_root, db_path)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        logger.info(f"Connexion à la base de données établie: {db_path}")
        
        cursor = self.conn.cursor()
        
        # Création de la table des articles
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            author TEXT,
            date TEXT,
            category TEXT,
            tags TEXT,
            url TEXT UNIQUE,
            medical_relevance_score REAL,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Création de la table des commentaires
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT,
            author TEXT,
            content TEXT,
            date TEXT,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
        ''')
        
        self.conn.commit()
        logger.info("Structure de la base de données initialisée")

    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Récupère une page avec gestion des erreurs et des délais"""
        for attempt in range(self.config['MAX_RETRIES']):
            try:
                if self.config['RANDOM_DELAY']:
                    time.sleep(random.uniform(1, self.config['REQUEST_DELAY']))
                else:
                    time.sleep(self.config['REQUEST_DELAY'])
                    
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
                
            except requests.RequestException as e:
                logger.warning(f"Tentative {attempt + 1} échouée pour {url}: {str(e)}")
                if attempt < self.config['MAX_RETRIES'] - 1:
                    time.sleep(self.config['RETRY_DELAY'])
                else:
                    logger.error(f"Échec de la récupération de {url} après {self.config['MAX_RETRIES']} tentatives")
                    return None

    def extract_article_data(self, article_url: str) -> Optional[Dict[str, Any]]:
        """Extrait les données d'un article"""
        soup = self.get_page(article_url)
        if not soup:
            return None
            
        try:
            # Extraction des données avec les sélecteurs configurés
            selectors = self.config['SELECTORS']
            title = soup.select_one(selectors['title'])
            content = soup.select_one(selectors['content'])
            author = soup.select_one(selectors['author'])
            date = soup.select_one(selectors['date'])
            category = soup.select_one(selectors['category'])
            tags = soup.select(selectors['tags'])
            
            if not all([title, content]):
                logger.warning(f"Données manquantes pour l'article: {article_url}")
                return None
                
            # Analyse du contenu
            doc = self.nlp(content.get_text())
            medical_score = self.medical_analyzer.analyze_medical_relevance(doc)
            
            return {
                'id': article_url.split('/')[-1],
                'title': title.get_text().strip(),
                'content': content.get_text().strip(),
                'author': author.get_text().strip() if author else "Unknown",
                'date': date.get_text().strip() if date else datetime.now().isoformat(),
                'category': category.get_text().strip() if category else "Uncategorized",
                'tags': ','.join([tag.get_text().strip() for tag in tags]),
                'url': article_url,
                'medical_relevance_score': medical_score,
                'keywords': ','.join([token.text for token in doc if token.is_stop == False])
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données de l'article {article_url}: {str(e)}")
            return None

    def extract_comments(self, article_url: str) -> List[Dict[str, Any]]:
        """Extrait les commentaires d'un article"""
        soup = self.get_page(article_url)
        if not soup:
            return []
            
        comments = []
        try:
            for comment in soup.select(self.config['SELECTORS']['comments']):
                author = comment.find_previous(self.config['SELECTORS']['comment_author'])
                date = comment.find_previous(self.config['SELECTORS']['comment_date'])
                
                comments.append({
                    'author': author.get_text().strip() if author else "Anonymous",
                    'content': comment.get_text().strip(),
                    'date': date.get_text().strip() if date else datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des commentaires de {article_url}: {str(e)}")
            
        return comments

    def save_article(self, article_data: Dict[str, Any], comments: List[Dict[str, Any]]):
        """Sauvegarde un article et ses commentaires dans la base de données"""
        try:
            cursor = self.conn.cursor()
            
            # Insertion de l'article
            cursor.execute('''
            INSERT OR REPLACE INTO articles (
                id, title, content, author, date, category, tags, url,
                medical_relevance_score, keywords
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_data['id'], article_data['title'], article_data['content'],
                article_data['author'], article_data['date'], article_data['category'],
                article_data['tags'], article_data['url'], article_data['medical_relevance_score'],
                article_data['keywords']
            ))
            
            # Insertion des commentaires
            for comment in comments:
                cursor.execute('''
                INSERT INTO comments (article_id, author, content, date)
                VALUES (?, ?, ?, ?)
                ''', (
                    article_data['id'], comment['author'],
                    comment['content'], comment['date']
                ))
                
            self.conn.commit()
            logger.info(f"Article sauvegardé avec succès: {article_data['title']}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'article {article_data['url']}: {str(e)}")
            self.conn.rollback()

    def get_article_links(self, category_url: str) -> List[str]:
        """Récupère les liens des articles d'une catégorie"""
        article_links = []
        page = 1
        
        # D'abord, vérifier la page d'accueil
        home_url = self.base_url
        soup = self.get_page(home_url)
        if not soup:
            logger.error(f"Impossible d'accéder à la page d'accueil: {home_url}")
            return []
            
        # Vérifier la structure de la page
        logger.info(f"Structure de la page d'accueil: {soup.prettify()[:500]}")
        
        # Essayer différentes structures d'URL possibles
        url_patterns = [
            f"{self.base_url}{category_url}/page/{page}",
            f"{self.base_url}/category{category_url}/page/{page}",
            f"{self.base_url}/ar{category_url}/page/{page}",
            f"{self.base_url}/blog{category_url}/page/{page}"
        ]
        
        for pattern in url_patterns:
            url = pattern
            soup = self.get_page(url)
            if soup:
                logger.info(f"Structure d'URL valide trouvée: {url}")
                break
                
        if not soup:
            logger.error(f"Aucune structure d'URL valide trouvée pour la catégorie {category_url}")
            return []
            
        while page <= self.config['MAX_PAGES_PER_CATEGORY']:
            links = soup.select(self.config['SELECTORS']['article_links'])
            if not links:
                break
                
            article_links.extend([link['href'] for link in links])
            page += 1
            
            # Mettre à jour l'URL pour la page suivante
            url = pattern.replace(f"/page/{page-1}", f"/page/{page}")
            soup = self.get_page(url)
            if not soup:
                break
                
        return article_links

    def scrape_category(self, category_path: str):
        """Scrape tous les articles d'une catégorie"""
        logger.info(f"Début du scraping de la catégorie: {category_path}")
        
        article_links = self.get_article_links(category_path)
        logger.info(f"Nombre d'articles trouvés: {len(article_links)}")
        
        for url in tqdm(article_links, desc=f"Scraping {category_path}"):
            article_data = self.extract_article_data(url)
            if article_data:
                comments = self.extract_comments(url)
                self.save_article(article_data, comments)

    def run(self):
        """Lance le scraping de toutes les catégories"""
        logger.info("Démarrage du scraping DailyMedicalInfo")
        
        for category_name, category_path in self.config['CATEGORIES'].items():
            logger.info(f"Traitement de la catégorie: {category_name}")
            self.scrape_category(category_path)
            
        logger.info("Scraping DailyMedicalInfo terminé")

if __name__ == "__main__":
    scraper = DailyMedicalInfoScraper()
    scraper.run() 