"""
Gestionnaire de proxies pour le scraping
"""
import os
import json
import random
from typing import Dict, List, Optional
import requests
import aiohttp
from datetime import datetime, timedelta

from app.utils.logger import setup_logger

logger = setup_logger("proxy_manager")

class Proxy:
    """Représente un proxy avec ses métadonnées"""
    
    def __init__(self, host: str, port: int, username: Optional[str] = None,
                 password: Optional[str] = None, protocol: str = "http"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.protocol = protocol
        self.last_used = None
        self.failures = 0
        self.success = 0
        
    @property
    def url(self) -> str:
        """Retourne l'URL complète du proxy"""
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.protocol}://{auth}{self.host}:{self.port}"
        
    @property
    def is_available(self) -> bool:
        """Vérifie si le proxy est disponible"""
        if self.failures >= 3:  # Blacklist après 3 échecs
            return False
        if self.last_used and datetime.now() - self.last_used < timedelta(seconds=1):
            return False
        return True
        
    def mark_success(self):
        """Marque une utilisation réussie"""
        self.success += 1
        self.failures = 0
        self.last_used = datetime.now()
        
    def mark_failure(self):
        """Marque un échec"""
        self.failures += 1
        self.last_used = datetime.now()

class ProxyPool:
    """Gère un pool de proxies"""
    
    def __init__(self):
        self.proxies: List[Proxy] = []
        self.current_index = 0
        
    def add_proxy(self, proxy: Proxy):
        """Ajoute un proxy au pool"""
        self.proxies.append(proxy)
        
    def get_next_proxy(self) -> Optional[Proxy]:
        """Retourne le prochain proxy disponible"""
        if not self.proxies:
            return None
            
        # Recherche du prochain proxy disponible
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            if proxy.is_available:
                return proxy
                
            attempts += 1
            
        return None
        
    def remove_proxy(self, proxy: Proxy):
        """Retire un proxy du pool"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            
    async def test_proxy(self, proxy: Proxy) -> bool:
        """
        Teste un proxy
        
        Args:
            proxy: Proxy à tester
            
        Returns:
            bool: True si le proxy fonctionne
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://httpbin.org/ip",
                    proxy=proxy.url,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        proxy.mark_success()
                        return True
                        
            proxy.mark_failure()
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors du test du proxy {proxy.url}: {e}")
            proxy.mark_failure()
            return False

class ProxyManager:
    """Gestionnaire principal des proxies"""
    
    def __init__(self):
        self.pool = ProxyPool()
        self.bright_data_enabled = os.getenv("BRIGHT_DATA_ENABLED", "false").lower() == "true"
        self.scraper_api_enabled = os.getenv("SCRAPER_API_ENABLED", "false").lower() == "true"
        
    async def initialize(self):
        """Initialise le gestionnaire avec différentes sources de proxies"""
        # Configuration BrightData
        if self.bright_data_enabled:
            await self._setup_bright_data()
            
        # Configuration ScraperAPI
        if self.scraper_api_enabled:
            await self._setup_scraper_api()
            
        # Ajout de proxies gratuits
        await self._add_free_proxies()
        
    async def _setup_bright_data(self):
        """Configure les proxies BrightData"""
        username = os.getenv("BRIGHT_DATA_USERNAME")
        password = os.getenv("BRIGHT_DATA_PASSWORD")
        
        if username and password:
            proxy = Proxy(
                host="brd.superproxy.io",
                port=22225,
                username=username,
                password=password,
                protocol="http"
            )
            self.pool.add_proxy(proxy)
            
    async def _setup_scraper_api(self):
        """Configure ScraperAPI"""
        api_key = os.getenv("SCRAPER_API_KEY")
        
        if api_key:
            proxy = Proxy(
                host="proxy-server.scraperapi.com",
                port=8001,
                username=api_key,
                protocol="http"
            )
            self.pool.add_proxy(proxy)
            
    async def _add_free_proxies(self):
        """Ajoute des proxies gratuits depuis différentes sources"""
        # ProxyScrape
        try:
            response = requests.get(
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            )
            
            if response.status_code == 200:
                for line in response.text.split("\n"):
                    if ":" in line:
                        host, port = line.strip().split(":")
                        proxy = Proxy(host=host, port=int(port))
                        if await self.pool.test_proxy(proxy):
                            self.pool.add_proxy(proxy)
                            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des proxies gratuits: {e}")
            
    async def get_proxy(self) -> Optional[Proxy]:
        """Retourne un proxy disponible"""
        return self.pool.get_next_proxy()
        
    def mark_proxy_success(self, proxy: Proxy):
        """Marque un proxy comme fonctionnel"""
        proxy.mark_success()
        
    def mark_proxy_failure(self, proxy: Proxy):
        """Marque un proxy comme défaillant"""
        proxy.mark_failure()
        if not proxy.is_available:
            self.pool.remove_proxy(proxy) 