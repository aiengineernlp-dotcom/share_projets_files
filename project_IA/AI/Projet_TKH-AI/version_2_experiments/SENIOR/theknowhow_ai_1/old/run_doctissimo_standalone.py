#!/usr/bin/env python3
"""
Script autonome pour tester le scraper Doctissimo.
Ce script implémente toutes les dépendances nécessaires pour éviter les problèmes d'import.
"""

import os
import sys
import asyncio
import logging
import json
import yaml
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

# Ajouter le répertoire racine au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))  # Remonter de src/scripts à la racine
sys.path.insert(0, root_dir)

# Définir les chemins
DATA_DIR = os.path.join(root_dir, "data")
LOG_DIR = os.path.join(DATA_DIR, "log")
OUTPUT_DIR = os.path.join(DATA_DIR, "databases")
MEDICAL_WEBSITES_DIR = os.path.join(OUTPUT_DIR, "medical_websites")
DOCTISSIMO_DIR = os.path.join(MEDICAL_WEBSITES_DIR, "doctissimo")
CONFIG_DIR = os.path.join(root_dir, "config")

# Créer les dossiers nécessaires
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MEDICAL_WEBSITES_DIR, exist_ok=True)
os.makedirs(DOCTISSIMO_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "doctissimo_standalone.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("doctissimo_standalone")

# Créer une configuration minimale pour Doctissimo
doctissimo_config = {
    "base_url": "https://www.doctissimo.fr",
    "categories": ["sante", "medicaments", "maladies", "nutrition"],
    "max_articles": 5,
    "request_delay": 2.0,
    "timeout": 30,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "storage": {
        "database_path": os.path.join(DOCTISSIMO_DIR, "doctissimo.db")
    }
}

# Sauvegarder la configuration dans un fichier
config_path = os.path.join(CONFIG_DIR, "doctissimo_temp.yaml")
with open(config_path, "w") as f:
    yaml.dump(doctissimo_config, f)

# Définir une fonction de chargement de configuration simple
def load_config(config_path=None):
    """Charge la configuration depuis un fichier YAML."""
    if not config_path:
        return {}
    
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {e}")
        return {}

# Définir une classe de stockage simple
class SQLiteStorage:
    """Classe de stockage simple pour les tests."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        logger.info(f"Stockage initialisé avec la base de données: {db_path}")
    
    async def save_article(self, article_data):
        """Sauvegarde un article dans un fichier JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"doctissimo_{timestamp}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Article sauvegardé dans {filepath}")
        return True

# Définir la classe de base pour les scrapers médicaux
class BaseMedicalScraper(ABC):
    """Classe de base pour tous les scrapers de sites médicaux."""

    def __init__(self, config_path=None):
        """
        Initialise le scraper avec la configuration spécifiée.
        
        Args:
            config_path (str, optional): Chemin vers le fichier de configuration.
        """
        self.config = load_config(config_path) if config_path else {}
        self.storage = SQLiteStorage(self.config.get('storage', {}).get('database_path', 'medical_data.db'))
        self.logger = self._setup_logger()
        self.session = None
        self.max_articles = self.config.get('max_articles', 100)
        
    def _setup_logger(self):
        """Configure et retourne un logger."""
        logger_name = self.__class__.__name__
        logger = logging.getLogger(logger_name)
        return logger
        
    async def initialize(self):
        """Initialise les ressources nécessaires."""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': self.config.get('user_agent', 'Mozilla/5.0'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
        )
        
    async def cleanup(self):
        """Nettoie les ressources utilisées."""
        if self.session:
            await self.session.close()
            
    @abstractmethod
    async def scrape_page(self, url):
        """Extrait les données d'une page."""
        pass
        
    @abstractmethod
    async def extract_article_data(self, soup):
        """Extrait les données d'un article depuis la soupe HTML."""
        pass
        
    async def fetch_page(self, url):
        """Récupère le contenu HTML d'une page."""
        if not self.session:
            await self.initialize()
            
        try:
            async with self.session.get(url, timeout=self.config.get('timeout', 30)) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.error(f"Erreur lors de la récupération de {url}: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Exception lors de la récupération de {url}: {e}")
            return None
            
    def parse_html(self, html):
        """Parse le HTML en objet BeautifulSoup."""
        return BeautifulSoup(html, 'html.parser')
        
    async def save_article(self, article_data):
        """Sauvegarde un article dans le stockage."""
        try:
            await self.storage.save_article(article_data)
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de l'article: {e}")
            return False
            
    @abstractmethod
    async def run(self):
        """Exécute le scraper."""
        pass

