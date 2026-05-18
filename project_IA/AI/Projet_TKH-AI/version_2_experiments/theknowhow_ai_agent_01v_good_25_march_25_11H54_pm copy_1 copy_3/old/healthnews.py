"""
Module de scraping pour les actualités médicales.
Extrait les nouvelles de différentes sources d'information médicale.
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

class HealthNewsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.sources = {
            "medicalnewstoday": {
                "url": "https://www.medicalnewstoday.com",
                "sections": {
                    "latest": "/latest",
                    "popular": "/popular",
                    "conditions": "/categories",
                    "news": "/news"
                }
            },
            "healthline": {
                "url": "https://www.healthline.com",
                "sections": {
                    "news": "/health-news",
                    "trending": "/trending",
                    "conditions": "/health",
                    "nutrition": "/nutrition"
                }
            },
            "webmd": {
                "url": "https://www.webmd.com",
                "sections": {
                    "news": "/news/latest",
                    "health": "/health",
                    "drugs": "/drugs",
                    "living": "/living"
                }
            },
            "reuters-health": {
                "url": "https://www.reuters.com/health",
                "sections": {
                    "latest": "/latest",
                    "healthcare": "/healthcare",
                    "pharma": "/pharmaceuticals",
                    "biotech": "/biotech"
                }
            }
        }
        self.medical_keywords = [
            "health", "medical", "disease", "treatment", "research",
            "study", "clinical", "drug", "therapy", "patient",
            "healthcare", "medicine", "diagnosis", "prevention"
        ]

    async def connect(self, source: str) -> bool:
        """Établit la connexion avec une source d'actualités."""
        try:
            self.driver.get(self.sources[source]["url"])
            await self._handle_cookie_consent()
            return True
        except Exception as e:
            logging.error(f"Erreur de connexion à {source}: {str(e)}")
            return False

    async def fetch_data(self, source: str, section: str = "latest", limit: int = 100) -> List[Dict]:
        """Récupère les données d'une section spécifique."""
        items = []
        try:
            source_url = self.sources[source]["url"]
            section_path = self.sources[source]["sections"][section]
            self.driver.get(source_url + section_path)
            
            while len(items) < limit:
                elements = self.driver.find_elements(By.CLASS_NAME, "news-item")
                
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
        """Extrait les données d'un article d'actualité."""
        try:
            title = element.find_element(By.CLASS_NAME, "news-title").text
            summary = element.find_element(By.CLASS_NAME, "news-summary").text
            date_str = element.find_element(By.CLASS_NAME, "news-date").text
            
            base_data = {
                "id": element.get_attribute("data-article-id"),
                "title": title,
                "summary": summary,
                "language": await self._detect_content_language(summary),
                "published_at": await self._parse_date(date_str),
                "url": element.find_element(By.CLASS_NAME, "news-link").get_attribute("href"),
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
                    "bio": element.find_element(By.CLASS_NAME, "author-bio").text
                },
                "categories": [
                    cat.text for cat in 
                    element.find_elements(By.CLASS_NAME, "news-category")
                ],
                "tags": [
                    tag.text for tag in 
                    element.find_elements(By.CLASS_NAME, "news-tag")
                ],
                "sources": [
                    source.text for source in 
                    element.find_elements(By.CLASS_NAME, "news-source")
                ],
                "fact_checked": element.find_element(By.CLASS_NAME, "fact-check").text == "Verified"
            }
        except Exception:
            return {}

    async def _extract_metrics(self, element) -> Dict:
        """Extrait les métriques de l'article."""
        try:
            return {
                "views": int(
                    element.find_element(By.CLASS_NAME, "view-count")
                    .text.replace(",", "")
                ),
                "shares": int(
                    element.find_element(By.CLASS_NAME, "share-count")
                    .text.replace(",", "")
                ),
                "comments": int(
                    element.find_element(By.CLASS_NAME, "comment-count")
                    .text.replace(",", "")
                ),
                "reading_time": int(
                    element.find_element(By.CLASS_NAME, "reading-time")
                    .text.split()[0]
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
        content = item_data["summary"].lower()
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
        """Analyse l'activité d'une section d'une source."""
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
                    "total_shares": 0,
                    "total_comments": 0,
                    "avg_reading_time": 0
                },
                "fact_checking": {
                    "verified": 0,
                    "unverified": 0
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
                analysis["engagement"]["total_shares"] += item.get("shares", 0)
                analysis["engagement"]["total_comments"] += item.get("comments", 0)
                analysis["engagement"]["avg_reading_time"] += item.get("reading_time", 0)
                
                # Vérification des faits
                if item.get("fact_checked", False):
                    analysis["fact_checking"]["verified"] += 1
                else:
                    analysis["fact_checking"]["unverified"] += 1
            
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
