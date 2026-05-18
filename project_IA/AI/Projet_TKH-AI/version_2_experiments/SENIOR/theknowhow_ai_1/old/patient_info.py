"""
Module de scraping pour Patient.info.
Utilise Selenium pour extraire le contenu des forums médicaux anglophones.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from collections import defaultdict
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import requests

from app.scraping.base.base_scraper import BaseScraper
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class PatientInfoScraper(BaseScraper):
    """Scraper spécialisé pour Patient.info."""
    
    def __init__(self):
        """Initialise le scraper Patient.info avec les configurations."""
        super().__init__(source_name="patient_info", source_type="forum")
        self.driver = None
        self.base_url = "https://patient.info/forums"
        self.categories = [
            "general-health",
            "mental-health",
            "pregnancy",
            "cancer",
            "heart-disease",
            "diabetes",
            "allergies",
            "skin-conditions",
            "digestive-health",
            "medications"
        ]
        self.medical_keywords = [
            "symptoms",
            "treatment",
            "diagnosis",
            "medication",
            "disease",
            "consultation",
            "doctor",
            "GP",
            "NHS",
            "prescription",
            "dosage",
            "medical",
            "clinical",
            "therapy",
            "health",
            "specialist",
            "referral"
        ]
        self.discussion_cache = defaultdict(list)
        self.max_cache_size = 1000
        
    async def connect(self) -> bool:
        """Établit la connexion avec Patient.info."""
        try:
            # Configuration de Selenium
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            
            # Test de connexion
            self.driver.get(self.base_url)
            
            # Gestion des cookies (GDPR)
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
                )
                cookie_button.click()
            except:
                pass
                
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Patient.info: {e}")
            return False

    async def fetch_data(self, category: str, limit: int = 100) -> List[Dict]:
        """
        Récupère les discussions d'une catégorie.
        
        Args:
            category: Catégorie du forum
            limit: Nombre maximum de discussions
            
        Returns:
            Liste de dictionnaires contenant les données
        """
        try:
            discussions = []
            page = 1
            
            while len(discussions) < limit:
                # Navigation vers la page de la catégorie
                url = f"{self.base_url}/{category}?page={page}"
                self.driver.get(url)
                
                # Attente du chargement des discussions
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "forum-topic"))
                )
                
                # Extraction des discussions
                topic_elements = self.driver.find_elements(By.CLASS_NAME, "forum-topic")
                
                if not topic_elements:
                    break
                    
                for element in topic_elements[:limit - len(discussions)]:
                    try:
                        # Extraction des données de base de la discussion
                        topic_data = {
                            "id": element.get_attribute("data-topic-id"),
                            "title": element.find_element(By.CLASS_NAME, "topic-title").text,
                            "url": element.find_element(By.CLASS_NAME, "topic-link").get_attribute("href"),
                            "author": {
                                "username": element.find_element(By.CLASS_NAME, "author-name").text,
                                "profile_url": element.find_element(By.CLASS_NAME, "author-link").get_attribute("href"),
                                "is_verified": len(element.find_elements(By.CLASS_NAME, "verified-badge")) > 0,
                                "is_doctor": len(element.find_elements(By.CLASS_NAME, "doctor-badge")) > 0
                            },
                            "created_at": element.find_element(By.CLASS_NAME, "topic-date").get_attribute("datetime"),
                            "category": category,
                            "metrics": {
                                "views": int(element.find_element(By.CLASS_NAME, "view-count").text.replace(",", "")),
                                "replies": int(element.find_element(By.CLASS_NAME, "reply-count").text),
                                "likes": int(element.find_element(By.CLASS_NAME, "like-count").text)
                            },
                            "tags": [
                                tag.text
                                for tag in element.find_elements(By.CLASS_NAME, "topic-tag")
                            ],
                            "is_medical_content": self._is_medical_content(
                                f"{element.find_element(By.CLASS_NAME, 'topic-title').text} "
                                f"{element.find_element(By.CLASS_NAME, 'topic-preview').text}"
                            ),
                            "is_answered": len(element.find_elements(By.CLASS_NAME, "answered-badge")) > 0,
                            "collected_at": datetime.now().isoformat()
                        }
                        
                        # Récupération du contenu complet de la discussion
                        topic_content = await self._fetch_topic_content(topic_data["url"])
                        topic_data.update(topic_content)
                        
                        discussions.append(topic_data)
                        
                    except Exception as e:
                        logger.error(f"Error extracting topic data: {e}")
                        continue
                        
                page += 1
                
            return discussions
            
        except Exception as e:
            logger.error(f"Error fetching discussions from category {category}: {e}")
            return []

    async def _fetch_topic_content(self, url: str) -> Dict:
        """
        Récupère le contenu complet d'une discussion.
        
        Args:
            url: URL de la discussion
            
        Returns:
            Dictionnaire contenant le contenu et les réponses
        """
        try:
            self.driver.get(url)
            
            # Attente du chargement du contenu
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "topic-content"))
            )
            
            # Extraction du contenu initial
            initial_post = self.driver.find_element(By.CLASS_NAME, "topic-content")
            content = {
                "content": initial_post.text,
                "has_images": len(initial_post.find_elements(By.TAG_NAME, "img")) > 0,
                "has_links": len(initial_post.find_elements(By.TAG_NAME, "a")) > 0,
                "has_files": len(initial_post.find_elements(By.CLASS_NAME, "attachment")) > 0,
                "medical_references": [
                    ref.get_attribute("href")
                    for ref in initial_post.find_elements(By.CLASS_NAME, "medical-reference")
                ]
            }
            
            # Chargement de toutes les réponses
            while True:
                try:
                    load_more = self.driver.find_element(By.CLASS_NAME, "load-more-replies")
                    if not load_more.is_displayed():
                        break
                    load_more.click()
                    time.sleep(1)
                except:
                    break
            
            # Extraction des réponses
            replies = []
            reply_elements = self.driver.find_elements(By.CLASS_NAME, "reply-item")
            
            for reply in reply_elements:
                try:
                    reply_data = {
                        "id": reply.get_attribute("data-reply-id"),
                        "content": reply.find_element(By.CLASS_NAME, "reply-content").text,
                        "author": {
                            "username": reply.find_element(By.CLASS_NAME, "reply-author").text,
                            "profile_url": reply.find_element(By.CLASS_NAME, "author-link").get_attribute("href"),
                            "is_verified": len(reply.find_elements(By.CLASS_NAME, "verified-badge")) > 0,
                            "is_doctor": len(reply.find_elements(By.CLASS_NAME, "doctor-badge")) > 0,
                            "speciality": reply.find_element(By.CLASS_NAME, "doctor-speciality").text if len(reply.find_elements(By.CLASS_NAME, "doctor-speciality")) > 0 else None
                        },
                        "created_at": reply.find_element(By.CLASS_NAME, "reply-date").get_attribute("datetime"),
                        "is_medical_content": self._is_medical_content(
                            reply.find_element(By.CLASS_NAME, "reply-content").text
                        ),
                        "has_images": len(reply.find_elements(By.TAG_NAME, "img")) > 0,
                        "has_links": len(reply.find_elements(By.TAG_NAME, "a")) > 0,
                        "has_files": len(reply.find_elements(By.CLASS_NAME, "attachment")) > 0,
                        "medical_references": [
                            ref.get_attribute("href")
                            for ref in reply.find_elements(By.CLASS_NAME, "medical-reference")
                        ],
                        "metrics": {
                            "likes": int(reply.find_element(By.CLASS_NAME, "like-count").text),
                            "helpful_marks": int(reply.find_element(By.CLASS_NAME, "helpful-count").text)
                        },
                        "is_accepted_answer": len(reply.find_elements(By.CLASS_NAME, "accepted-answer")) > 0
                    }
                    replies.append(reply_data)
                    
                except Exception as e:
                    logger.error(f"Error extracting reply data: {e}")
                    continue
                    
            content["replies"] = replies
            return content
            
        except Exception as e:
            logger.error(f"Error fetching topic content from {url}: {e}")
            return {"content": "", "replies": []}

    def _is_medical_content(self, text: str) -> bool:
        """
        Vérifie si le contenu est lié au domaine médical.
        
        Args:
            text: Texte à analyser
            
        Returns:
            True si le contenu est médical
        """
        if not text:
            return False
            
        text_lower = text.lower()
        return any(
            keyword.lower() in text_lower
            for keyword in self.medical_keywords
        )

    async def analyze_category_activity(self, category: str, days: int = 7) -> Dict:
        """
        Analyse l'activité d'une catégorie.
        
        Args:
            category: Catégorie à analyser
            days: Nombre de jours d'historique
            
        Returns:
            Statistiques d'activité de la catégorie
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Récupération des discussions récentes
            discussions = await self.fetch_data(category, limit=1000)
            
            # Filtrage par date
            recent_discussions = [
                discussion for discussion in discussions
                if datetime.fromisoformat(discussion["created_at"]) >= start_date
            ]
            
            if not recent_discussions:
                return {}
                
            # Analyse des discussions
            total_discussions = len(recent_discussions)
            medical_discussions = len([
                discussion for discussion in recent_discussions
                if discussion["is_medical_content"]
            ])
            
            # Analyse des réponses
            total_replies = sum(
                len(discussion["replies"])
                for discussion in recent_discussions
            )
            medical_replies = sum(
                len([
                    reply
                    for reply in discussion["replies"]
                    if reply["is_medical_content"]
                ])
                for discussion in recent_discussions
            )
            
            # Analyse des réponses des médecins
            doctor_replies = sum(
                len([
                    reply
                    for reply in discussion["replies"]
                    if reply["author"]["is_doctor"]
                ])
                for discussion in recent_discussions
            )
            
            # Analyse des réponses acceptées
            accepted_answers = sum(
                len([
                    reply
                    for reply in discussion["replies"]
                    if reply["is_accepted_answer"]
                ])
                for discussion in recent_discussions
            )
            
            # Analyse des métriques d'engagement
            total_views = sum(
                discussion["metrics"]["views"]
                for discussion in recent_discussions
            )
            total_likes = sum(
                discussion["metrics"]["likes"]
                for discussion in recent_discussions
            )
            total_helpful_marks = sum(
                sum(
                    reply["metrics"]["helpful_marks"]
                    for reply in discussion["replies"]
                )
                for discussion in recent_discussions
            )
            
            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat()
                },
                "discussions": {
                    "total": total_discussions,
                    "medical": medical_discussions,
                    "avg_per_day": total_discussions / days,
                    "answered_percentage": len([d for d in recent_discussions if d["is_answered"]]) / total_discussions * 100 if total_discussions > 0 else 0
                },
                "replies": {
                    "total": total_replies,
                    "medical": medical_replies,
                    "doctor": doctor_replies,
                    "accepted": accepted_answers,
                    "avg_per_discussion": total_replies / total_discussions if total_discussions > 0 else 0
                },
                "engagement": {
                    "total_views": total_views,
                    "total_likes": total_likes,
                    "total_helpful_marks": total_helpful_marks,
                    "avg_views_per_discussion": total_views / total_discussions if total_discussions > 0 else 0,
                    "avg_likes_per_discussion": total_likes / total_discussions if total_discussions > 0 else 0,
                    "avg_helpful_marks_per_reply": total_helpful_marks / total_replies if total_replies > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing category {category}: {e}")
            return {}

    async def process_data(self, data: List[Dict]) -> List[Dict]:
        """
        Traite et nettoie les données récupérées.
        
        Args:
            data: Données brutes
            
        Returns:
            Données traitées
        """
        processed_data = []
        
        for item in data:
            if item.get("is_medical_content"):
                # Ajout de métadonnées supplémentaires
                item["has_doctor_response"] = any(
                    reply["author"]["is_doctor"]
                    for reply in item.get("replies", [])
                )
                item["has_accepted_answer"] = any(
                    reply["is_accepted_answer"]
                    for reply in item.get("replies", [])
                )
                item["medical_reference_count"] = len(item.get("medical_references", []))
                
                processed_data.append(item)
                
        return processed_data

    async def run(self, limit: int = 100) -> None:
        """
        Exécute le processus complet de scraping.
        
        Args:
            limit: Nombre maximum de résultats par catégorie
        """
        if not await self.connect():
            logger.error("Unable to connect to Patient.info")
            return

        try:
            # Scraping des catégories
            for category in self.categories:
                try:
                    logger.info(f"Scraping Patient.info category {category}")
                    
                    # Récupération des discussions
                    discussions = await self.fetch_data(category, limit)
                    if discussions:
                        # Traitement des données
                        processed_discussions = await self.process_data(discussions)
                        
                        # Sauvegarde des données
                        await self.save_data(processed_discussions, is_processed=True)
                        
                        # Analyse de l'activité de la catégorie
                        activity_stats = await self.analyze_category_activity(category)
                        if activity_stats:
                            await self.save_data([activity_stats], is_processed=True)
                        
                        logger.info(f"Successfully scraped category {category}")
                        
                except Exception as e:
                    logger.error(f"Error scraping category {category}: {e}")
                    continue
                    
            # Nettoyage des ressources Selenium
            if self.driver:
                self.driver.quit()
                
        except Exception as e:
            logger.error(f"Error during Patient.info scraping: {e}")
            if self.driver:
                self.driver.quit() 