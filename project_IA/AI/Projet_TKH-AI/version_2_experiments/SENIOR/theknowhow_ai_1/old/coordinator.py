"""
Coordinateur central pour tous les scrapers
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.config import SCRAPING_CONFIG
from app.utils.logger import setup_logger
from app.scraping.social_media.reddit import RedditScraper
from app.scraping.social_media.twitter import TwitterScraper
# Importer les autres scrapers...

logger = setup_logger("scraping_coordinator")

class ScrapingCoordinator:
    """Coordonne l'exécution de tous les scrapers"""
    
    def __init__(self):
        """Initialise le coordinateur avec tous les scrapers disponibles"""
        self.scrapers = {
            "social_media": {
                "reddit": RedditScraper("reddit", "social_media"),
                "twitter": TwitterScraper("twitter", "social_media"),
                # Ajouter les autres scrapers...
            },
            "medical_forums": {
                # Ajouter les scrapers de forums...
            },
            "academic": {
                # Ajouter les scrapers académiques...
            }
        }
        
        self.active_tasks = {}
    
    async def start_scraping(self, source_types: Optional[List[str]] = None):
        """
        Lance le scraping pour les types de sources spécifiés
        
        Args:
            source_types: Liste des types de sources à scraper. Si None, scrape tout.
        """
        if source_types is None:
            source_types = list(self.scrapers.keys())
            
        tasks = []
        for source_type in source_types:
            if source_type in self.scrapers:
                for source_name, scraper in self.scrapers[source_type].items():
                    task = asyncio.create_task(
                        self._run_scraper(source_type, source_name, scraper)
                    )
                    tasks.append(task)
                    self.active_tasks[f"{source_type}.{source_name}"] = task
                    
        logger.info(f"Démarrage du scraping pour: {', '.join(source_types)}")
        await asyncio.gather(*tasks)
    
    async def stop_scraping(self, source_types: Optional[List[str]] = None):
        """
        Arrête le scraping pour les types de sources spécifiés
        
        Args:
            source_types: Liste des types de sources à arrêter. Si None, arrête tout.
        """
        if source_types is None:
            source_types = list(self.scrapers.keys())
            
        for source_type in source_types:
            for source_name in self.scrapers.get(source_type, {}):
                task_key = f"{source_type}.{source_name}"
                if task_key in self.active_tasks:
                    self.active_tasks[task_key].cancel()
                    logger.info(f"Arrêt du scraping pour {task_key}")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Récupère le statut de tous les scrapers actifs
        
        Returns:
            Dict: Statut de chaque scraper
        """
        status = {}
        for source_type, scrapers in self.scrapers.items():
            status[source_type] = {}
            for source_name, scraper in scrapers.items():
                task_key = f"{source_type}.{source_name}"
                status[source_type][source_name] = {
                    "active": task_key in self.active_tasks,
                    "metrics": scraper.metrics if hasattr(scraper, "metrics") else {}
                }
        return status
    
    async def _run_scraper(self, source_type: str, source_name: str, scraper: Any):
        """
        Exécute un scraper en continu selon sa configuration
        
        Args:
            source_type: Type de source
            source_name: Nom de la source
            scraper: Instance du scraper
        """
        config = SCRAPING_CONFIG.get(source_type, {}).get(source_name, {})
        update_interval = config.get("update_interval", 3600)  # Par défaut 1h
        
        try:
            while True:
                logger.info(f"Démarrage du cycle de scraping pour {source_type}.{source_name}")
                scraper.start_metrics()
                
                try:
                    # Connexion
                    if not await scraper.connect():
                        raise Exception("Échec de la connexion")
                    
                    # Collecte des données
                    data = await scraper.fetch_data()
                    if data:
                        # Sauvegarde des données brutes
                        await scraper.save_data(data, is_processed=False)
                        
                        # Traitement et sauvegarde des données enrichies
                        processed_data = await scraper.process_data(data)
                        await scraper.save_data(processed_data, is_processed=True)
                        
                except Exception as e:
                    logger.error(f"Erreur lors du scraping de {source_type}.{source_name}: {e}")
                    scraper.increment_metric("errors_count")
                
                metrics = scraper.end_metrics()
                logger.info(
                    f"Cycle de scraping terminé pour {source_type}.{source_name}. "
                    f"Items collectés: {metrics['items_collected']}, "
                    f"Erreurs: {metrics['errors_count']}"
                )
                
                # Attente avant le prochain cycle
                await asyncio.sleep(update_interval)
                
        except asyncio.CancelledError:
            logger.info(f"Scraping arrêté pour {source_type}.{source_name}")
        except Exception as e:
            logger.error(f"Erreur fatale pour {source_type}.{source_name}: {e}")
            raise 