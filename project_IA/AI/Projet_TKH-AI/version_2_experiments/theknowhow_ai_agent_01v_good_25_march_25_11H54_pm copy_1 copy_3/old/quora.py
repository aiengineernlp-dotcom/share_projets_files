"""
Module de scraping Quora pour la collecte de questions et réponses médicales.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_scrapper.base_scraper import BaseScraper
from core.data_collection.storage.sqlite_storage import SQLiteStorage
from core.utils.config import load_config

logger = setup_logger(__name__)

class QuoraScraper(BaseScraper):
    """Scraper spécialisé pour Quora."""
    
    def __init__(self):
        """Initialise le scraper Quora avec les configurations."""
        super().__init__(source_name="quora", source_type="social_media")
        self.driver = None
        self.base_url = "https://www.quora.com"
        self.topics = [
            "Medicine",
            "Medical-Conditions",
            "Healthcare",
            "Doctors",
            "Medical-Science",
            "Medical-Research",
            "Medical-Advice",
            "Hospitals",
            "Public-Health",
            "Mental-Health"
        ]
        
    async def connect(self) -> bool:
        """Établit la connexion avec Quora via Selenium."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")  # Mode sans interface
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            
            # Connexion à Quora
            self.driver.get(self.base_url)
            
            # TODO: Ajouter la gestion de la connexion si nécessaire
            # self._login()
            
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion à Quora: {e}")
            return False

    async def fetch_data(self, topic: str, limit: int = 50) -> List[Dict]:
        """
        Récupère les questions et réponses d'un topic.
        
        Args:
            topic: Nom du topic
            limit: Nombre maximum de questions à récupérer
            
        Returns:
            Liste de dictionnaires contenant les données
        """
        try:
            questions = []
            topic_url = f"{self.base_url}/topic/{topic}"
            self.driver.get(topic_url)
            
            # Attente du chargement des questions
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "q-box"))
            )
            
            # Scroll pour charger plus de questions
            questions_loaded = 0
            while questions_loaded < limit:
                # Scroll
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                
                # Attente du chargement
                await self._wait_for_new_content()
                
                # Extraction des questions visibles
                question_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.q-box div.qu-cursor--pointer"
                )
                
                for element in question_elements[questions_loaded:limit]:
                    try:
                        # Extraction des données de la question
                        question_data = await self._extract_question_data(element)
                        if question_data:
                            questions.append(question_data)
                            questions_loaded += 1
                            
                    except Exception as e:
                        logger.error(f"Erreur lors de l'extraction d'une question: {e}")
                        continue
                        
                if len(question_elements) < limit:
                    break
                    
            return questions
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des questions pour le topic {topic}: {e}")
            return []
        
    async def _extract_question_data(self, element) -> Optional[Dict]:
        """
        Extrait les données d'une question.
        
        Args:
            element: Élément HTML de la question
            
        Returns:
            Dictionnaire contenant les données de la question
        """
        try:
            # Clic sur la question pour voir les détails
            element.click()
            
            # Attente du chargement des détails
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "q-text"))
            )
            
            # Extraction des données
            question_data = {
                "id": element.get_attribute("data-id"),
                "title": element.find_element(By.CSS_SELECTOR, "span.q-text").text,
                "url": element.find_element(By.CSS_SELECTOR, "a").get_attribute("href"),
                "topic": self.current_topic,
                "answers": await self._extract_answers(),
                "type": "question",
                "collected_at": datetime.now().isoformat()
            }
            
            return question_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données d'une question: {e}")
            return None

    async def _extract_answers(self, limit: int = 10) -> List[Dict]:
        """
        Extrait les réponses d'une question.
        
        Args:
            limit: Nombre maximum de réponses à extraire
            
        Returns:
            Liste des réponses
        """
        try:
            answers = []
            
            # Attente du chargement des réponses
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "q-answer"))
            )
            
            # Extraction des réponses
            answer_elements = self.driver.find_elements(
                By.CLASS_NAME,
                "q-answer"
            )[:limit]
            
            for element in answer_elements:
                try:
                    answer_data = {
                        "id": element.get_attribute("data-id"),
                        "text": element.find_element(By.CSS_SELECTOR, "div.q-text").text,
                        "author": {
                            "name": element.find_element(By.CSS_SELECTOR, "a.q-user").text,
                            "url": element.find_element(By.CSS_SELECTOR, "a.q-user").get_attribute("href")
                        },
                        "upvotes": int(element.find_element(By.CSS_SELECTOR, "span.q-upvotes").text or 0),
                        "type": "answer"
                    }
                    answers.append(answer_data)
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'extraction d'une réponse: {e}")
                    continue
                    
            return answers
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des réponses: {e}")
            return []

    async def _wait_for_new_content(self, timeout: int = 5):
        """
        Attend le chargement de nouveau contenu.
        
        Args:
            timeout: Temps d'attente maximum en secondes
        """
        try:
            old_height = self.driver.execute_script("return document.body.scrollHeight")
            await asyncio.sleep(1)
            
            start_time = datetime.now()
            while True:
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height > old_height:
                    break
                    
                if (datetime.now() - start_time).seconds > timeout:
                    break
                    
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'attente du nouveau contenu: {e}")

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
            if item["type"] == "question":
                # Nettoyage du titre
                item["title"] = self._clean_text(item["title"])
                
                # Nettoyage des réponses
                cleaned_answers = []
                for answer in item.get("answers", []):
                    answer["text"] = self._clean_text(answer["text"])
                    if self._is_medical_answer(answer["text"]):
                        cleaned_answers.append(answer)
                item["answers"] = cleaned_answers
                
                # Validation du contenu médical
                if self._is_medical_question(item["title"]) or cleaned_answers:
                    processed_data.append(item)
                
        return processed_data

    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte des caractères indésirables.
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        if not text:
            return ""
            
        # Nettoyage basique
        text = text.strip()
        text = text.replace("\n", " ")
        text = " ".join(text.split())  # Normalise les espaces
        
        return text

    def _is_medical_question(self, text: str) -> bool:
        """
        Vérifie si la question est liée au domaine médical.
        
        Args:
            text: Texte de la question
            
        Returns:
            True si la question est médicale
        """
        medical_keywords = {
            "santé", "médical", "symptômes", "traitement",
            "maladie", "diagnostic", "patient", "clinique",
            "hôpital", "docteur", "médecin", "chirurgie",
            "médicament", "prescription", "consultation"
        }
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in medical_keywords)

    def _is_medical_answer(self, text: str) -> bool:
        """
        Vérifie si la réponse est liée au domaine médical.
        
        Args:
            text: Texte de la réponse
            
        Returns:
            True si la réponse est médicale
        """
        # Utilise les mêmes critères que pour les questions
        return self._is_medical_question(text)

    async def run(self, limit: int = 50) -> None:
        """
        Exécute le processus complet de scraping.
        
        Args:
            limit: Nombre maximum de questions par topic
        """
        if not await self.connect():
            logger.error("Impossible de se connecter à Quora")
            return

        try:
            for topic in self.topics:
                try:
                    logger.info(f"Scraping du topic Quora '{topic}'")
                    
                    # Récupération des données
                    raw_data = await self.fetch_data(topic, limit)
                    if not raw_data:
                        continue
                        
                    # Traitement des données
                    processed_data = await self.process_data(raw_data)
                    
                    # Sauvegarde des données
                    await self.save_data(processed_data, is_processed=True)
                    
                    logger.info(f"Scraping du topic {topic} terminé avec succès")
                    
                except Exception as e:
                    logger.error(f"Erreur lors du scraping du topic {topic}: {e}")
                    continue
                    
        finally:
            # Fermeture du navigateur
            if self.driver:
                self.driver.quit()
