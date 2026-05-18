"""
Fonctions utilitaires pour le scraping
"""
import random
from typing import Dict, List, Optional
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from app.utils.logger import setup_logger

logger = setup_logger("scraper_utils")

class ProxyManager:
    """Gestionnaire de proxies"""
    
    def __init__(self, proxy_list: Optional[List[str]] = None):
        self.proxies = proxy_list or []
        self.current_index = 0
        
    def add_proxy(self, proxy: str):
        """Ajoute un proxy à la liste"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            
    def get_next_proxy(self) -> Optional[str]:
        """Retourne le prochain proxy dans la rotation"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
        
    def remove_proxy(self, proxy: str):
        """Retire un proxy de la liste"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.current_index = min(self.current_index, len(self.proxies) - 1)

class UserAgentRotator:
    """Gestionnaire de User-Agents"""
    
    def __init__(self):
        self.ua = UserAgent()
        
    def get_random_user_agent(self) -> str:
        """Retourne un User-Agent aléatoire"""
        return self.ua.random

class RequestsManager:
    """Gestionnaire de requêtes HTTP"""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None,
                 ua_rotator: Optional[UserAgentRotator] = None):
        self.proxy_manager = proxy_manager or ProxyManager()
        self.ua_rotator = ua_rotator or UserAgentRotator()
        self.session = requests.Session()
        
    def get_headers(self) -> Dict[str, str]:
        """Retourne les en-têtes HTTP"""
        return {
            "User-Agent": self.ua_rotator.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        
    async def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Effectue une requête GET
        
        Args:
            url: URL à requêter
            **kwargs: Arguments supplémentaires pour requests
            
        Returns:
            Optional[requests.Response]: Réponse ou None en cas d'erreur
        """
        try:
            headers = kwargs.pop("headers", {})
            headers.update(self.get_headers())
            
            proxy = self.proxy_manager.get_next_proxy()
            if proxy:
                kwargs["proxies"] = {"http": proxy, "https": proxy}
                
            response = self.session.get(url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la requête GET vers {url}: {e}")
            if proxy:
                self.proxy_manager.remove_proxy(proxy)
            return None

class HTMLParser:
    """Analyseur de contenu HTML"""
    
    @staticmethod
    def parse_html(content: str) -> BeautifulSoup:
        """Parse le contenu HTML"""
        return BeautifulSoup(content, "html.parser")
        
    @staticmethod
    def extract_text(element) -> str:
        """Extrait le texte d'un élément"""
        return element.get_text(strip=True) if element else ""
        
    @staticmethod
    def extract_attribute(element, attribute: str) -> Optional[str]:
        """Extrait un attribut d'un élément"""
        return element.get(attribute) if element else None

class RateLimiter:
    """Gestionnaire de limitation de requêtes"""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.delay = 1.0 / requests_per_second
        self.last_request_time = 0
        
    async def wait(self):
        """Attend le délai nécessaire avant la prochaine requête"""
        import time
        import asyncio
        
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.delay:
            await asyncio.sleep(self.delay - time_since_last_request)
            
        self.last_request_time = time.time() 