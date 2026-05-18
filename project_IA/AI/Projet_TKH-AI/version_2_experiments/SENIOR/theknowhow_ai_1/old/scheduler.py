"""
Planificateur des tâches de scraping
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from app.config import SCRAPING_CONFIG
from app.utils.logger import setup_logger

logger = setup_logger("scraping_scheduler")

class ScrapingScheduler:
    """Gère la planification des tâches de scraping"""
    
    def __init__(self):
        self.tasks = {}
        self.running = False
        
    async def schedule_task(self, source_type: str, source_name: str, 
                          scraper: Any, interval: int):
        """
        Planifie une tâche de scraping
        
        Args:
            source_type: Type de source (social_media, medical_forums, etc.)
            source_name: Nom de la source
            scraper: Instance du scraper
            interval: Intervalle en secondes
        """
        task_key = f"{source_type}.{source_name}"
        
        while self.running:
            try:
                logger.info(f"Démarrage du scraping pour {task_key}")
                await scraper.run()
                logger.info(f"Scraping terminé pour {task_key}")
                
            except Exception as e:
                logger.error(f"Erreur lors du scraping de {task_key}: {e}")
                
            await asyncio.sleep(interval)
            
    async def start(self, source_types: Optional[List[str]] = None):
        """
        Démarre le planificateur
        
        Args:
            source_types: Liste des types de sources à planifier
        """
        self.running = True
        
        if source_types is None:
            source_types = list(SCRAPING_CONFIG.keys())
            
        for source_type in source_types:
            config = SCRAPING_CONFIG.get(source_type, {})
            for source_name, source_config in config.items():
                interval = source_config.get("update_interval", 3600)
                scraper = self._get_scraper(source_type, source_name)
                
                if scraper:
                    task = asyncio.create_task(
                        self.schedule_task(source_type, source_name, scraper, interval)
                    )
                    self.tasks[f"{source_type}.{source_name}"] = task
                    
        logger.info(f"Planificateur démarré pour: {', '.join(source_types)}")
        
    async def stop(self):
        """Arrête le planificateur"""
        self.running = False
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()
        logger.info("Planificateur arrêté")
        
    def _get_scraper(self, source_type: str, source_name: str) -> Optional[Any]:
        """
        Retourne l'instance du scraper approprié
        
        Args:
            source_type: Type de source
            source_name: Nom de la source
            
        Returns:
            Optional[Any]: Instance du scraper ou None
        """
        try:
            if source_type == "social_media":
                if source_name == "reddit":
                    from app.scraping.social_media.reddit import RedditScraper
                    return RedditScraper()
                elif source_name == "twitter":
                    from app.scraping.social_media.twitter import TwitterScraper
                    return TwitterScraper()
                # Ajouter d'autres scrapers...
                
            elif source_type == "medical_forums":
                if source_name == "healthunlocked":
                    from app.scraping.web.healthunlocked import HealthUnlockedScraper
                    return HealthUnlockedScraper()
                # Ajouter d'autres scrapers...
                
            elif source_type == "academic":
                if source_name == "pubmed":
                    from app.scraping.web.pubmed import PubMedScraper
                    return PubMedScraper()
                # Ajouter d'autres scrapers...
                
        except Exception as e:
            logger.error(f"Erreur lors de la création du scraper {source_type}.{source_name}: {e}")
            return None
            
        logger.warning(f"Scraper non trouvé pour {source_type}.{source_name}")
        return None 