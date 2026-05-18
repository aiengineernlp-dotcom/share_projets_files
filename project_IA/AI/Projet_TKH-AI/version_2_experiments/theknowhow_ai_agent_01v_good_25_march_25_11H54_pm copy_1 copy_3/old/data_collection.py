"""
Script principal pour la phase 1 de collecte de données.
Ce script coordonne la collecte de données depuis différentes sources et les stocke dans data/databases.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Imports des scrapers de médias sociaux
from src.core.phase_1_data_collection.scrapers.social_media.twitter_scraper import TwitterScraper
from src.core.phase_1_data_collection.scrapers.social_media.facebook_scraper import FacebookScraper
from src.core.phase_1_data_collection.scrapers.social_media.reddit_scraper import RedditScraper
from src.core.phase_1_data_collection.scrapers.social_media.linkedin import LinkedInScraper
from src.core.phase_1_data_collection.scrapers.social_media.instagram import InstagramScraper
from src.core.phase_1_data_collection.scrapers.social_media.tiktok import TikTokScraper
from src.core.phase_1_data_collection.scrapers.social_media.youtube import YouTubeScraper
from src.core.phase_1_data_collection.scrapers.social_media.telegram import TelegramScraper
from src.core.phase_1_data_collection.scrapers.social_media.whatsapp import WhatsAppScraper
from src.core.phase_1_data_collection.scrapers.social_media.quora import QuoraScraper

# Imports des scrapers de sites médicaux
from src.core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper import DoctissimoScraper
from src.core.phase_1_data_collection.scrapers.medical_websites.who import WHOScraper
from src.core.phase_1_data_collection.scrapers.medical_websites.medrxiv import MedRxivScraper
from src.core.phase_1_data_collection.scrapers.medical_websites.nih import NIHScraper
from src.core.phase_1_data_collection.scrapers.medical_websites.mohap import MOHAPScraper
from src.core.phase_1_data_collection.scrapers.medical_websites.dha import DHAScraper
from src.core.phase_1_data_collection.scrapers.medical_websites.doctoruna import DoctorunaScraper
from src.core.phase_1_data_collection.scrapers.medical_websites.healthunlocked import HealthUnlockedScraper
from src.core.phase_1_data_collection.scrapers.medical_websites.medicalblogs import MedicalBlogsScraper

# Définir les chemins
DATA_DIR = "data"
LOG_DIR = os.path.join(DATA_DIR, "log")
OUTPUT_DIR = os.path.join(DATA_DIR, "databases")

# Sous-dossiers pour mieux organiser les données par source
SOCIAL_MEDIA_DIR = os.path.join(OUTPUT_DIR, "social_media")
MEDICAL_WEBSITES_DIR = os.path.join(OUTPUT_DIR, "medical_websites")
ACADEMIC_DIR = os.path.join(OUTPUT_DIR, "academic")

LOG_FILE = os.path.join(LOG_DIR, "phase1_collector.log")

# Créer les dossiers nécessaires
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SOCIAL_MEDIA_DIR, exist_ok=True)
os.makedirs(MEDICAL_WEBSITES_DIR, exist_ok=True)
os.makedirs(ACADEMIC_DIR, exist_ok=True)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("phase1_collector")

class DataCollector:
    def __init__(self):
        """Initialise le collecteur de données avec tous les scrapers."""
        self.output_dir = OUTPUT_DIR
        
        # Initialisation des scrapers de médias sociaux
        self.social_media_scrapers = {
            "twitter": TwitterScraper(),
            "facebook": FacebookScraper(),
            "reddit": RedditScraper(),
            "linkedin": LinkedInScraper(),
            "instagram": InstagramScraper(),
            "tiktok": TikTokScraper(),
            "youtube": YouTubeScraper(),
            "telegram": TelegramScraper(),
            "whatsapp": WhatsAppScraper(),
            "quora": QuoraScraper()
        }
        
        # Initialisation des scrapers de sites médicaux
        self.medical_scrapers = {
            "doctissimo": DoctissimoScraper(),
            "who": WHOScraper(),
            "medrxiv": MedRxivScraper(),
            "nih": NIHScraper(),
            "mohap": MOHAPScraper(),
            "dha": DHAScraper(),
            "doctoruna": DoctorunaScraper(),
            "healthunlocked": HealthUnlockedScraper(),
            "medicalblogs": MedicalBlogsScraper()
        }
        
    async def collect_social_media_data(self):
        """Collecte les données depuis les médias sociaux."""
        logger.info("Début de la collecte depuis les médias sociaux")
        
        for source, scraper in self.social_media_scrapers.items():
            try:
                logger.info(f"Début de la collecte depuis {source}")
                
                # Connexion à la source
                await scraper.connect()
                
                # Collecte des données
                data = await scraper.fetch_data()
                
                # Validation et enrichissement des données
                validated_data = await scraper.validate_data(data)
                enriched_data = await scraper.enrich_data(validated_data)
                
                # Sauvegarde des données
                self._save_data(source, enriched_data)
                
                logger.info(f"Collecte terminée pour {source}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la collecte depuis {source}: {e}")
                continue
    
    async def collect_medical_data(self):
        """Collecte les données depuis les sites médicaux."""
        logger.info("Début de la collecte depuis les sites médicaux")
        
        for source, scraper in self.medical_scrapers.items():
            try:
                logger.info(f"Début de la collecte depuis {source}")
                
                # Connexion à la source
                await scraper.connect()
                
                # Collecte des données
                data = await scraper.fetch_data()
                
                # Validation et enrichissement des données
                validated_data = await scraper.validate_data(data)
                enriched_data = await scraper.enrich_data(validated_data)
                
                # Sauvegarde des données
                self._save_data(source, enriched_data)
                
                logger.info(f"Collecte terminée pour {source}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la collecte depuis {source}: {e}")
                continue
                
    def _save_data(self, source: str, data: List[Dict[str, Any]]):
        """Sauvegarde les données collectées dans un fichier JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{source}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Données sauvegardées dans {filepath}")

async def main():
    """Point d'entrée principal du script."""
    logger.info("Démarrage de la collecte de données - Phase 1")
    
    collector = DataCollector()
    
    # Collecte des données des médias sociaux
    await collector.collect_social_media_data()
    
    # Collecte des données des sites médicaux
    await collector.collect_medical_data()
    
    logger.info("Collecte de données terminée")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 