# Définir la classe DoctissimoScraper
class DoctissimoScraper(BaseMedicalScraper):
    """Scraper spécialisé pour Doctissimo."""

    def __init__(self, config_path=None):
        """
        Initialise le scraper Doctissimo.
        
        Args:
            config_path (str, optional): Chemin vers le fichier de configuration.
        """
        super().__init__(config_path)
        self.base_url = self.config.get('base_url', 'https://www.doctissimo.fr')
        self.categories = self.config.get('categories', [
            'sante', 'medicaments', 'maladies', 'nutrition'
        ])

    async def extract_article_data(self, soup):
        """Extrait les données d'un article depuis la soupe HTML."""
        try:
            # Extraire le titre
            title = soup.find('h1')
            title_text = title.text.strip() if title else "Titre inconnu"
            
            # Extraire la date
            date_elem = soup.find('time')
            date_text = date_elem.get('datetime') if date_elem else None
            if date_text:
                try:
                    date_obj = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                    date_formatted = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    date_formatted = date_text
            else:
                date_formatted = "Date inconnue"
            
            # Extraire l'auteur
            author_elem = soup.find('span', class_='author')
            author = author_elem.text.strip() if author_elem else "Auteur inconnu"
            
            # Extraire le contenu
            content_elem = soup.find('div', class_='content-article')
            content = ""
            if content_elem:
                # Supprimer les éléments non désirés
                for elem in content_elem.find_all(['script', 'style', 'iframe']):
                    elem.decompose()
                content = content_elem.get_text(separator='\n').strip()
            
            # Extraire les tags/catégories
            tags = []
            tags_elem = soup.find('ul', class_='tags')
            if tags_elem:
                for tag in tags_elem.find_all('li'):
                    tags.append(tag.text.strip())
            
            return {
                'title': title_text,
                'date': date_formatted,
                'author': author,
                'content': content,
                'tags': tags,
                'url': soup.find('link', rel='canonical').get('href') if soup.find('link', rel='canonical') else "URL inconnue",
                'source': 'Doctissimo'
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des données: {e}")
            return None

    async def scrape_page(self, url):
        """Extrait les données d'un article."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={"User-Agent": doctissimo_config["user_agent"]}, timeout=doctissimo_config["timeout"]) as response:
                    if response.status != 200:
                        logger.error(f"Erreur lors de la récupération de la page: {response.status}")
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extraction des données avec des sélecteurs CSS plus précis
                    title_elem = soup.select_one('h1')
                    title = title_elem.text.strip() if title_elem else "Titre inconnu"
                    
                    date_elem = soup.select_one('time')
                    date_str = date_elem.get('datetime') if date_elem else None
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if not date_str else date_str
                    
                    author_elem = soup.select_one('span.author-name, span.author')
                    author = author_elem.text.strip() if author_elem else "Auteur inconnu"
                    
                    content_elem = soup.select_one('div.content-article, div.article-content')
                    content = ""
                    if content_elem:
                        # Supprimer les éléments non désirés
                        for elem in content_elem.find_all(['script', 'style', 'iframe']):
                            elem.decompose()
                        content = content_elem.get_text(separator='\n').strip()
                    
                    tags_elems = soup.select('div.tags-article a, ul.tags li')
                    tags = [tag.text.strip() for tag in tags_elems] if tags_elems else []
                    
                    # Création du dictionnaire de données
                    article_data = {
                        "title": title,
                        "date": date,
                        "author": author,
                        "content": content,
                        "tags": tags,
                        "url": url,
                        "source": "Doctissimo"
                    }
                    
                    return article_data
                    
        except Exception as e:
            logger.error(f"Erreur lors du scraping de la page {url}: {e}")
            return None

    async def get_article_urls(self, category):
        """Récupère les URLs des articles d'une catégorie."""
        category_url = f"{self.base_url}/{category}"
        self.logger.info(f"Récupération des articles de la catégorie: {category_url}")
        
        html = await self.fetch_page(category_url)
        if not html:
            return []
            
        soup = self.parse_html(html)
        article_links = []
        
        # Chercher les liens d'articles
        for article in soup.find_all('article'):
            link = article.find('a')
            if link and link.get('href'):
                url = link.get('href')
                if not url.startswith('http'):
                    url = f"{self.base_url}{url}" if url.startswith('/') else f"{self.base_url}/{url}"
                article_links.append(url)
                
                if len(article_links) >= self.max_articles:
                    break
        
        self.logger.info(f"Trouvé {len(article_links)} articles dans la catégorie {category}")
        return article_links

    async def run(self):
        """Exécute le scraper."""
        await self.initialize()
        
        try:
            for category in self.categories:
                article_urls = await self.get_article_urls(category)
                
                for url in article_urls:
                    article_data = await self.scrape_page(url)
                    if article_data:
                        await self.save_article(article_data)
                    
                    # Pause pour éviter de surcharger le serveur
                    await asyncio.sleep(self.config.get('request_delay', 2))
        finally:
            await self.cleanup()

async def main():
    """Fonction principale pour tester le scraper Doctissimo."""
    logger.info("Démarrage du test du scraper Doctissimo")
    
    try:
        # Initialiser le scraper
        scraper = DoctissimoScraper()
        logger.info(f"Stockage initialisé avec la base de données: {doctissimo_config['storage']['database_path']}")
        logger.info("Scraper Doctissimo initialisé")
        logger.info("Scraper initialisé")
        
        # Collecter les données
        for category in doctissimo_config['categories'][:1]:  # Tester seulement la première catégorie
            logger.info(f"Collecte des articles de la catégorie: {category}")
            urls = await scraper.get_article_urls(category)
            logger.info(f"URLs trouvées: {len(urls)}")
            
            for url in urls[:2]:  # Tester seulement les 2 premiers articles
                logger.info(f"Traitement de l'URL: {url}")
                article_data = await scraper.scrape_page(url)
                if article_data:
                    # Sauvegarde des données
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"doctissimo_{timestamp}.json"
                    filepath = os.path.join(DOCTISSIMO_DIR, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(article_data, f, ensure_ascii=False, indent=2)
                        
                    logger.info(f"Article sauvegardé dans {filepath}")
                    logger.info(f"Article sauvegardé: {article_data['title']}")
        
        logger.info("Test terminé avec succès")
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors du test du scraper Doctissimo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("Démarrage du test autonome du scraper Doctissimo...")
    exit_code = asyncio.run(main())
    print(f"Test terminé avec code de sortie {exit_code}. Vérifiez les logs pour plus de détails.") 