"""
Implémentation du scraper pour les sites web médicaux.
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging
import re
from urllib.parse import urljoin, urlparse
from ...core.base_scraper import BaseScraper
from ...config.settings import MEDICAL_KEYWORDS, REGIONS

logger = logging.getLogger(__name__)

class MedicalWebScraper(BaseScraper):
    """Scraper spécifique pour les sites web médicaux."""
    
    def __init__(self):
        """Initialise le scraper web."""
        super().__init__({})  # Pas besoin de credentials pour le web scraping
        self.target_sites = [
            {
                "url": "https://www.example-medical-forum.ae",
                "selectors": {
                    "posts": ".forum-post",
                    "title": ".post-title",
                    "content": ".post-content",
                    "author": ".post-author",
                    "date": ".post-date"
                }
            },
            # Ajoutez d'autres sites avec leurs sélecteurs spécifiques
        ]
        self.session = None
        
    async def authenticate(self) -> bool:
        """Initialisation de la session HTTP."""
        try:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': self.user_agent}
            )
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la session: {str(e)}")
            return False
            
    async def _execute_request(self, url: str, selectors: Dict[str, str]) -> Optional[Dict]:
        """Exécute une requête HTTP et parse le contenu."""
        try:
            async with self.session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    posts = []
                    for post_element in soup.select(selectors['posts']):
                        try:
                            # Extraction des données avec gestion des erreurs
                            title = post_element.select_one(selectors['title'])
                            content = post_element.select_one(selectors['content'])
                            author = post_element.select_one(selectors['author'])
                            date = post_element.select_one(selectors['date'])
                            
                            if all([title, content]):  # Vérifie les champs obligatoires
                                post = {
                                    'title': title.text.strip(),
                                    'content': content.text.strip(),
                                    'author': author.text.strip() if author else "Anonymous",
                                    'created_at': self._parse_date(date.text.strip() if date else ""),
                                    'url': url,
                                    'source': urlparse(url).netloc
                                }
                                posts.append(post)
                        except Exception as e:
                            logger.warning(f"Erreur lors du parsing d'un post: {str(e)}")
                            continue
                            
                    return {'posts': posts}
                else:
                    logger.warning(f"Statut HTTP non-200 pour {url}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Erreur lors de la requête vers {url}: {str(e)}")
            return None
            
    def _parse_date(self, date_str: str) -> datetime:
        """Parse une date depuis différents formats."""
        try:
            # Ajoutez ici différents formats de date selon les sites
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%d/%m/%Y %H:%M",
                "%B %d, %Y",
                "%Y-%m-%d"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
                    
            # Si aucun format ne correspond, retourne la date actuelle
            return datetime.now()
        except Exception:
            return datetime.now()
            
    async def search_medical_content(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """Recherche du contenu médical sur les sites web."""
        all_posts = []
        visited_urls = set()
        
        for site in self.target_sites:
            try:
                # Collecte initiale
                response = await self._execute_request(site['url'], site['selectors'])
                if response and 'posts' in response:
                    posts = response['posts']
                    
                    # Enrichissement des posts
                    for post in posts:
                        if self._is_relevant_content(post['content'], keywords):
                            post['relevance_score'] = self._calculate_relevance_score(post)
                            post['medical_category'] = self._classify_medical_category(post)
                            post['urgency_level'] = self._determine_urgency(post)
                            post['location_mentions'] = self._extract_locations(post)
                            all_posts.append(post)
                            
                    # Collecte des liens supplémentaires
                    additional_urls = await self._extract_relevant_links(site['url'], limit - len(all_posts))
                    for url in additional_urls:
                        if url not in visited_urls and len(all_posts) < limit:
                            visited_urls.add(url)
                            try:
                                sub_response = await self._execute_request(url, site['selectors'])
                                if sub_response and 'posts' in sub_response:
                                    for post in sub_response['posts']:
                                        if self._is_relevant_content(post['content'], keywords):
                                            post['relevance_score'] = self._calculate_relevance_score(post)
                                            post['medical_category'] = self._classify_medical_category(post)
                                            post['urgency_level'] = self._determine_urgency(post)
                                            post['location_mentions'] = self._extract_locations(post)
                                            all_posts.append(post)
                            except Exception as e:
                                logger.error(f"Erreur lors du scraping de {url}: {str(e)}")
                                continue
                                
            except Exception as e:
                logger.error(f"Erreur lors du scraping de {site['url']}: {str(e)}")
                continue
                
            if len(all_posts) >= limit:
                break
                
        return all_posts[:limit]
        
    async def _extract_relevant_links(self, base_url: str, limit: int) -> Set[str]:
        """Extrait les liens pertinents d'une page."""
        relevant_links = set()
        try:
            async with self.session.get(base_url, timeout=self.timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(base_url, href)
                        
                        # Vérifie si le lien est pertinent
                        if self._is_relevant_link(full_url, base_url):
                            relevant_links.add(full_url)
                            if len(relevant_links) >= limit:
                                break
                                
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des liens de {base_url}: {str(e)}")
            
        return relevant_links
        
    def _is_relevant_link(self, url: str, base_url: str) -> bool:
        """Vérifie si un lien est pertinent pour le scraping."""
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)
            
            # Vérifie si le lien est sur le même domaine
            if parsed_url.netloc != parsed_base.netloc:
                return False
                
            # Évite les liens non pertinents
            irrelevant_patterns = [
                r'/user/',
                r'/profile/',
                r'/login/',
                r'/register/',
                r'\.(jpg|jpeg|png|gif|css|js)$'
            ]
            
            return not any(re.search(pattern, url.lower()) for pattern in irrelevant_patterns)
            
        except Exception:
            return False
            
    def _is_relevant_content(self, content: str, keywords: List[str]) -> bool:
        """Vérifie si le contenu est pertinent selon les mots-clés."""
        content_lower = content.lower()
        
        # Vérifie la présence de mots-clés
        keyword_match = any(keyword.lower() in content_lower for keyword in keywords)
        
        # Vérifie la présence de termes médicaux
        medical_match = any(
            keyword.lower() in content_lower
            for category in MEDICAL_KEYWORDS.values()
            for keyword in category
        )
        
        return keyword_match and medical_match
        
    def _calculate_relevance_score(self, post: Dict) -> float:
        """Calcule un score de pertinence pour un post."""
        score = 0.0
        content = (post['title'] + ' ' + post['content']).lower()
        
        # Score basé sur les mots-clés médicaux (50%)
        keyword_matches = 0
        for category in MEDICAL_KEYWORDS.values():
            for keyword in category:
                if keyword in content:
                    keyword_matches += 1
        keyword_score = min(keyword_matches / 12, 1.0) * 0.5
        
        # Score basé sur la longueur du contenu (30%)
        content_length = len(content)
        length_score = min(content_length / 1000, 1.0) * 0.3
        
        # Score basé sur la fraîcheur (20%)
        hours_old = (datetime.now() - post['created_at']).total_seconds() / 3600
        if hours_old <= 24:
            time_score = 0.2
        elif hours_old <= 72:
            time_score = 0.15
        elif hours_old <= 168:
            time_score = 0.1
        else:
            time_score = 0.05
            
        return round(keyword_score + length_score + time_score, 3)
        
    def _classify_medical_category(self, post: Dict) -> str:
        """Classifie le post dans une catégorie médicale."""
        content = (post['title'] + ' ' + post['content']).lower()
        
        # Compte les occurrences de mots-clés par catégorie
        category_scores = {}
        for category, keywords in MEDICAL_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in content)
            category_scores[category] = score
            
        # Retourne la catégorie avec le plus de correspondances
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return "general"
        
    def _determine_urgency(self, post: Dict) -> str:
        """Détermine le niveau d'urgence d'un post."""
        content = (post['title'] + ' ' + post['content']).lower()
        
        urgent_keywords = {
            "emergency", "urgent", "help", "asap", "immediate",
            "severe pain", "bleeding", "chest pain", "difficulty breathing"
        }
        
        # Compte les mots-clés d'urgence
        urgency_count = sum(1 for keyword in urgent_keywords if keyword in content)
        
        if urgency_count >= 3:
            return "HIGH"
        elif urgency_count >= 1:
            return "MEDIUM"
        return "LOW"
        
    def _extract_locations(self, post: Dict) -> List[str]:
        """Extrait les mentions de localisation dans le post."""
        content = (post['title'] + ' ' + post['content']).lower()
        locations = []
        
        for region, cities in REGIONS.items():
            for city in cities:
                if city.lower() in content:
                    locations.append(city)
                    
        return list(set(locations))  # Supprime les doublons
        
    async def close(self):
        """Ferme la session HTTP."""
        if self.session:
            await self.session.close() 