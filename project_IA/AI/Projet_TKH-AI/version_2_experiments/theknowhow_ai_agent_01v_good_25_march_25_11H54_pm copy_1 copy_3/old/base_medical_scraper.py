"""
Classe de base pour les scrapers de sites web médicaux.
Cette classe fournit les fonctionnalités communes à tous les scrapers de sites médicaux.
"""

import os
import logging
import aiohttp
import asyncio
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import json

from src.core.phase_1_data_collection.storage.sqlite_storage import SQLiteStorage
from src.core.utils.config import load_config

class BaseMedicalScraper(ABC):
    """Classe de base pour tous les scrapers de sites médicaux."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le scraper avec la configuration spécifiée.
        
        Args:
            config_path (str, optional): Chemin vers le fichier de configuration.
        """
        self.config = load_config(config_path) if config_path else {}
        
        # Utiliser la variable d'environnement MEDICAL_DB_PATH si elle existe
        db_path = os.environ.get('MEDICAL_DB_PATH', 'data/databases/medical_websites/medical_data.db')
        self.storage = SQLiteStorage(self.config.get('storage', {}).get('database_path', db_path))
        
        self.logger = self._setup_logger()
        self.session = None
        self.metrics = {
            'pages_scraped': 0,
            'articles_collected': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }

    def _setup_logger(self) -> logging.Logger:
        """Configure le logger pour le scraper."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Ajout d'un handler pour fichier si spécifié dans la config
            if self.config.get('logging', {}).get('file_path'):
                file_handler = logging.FileHandler(
                    self.config['logging']['file_path']
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        
        return logger

    async def initialize(self):
        """Initialise les ressources nécessaires pour le scraping."""
        self.session = aiohttp.ClientSession(
            headers=self.config.get('headers', {})
        )
        await self.storage.initialize()
        self.metrics['start_time'] = datetime.now()

    async def cleanup(self):
        """Nettoie les ressources utilisées."""
        if self.session:
            await self.session.close()
        await self.storage.close()
        self.metrics['end_time'] = datetime.now()

    @abstractmethod
    async def scrape_page(self, url: str) -> Dict[str, Any]:
        """
        Scrape une page spécifique.
        
        Args:
            url (str): URL de la page à scraper.
            
        Returns:
            Dict[str, Any]: Données scrapées de la page.
        """
        pass

    @abstractmethod
    async def extract_article_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extrait les données d'un article à partir du HTML.
        
        Args:
            soup (BeautifulSoup): Objet BeautifulSoup de la page.
            
        Returns:
            Dict[str, Any]: Données extraites de l'article.
        """
        pass

    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Récupère le contenu HTML d'une page.
        
        Args:
            url (str): URL de la page à récupérer.
            
        Returns:
            Optional[str]: Contenu HTML de la page ou None en cas d'erreur.
        """
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.error(
                        f"Erreur lors de la récupération de {url}: {response.status}"
                    )
                    self.metrics['errors'] += 1
                    return None
        except Exception as e:
            self.logger.error(f"Exception lors de la récupération de {url}: {str(e)}")
            self.metrics['errors'] += 1
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse le HTML en utilisant BeautifulSoup.
        
        Args:
            html (str): Contenu HTML à parser.
            
        Returns:
            BeautifulSoup: Objet BeautifulSoup parsé.
        """
        return BeautifulSoup(html, 'html.parser')

    async def save_article(self, article_data: Dict[str, Any]):
        """
        Sauvegarde les données d'un article.
        
        Args:
            article_data (Dict[str, Any]): Données de l'article à sauvegarder.
        """
        try:
            await self.storage.save_medical_article(article_data)
            self.metrics['articles_collected'] += 1
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de l'article: {str(e)}")
            self.metrics['errors'] += 1

    def create_backup(self):
        """Crée une sauvegarde des données collectées."""
        try:
            backup_path = self.config.get('storage', {}).get('backup_path')
            if backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = os.path.join(
                    backup_path, 
                    f"medical_data_backup_{timestamp}.json"
                )
                with open(backup_file, 'w') as f:
                    json.dump(self.metrics, f)
                self.logger.info(f"Sauvegarde créée: {backup_file}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de la sauvegarde: {str(e)}")
            self.metrics['errors'] += 1

    @abstractmethod
    async def run(self):
        """
        Exécute le processus de scraping.
        Cette méthode doit être implémentée par les classes enfants.
        """
        pass 