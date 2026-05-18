"""
Module de scraping pour les blogs médicaux.
Extrait les articles et actualités de différentes sources médicales en ligne.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.scraping.base_scraper import BaseScraper
from app.utils.text_processing import detect_language, translate_text
from app.utils.medical_validation import validate_medical_content

class MedicalBlogsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.sources = {
            "kevinmd": {
                "url": "https://www.kevinmd.com",
                "sections": {
                    "recent": "/blog",
                    "popular": "/popular",
                    "conditions": "/conditions",
                    "specialties": "/specialties"
                }
            },
            "medscape": {
                "url": "https://www.medscape.com/blogs",
                "sections": {
                    "recent": "/latest",
                    "specialties": "/specialty",
                    "lifestyle": "/lifestyle",
                    "tech": "/technology"
                }
            },
            "sciencebasedmedicine": {
                "url": "https://sciencebasedmedicine.org",
                "sections": {
                    "recent": "/blog",
                    "topics": "/topics",
                    "authors": "/authors",
                    "resources": "/resources"
                }
            }
        }
        self.medical_keywords = [
            "health", "medical", "clinical", "patient", "treatment",
            "disease", "medicine", "healthcare", "doctor", "physician",
            "diagnosis", "therapy", "research", "evidence-based"
        ]

    async def connect(self, source: str) -> bool:
        """Établit la connexion avec un blog médical."""
        try:
            self.driver.get(self.sources[source]["url"])
            await self._handle_cookie_consent()
            return True
        except Exception as e:
            logging.error(f"Erreur de connexion à {source}: {str(e)}")
            return False

    async def fetch_data(self, source: str, section: str = "recent", limit: int = 100) -> List[Dict]:
        """Récupère les données d'une section spécifique d'un blog."""
        items = []
        try:
            source_url = self.sources[source]["url"]
            section_path = self.sources[source]["sections"][section]
            self.driver.get(source_url + section_path)
            
            while len(items) < limit:
                elements = self.driver.find_elements(By.CLASS_NAME, "post-item")
                
                for element in elements:
                    if len(items) >= limit:
                        break
                        
                    item_data = await self._extract_item_data(element, source, section)
                    if item_data and await self._is_medical_content(item_data):
                        items.append(item_data)
                
                if not await self._next_page():
                    break
                    
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des données: {str(e)}")
            
        return items

    async def _extract_item_data(self, element, source: str, section: str) -> Optional[Dict]:
        """Extrait les données d'un article de blog."""
        try:
            title = element.find_element(By.CLASS_NAME, "post-title").text
            content = element.find_element(By.CLASS_NAME, "post-excerpt").text
            date_str = element.find_element(By.CLASS_NAME, "post-date").text
            
            base_data = {
                "id": element.get_attribute("data-post-id"),
                "title": title,
                "content": content,
                "language": await self._detect_content_language(content),
                "published_at": await self._parse_date(date_str),
                "url": element.find_element(By.TAG_NAME, "a").get_attribute("href"),
                "source": source,
                "section": section
            }
            
            # Ajout des métadonnées
            metadata = await self._extract_metadata(element)
            base_data.update(metadata)
            
            # Ajout des métriques
            metrics = await self._extract_metrics(element)
            base_data.update(metrics)
            
            return base_data
            
        except Exception as e:
            logging.error(f"Erreur lors de l'extraction des données: {str(e)}")
            return None

    async def _extract_metadata(self, element) -> Dict:
        """Extrait les métadonnées de l'article."""
        try:
            return {
                "author": {
                    "name": element.find_element(By.CLASS_NAME, "author-name").text,
                    "title": element.find_element(By.CLASS_NAME, "author-title").text,
                    "bio": element.find_element(By.CLASS_NAME, "author-bio").text,
                    "profile": element.find_element(By.CLASS_NAME, "author-link").get_attribute("href")
                },
                "categories": [
                    cat.text for cat in 
                    element.find_elements(By.CLASS_NAME, "post-category")
                ],
                "tags": [
                    tag.text for tag in 
                    element.find_elements(By.CLASS_NAME, "post-tag")
                ],
                "reading_time": element.find_element(By.CLASS_NAME, "reading-time").text
            }
        except Exception:
            return {}

    async def _extract_metrics(self, element) -> Dict:
        """Extrait les métriques de l'article."""
        try:
            return {
                "views": int(
                    element.find_element(By.CLASS_NAME, "post-views")
                    .text.replace(",", "")
                ),
                "comments": int(
                    element.find_element(By.CLASS_NAME, "comment-count")
                    .text.replace(",", "")
                ),
                "shares": int(
                    element.find_element(By.CLASS_NAME, "share-count")
                    .text.replace(",", "")
                ),
                "likes": int(
                    element.find_element(By.CLASS_NAME, "like-count")
                    .text.replace(",", "")
                )
            }
        except Exception:
            return {}

    async def _detect_content_language(self, text: str) -> str:
        """Détecte la langue du contenu."""
        try:
            return detect_language(text)
        except Exception:
            return "en"

    async def _is_medical_content(self, item_data: Dict) -> bool:
        """Vérifie si le contenu est médical."""
        content = item_data["content"].lower()
        title = item_data["title"].lower()
        categories = [cat.lower() for cat in item_data.get("categories", [])]
        tags = [tag.lower() for tag in item_data.get("tags", [])]
        
        has_keywords = any(
            keyword in content or keyword in title 
            for keyword in self.medical_keywords
        )
        
        has_category_keywords = any(
            keyword in cat for cat in categories 
            for keyword in self.medical_keywords
        )
        
        has_tag_keywords = any(
            keyword in tag for tag in tags 
            for keyword in self.medical_keywords
        )
        
        return has_keywords or has_category_keywords or has_tag_keywords or validate_medical_content(content)

    async def _next_page(self) -> bool:
        """Passe à la page suivante si disponible."""
        try:
            next_button = self.driver.find_element(By.CLASS_NAME, "next-page")
            if "disabled" not in next_button.get_attribute("class"):
                next_button.click()
                WebDriverWait(self.driver, 10).until(
                    EC.staleness_of(next_button)
                )
                return True
            return False
        except Exception:
            return False

    async def analyze_source_activity(self, source: str, section: str, days: int = 7) -> Dict:
        """Analyse l'activité d'une section d'un blog."""
        try:
            items = await self.fetch_data(source, section, limit=100)
            current_date = datetime.now()
            
            recent_items = [
                item for item in items
                if (current_date - item["published_at"]).days <= days
            ]
            
            analysis = {
                "total_items": len(recent_items),
                "by_category": {},
                "by_author": {},
                "by_tag": {},
                "engagement": {
                    "total_views": 0,
                    "total_comments": 0,
                    "total_shares": 0,
                    "total_likes": 0,
                    "avg_reading_time": 0
                }
            }
            
            for item in recent_items:
                # Analyse par catégorie
                for category in item.get("categories", ["unknown"]):
                    analysis["by_category"][category] = analysis["by_category"].get(category, 0) + 1
                
                # Analyse par auteur
                author = item.get("author", {}).get("name", "unknown")
                analysis["by_author"][author] = analysis["by_author"].get(author, 0) + 1
                
                # Analyse par tag
                for tag in item.get("tags", ["unknown"]):
                    analysis["by_tag"][tag] = analysis["by_tag"].get(tag, 0) + 1
                
                # Métriques d'engagement
                analysis["engagement"]["total_views"] += item.get("views", 0)
                analysis["engagement"]["total_comments"] += item.get("comments", 0)
                analysis["engagement"]["total_shares"] += item.get("shares", 0)
                analysis["engagement"]["total_likes"] += item.get("likes", 0)
                
                # Temps de lecture moyen
                reading_time = item.get("reading_time", "0").split()[0]
                analysis["engagement"]["avg_reading_time"] += int(reading_time)
            
            if recent_items:
                analysis["engagement"]["avg_reading_time"] /= len(recent_items)
            
            return analysis
            
        except Exception as e:
            logging.error(f"Erreur lors de l'analyse de l'activité: {str(e)}")
            return {}

    async def run(self, limit: int = 100) -> List[Dict]:
        """Exécute le processus complet de scraping."""
        all_items = []
        try:
            for source in self.sources:
                if await self.connect(source):
                    for section in self.sources[source]["sections"]:
                        items = await self.fetch_data(source, section, limit)
                        all_items.extend(items)
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution du scraper: {str(e)}")
        finally:
            self.cleanup()
        
        return all_items
