"""
Module de scraping pour les journaux médicaux.
Extrait les articles scientifiques de différentes revues médicales majeures.
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

class MedicalJournalsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.journals = {
            "nejm": {
                "url": "https://www.nejm.org",
                "sections": {
                    "current": "/current",
                    "recent": "/recent",
                    "specialties": "/medical-specialties",
                    "multimedia": "/multimedia"
                }
            },
            "lancet": {
                "url": "https://www.thelancet.com",
                "sections": {
                    "current": "/current",
                    "online-first": "/online-first",
                    "specialties": "/clinical/specialties",
                    "collections": "/collections"
                }
            },
            "jama": {
                "url": "https://jamanetwork.com",
                "sections": {
                    "current": "/current",
                    "online-first": "/online-first",
                    "specialties": "/collections/specialties",
                    "clinical-reviews": "/clinical-reviews"
                }
            },
            "bmj": {
                "url": "https://www.bmj.com",
                "sections": {
                    "latest": "/content/latest",
                    "research": "/research",
                    "education": "/education",
                    "news": "/news"
                }
            }
        }
        self.medical_keywords = [
            "clinical", "medical", "health", "disease", "treatment",
            "therapy", "diagnosis", "prognosis", "epidemiology",
            "pathology", "medicine", "biomedical", "therapeutic"
        ]

    async def connect(self, journal: str) -> bool:
        """Établit la connexion avec un journal médical."""
        try:
            self.driver.get(self.journals[journal]["url"])
            await self._handle_cookie_consent()
            await self._handle_login(journal)
            return True
        except Exception as e:
            logging.error(f"Erreur de connexion à {journal}: {str(e)}")
            return False

    async def _handle_login(self, journal: str) -> None:
        """Gère la connexion au journal si nécessaire."""
        try:
            if journal == "nejm":
                username = self.driver.find_element(By.ID, "username")
                password = self.driver.find_element(By.ID, "password")
                username.send_keys(self.config["NEJM_USERNAME"])
                password.send_keys(self.config["NEJM_PASSWORD"])
            elif journal == "lancet":
                username = self.driver.find_element(By.ID, "user-email")
                password = self.driver.find_element(By.ID, "user-password")
                username.send_keys(self.config["LANCET_USERNAME"])
                password.send_keys(self.config["LANCET_PASSWORD"])
            # Ajouter d'autres journaux selon les besoins
            
            login_button = self.driver.find_element(By.CLASS_NAME, "login-button")
            login_button.click()
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-profile"))
            )
        except Exception as e:
            logging.error(f"Erreur lors de la connexion: {str(e)}")

    async def fetch_data(self, journal: str, section: str = "current", limit: int = 100) -> List[Dict]:
        """Récupère les données d'une section spécifique d'un journal."""
        items = []
        try:
            journal_url = self.journals[journal]["url"]
            section_path = self.journals[journal]["sections"][section]
            self.driver.get(journal_url + section_path)
            
            while len(items) < limit:
                elements = self.driver.find_elements(By.CLASS_NAME, "article-item")
                
                for element in elements:
                    if len(items) >= limit:
                        break
                        
                    item_data = await self._extract_item_data(element, journal, section)
                    if item_data and await self._is_medical_content(item_data):
                        items.append(item_data)
                
                if not await self._next_page():
                    break
                    
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des données: {str(e)}")
            
        return items

    async def _extract_item_data(self, element, journal: str, section: str) -> Optional[Dict]:
        """Extrait les données d'un article scientifique."""
        try:
            title = element.find_element(By.CLASS_NAME, "article-title").text
            abstract = element.find_element(By.CLASS_NAME, "article-abstract").text
            date_str = element.find_element(By.CLASS_NAME, "publication-date").text
            
            base_data = {
                "doi": element.get_attribute("data-doi"),
                "title": title,
                "abstract": abstract,
                "language": "en",
                "published_at": await self._parse_date(date_str),
                "url": element.find_element(By.CLASS_NAME, "article-link").get_attribute("href"),
                "journal": journal,
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
                "authors": [
                    author.text for author in 
                    element.find_elements(By.CLASS_NAME, "author-name")
                ],
                "affiliations": [
                    aff.text for aff in 
                    element.find_elements(By.CLASS_NAME, "author-affiliation")
                ],
                "keywords": [
                    kw.text for kw in 
                    element.find_elements(By.CLASS_NAME, "keyword")
                ],
                "article_type": element.find_element(By.CLASS_NAME, "article-type").text,
                "specialties": [
                    spec.text for spec in 
                    element.find_elements(By.CLASS_NAME, "specialty")
                ],
                "funding": [
                    fund.text for fund in 
                    element.find_elements(By.CLASS_NAME, "funding-source")
                ]
            }
        except Exception:
            return {}

    async def _extract_metrics(self, element) -> Dict:
        """Extrait les métriques de l'article."""
        try:
            return {
                "citations": int(
                    element.find_element(By.CLASS_NAME, "citation-count")
                    .text.replace(",", "")
                ),
                "views": int(
                    element.find_element(By.CLASS_NAME, "view-count")
                    .text.replace(",", "")
                ),
                "downloads": int(
                    element.find_element(By.CLASS_NAME, "download-count")
                    .text.replace(",", "")
                ),
                "altmetric_score": float(
                    element.find_element(By.CLASS_NAME, "altmetric-score").text
                ),
                "impact_factor": float(
                    element.find_element(By.CLASS_NAME, "impact-factor").text
                )
            }
        except Exception:
            return {}

    async def _is_medical_content(self, item_data: Dict) -> bool:
        """Vérifie si le contenu est médical."""
        content = item_data["abstract"].lower()
        title = item_data["title"].lower()
        keywords = [kw.lower() for kw in item_data.get("keywords", [])]
        specialties = [spec.lower() for spec in item_data.get("specialties", [])]
        
        has_keywords = any(
            keyword in content or keyword in title 
            for keyword in self.medical_keywords
        )
        
        has_keyword_match = any(
            keyword in kw for kw in keywords 
            for keyword in self.medical_keywords
        )
        
        has_specialty_match = any(
            keyword in spec for spec in specialties 
            for keyword in self.medical_keywords
        )
        
        return has_keywords or has_keyword_match or has_specialty_match or validate_medical_content(content)

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

    async def analyze_journal_activity(self, journal: str, section: str, days: int = 7) -> Dict:
        """Analyse l'activité d'une section d'un journal."""
        try:
            items = await self.fetch_data(journal, section, limit=100)
            current_date = datetime.now()
            
            recent_items = [
                item for item in items
                if (current_date - item["published_at"]).days <= days
            ]
            
            analysis = {
                "total_items": len(recent_items),
                "by_specialty": {},
                "by_article_type": {},
                "by_institution": {},
                "metrics": {
                    "total_citations": 0,
                    "total_views": 0,
                    "total_downloads": 0,
                    "avg_impact_factor": 0.0,
                    "avg_altmetric": 0.0
                }
            }
            
            for item in recent_items:
                # Analyse par spécialité
                for specialty in item.get("specialties", ["unknown"]):
                    analysis["by_specialty"][specialty] = analysis["by_specialty"].get(specialty, 0) + 1
                
                # Analyse par type d'article
                article_type = item.get("article_type", "unknown")
                analysis["by_article_type"][article_type] = analysis["by_article_type"].get(article_type, 0) + 1
                
                # Analyse par institution
                for affiliation in item.get("affiliations", ["unknown"]):
                    analysis["by_institution"][affiliation] = analysis["by_institution"].get(affiliation, 0) + 1
                
                # Métriques globales
                analysis["metrics"]["total_citations"] += item.get("citations", 0)
                analysis["metrics"]["total_views"] += item.get("views", 0)
                analysis["metrics"]["total_downloads"] += item.get("downloads", 0)
                analysis["metrics"]["avg_impact_factor"] += item.get("impact_factor", 0)
                analysis["metrics"]["avg_altmetric"] += item.get("altmetric_score", 0)
            
            if recent_items:
                analysis["metrics"]["avg_impact_factor"] /= len(recent_items)
                analysis["metrics"]["avg_altmetric"] /= len(recent_items)
            
            return analysis
            
        except Exception as e:
            logging.error(f"Erreur lors de l'analyse de l'activité: {str(e)}")
            return {}

    async def run(self, limit: int = 100) -> List[Dict]:
        """Exécute le processus complet de scraping."""
        all_items = []
        try:
            for journal in self.journals:
                if await self.connect(journal):
                    for section in self.journals[journal]["sections"]:
                        items = await self.fetch_data(journal, section, limit)
                        all_items.extend(items)
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution du scraper: {str(e)}")
        finally:
            self.cleanup()
        
        return all_items
