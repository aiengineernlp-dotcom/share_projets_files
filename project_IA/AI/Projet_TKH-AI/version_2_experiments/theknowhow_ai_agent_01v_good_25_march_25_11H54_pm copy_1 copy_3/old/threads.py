"""
Module de scraping pour Threads.
Utilise l'API non officielle de Threads pour extraire le contenu médical.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from collections import defaultdict
import json

import requests
from bs4 import BeautifulSoup

from app.scraping.base.base_scraper import BaseScraper
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ThreadsScraper(BaseScraper):
    """Scraper spécialisé pour Threads."""
    
    def __init__(self):
        """Initialise le scraper Threads avec les configurations."""
        super().__init__(source_name="threads", source_type="social_media")
        self.session = None
        self.base_url = "https://www.threads.net"
        self.api_base_url = "https://www.threads.net/api/graphql"
        self.medical_accounts = [
            "who",
            "mayoclinic",
            "clevelandclinic",
            "webmd",
            "medicalnewstoday"
        ]
        self.medical_keywords = [
            "santé",
            "médical",
            "médecin",
            "traitement",
            "diagnostic",
            "clinique",
            "hôpital",
            "health",
            "medical",
            "doctor",
            "treatment",
            "diagnosis",
            "clinical",
            "hospital"
        ]
        self.thread_cache = defaultdict(list)
        self.max_cache_size = 1000
        
    async def connect(self) -> bool:
        """Établit la connexion avec Threads."""
        try:
            self.session = requests.Session()
            
            # Configuration des headers
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.5",
                "X-IG-App-ID": os.getenv("THREADS_APP_ID"),
                "X-CSRFToken": os.getenv("THREADS_CSRF_TOKEN")
            })
            
            # Authentification
            auth_data = {
                "username": os.getenv("THREADS_USERNAME"),
                "password": os.getenv("THREADS_PASSWORD")
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=auth_data
            )
            
            return response.ok
            
        except Exception as e:
            logger.error(f"Erreur de connexion à Threads: {e}")
            return False

    async def fetch_data(self, username: str, limit: int = 100) -> List[Dict]:
        """
        Récupère les threads d'un utilisateur.
        
        Args:
            username: Nom d'utilisateur
            limit: Nombre maximum de threads
            
        Returns:
            Liste de dictionnaires contenant les données
        """
        try:
            # Récupération de l'ID de l'utilisateur
            user_id = await self._get_user_id(username)
            if not user_id:
                return []
                
            # Récupération des threads
            query_data = {
                "query_hash": "threads_user_threads",
                "variables": {
                    "user_id": user_id,
                    "first": limit
                }
            }
            
            response = self.session.post(
                self.api_base_url,
                json=query_data
            )
            
            if not response.ok:
                return []
                
            threads_data = response.json()
            threads = []
            
            for thread in threads_data.get("data", {}).get("user", {}).get("threads", []):
                try:
                    thread_data = await self._extract_thread_data(thread)
                    if thread_data:
                        threads.append(thread_data)
                        
                except Exception as e:
                    logger.error(f"Erreur lors de l'extraction d'un thread: {e}")
                    continue
                    
            return threads
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des threads de @{username}: {e}")
            return []

    async def _get_user_id(self, username: str) -> Optional[str]:
        """
        Récupère l'ID d'un utilisateur Threads.
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            ID de l'utilisateur
        """
        try:
            response = self.session.get(f"{self.base_url}/{username}")
            
            if not response.ok:
                return None
                
            # Extraction de l'ID depuis le HTML
            soup = BeautifulSoup(response.text, "html.parser")
            user_data = soup.find("script", {"type": "application/ld+json"})
            
            if not user_data:
                return None
                
            data = json.loads(user_data.string)
            return data.get("identifier")
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'ID de @{username}: {e}")
            return None

    async def _extract_thread_data(self, thread: Dict) -> Optional[Dict]:
        """
        Extrait les données d'un thread.
        
        Args:
            thread: Données brutes du thread
            
        Returns:
            Dictionnaire contenant les données du thread
        """
        try:
            # Construction des données du thread
            thread_data = {
                "type": "thread",
                "id": thread.get("id"),
                "content": thread.get("text", ""),
                "created_at": datetime.fromtimestamp(
                    thread.get("created_at", 0)
                ).isoformat(),
                "author": {
                    "username": thread.get("user", {}).get("username"),
                    "name": thread.get("user", {}).get("full_name"),
                    "is_verified": thread.get("user", {}).get("is_verified", False)
                },
                "metrics": {
                    "likes": thread.get("like_count", 0),
                    "replies": thread.get("reply_count", 0),
                    "reposts": thread.get("repost_count", 0)
                },
                "is_medical_content": self._is_medical_content(thread.get("text", "")),
                "collected_at": datetime.now().isoformat()
            }
            
            # Récupération des réponses
            replies = await self._fetch_replies(thread.get("id"))
            thread_data["replies"] = replies
            
            return thread_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données du thread: {e}")
            return None

    async def _fetch_replies(self, thread_id: str) -> List[Dict]:
        """
        Récupère les réponses d'un thread.
        
        Args:
            thread_id: ID du thread
            
        Returns:
            Liste des réponses
        """
        try:
            query_data = {
                "query_hash": "thread_replies",
                "variables": {
                    "thread_id": thread_id,
                    "first": 50
                }
            }
            
            response = self.session.post(
                self.api_base_url,
                json=query_data
            )
            
            if not response.ok:
                return []
                
            replies_data = response.json()
            replies = []
            
            for reply in replies_data.get("data", {}).get("thread", {}).get("replies", []):
                try:
                    reply_data = {
                        "id": reply.get("id"),
                        "content": reply.get("text", ""),
                        "created_at": datetime.fromtimestamp(
                            reply.get("created_at", 0)
                        ).isoformat(),
                        "author": {
                            "username": reply.get("user", {}).get("username"),
                            "name": reply.get("user", {}).get("full_name"),
                            "is_verified": reply.get("user", {}).get("is_verified", False)
                        },
                        "metrics": {
                            "likes": reply.get("like_count", 0),
                            "replies": reply.get("reply_count", 0)
                        },
                        "is_medical_content": self._is_medical_content(reply.get("text", ""))
                    }
                    replies.append(reply_data)
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'extraction d'une réponse: {e}")
                    continue
                    
            return replies
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des réponses du thread {thread_id}: {e}")
            return []

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

    async def analyze_account_activity(self, username: str, days: int = 7) -> Dict:
        """
        Analyse l'activité d'un compte médical.
        
        Args:
            username: Nom d'utilisateur
            days: Nombre de jours d'historique
            
        Returns:
            Statistiques d'activité du compte
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Récupération des threads récents
            threads = await self.fetch_data(username, limit=1000)
            
            # Filtrage par date
            recent_threads = [
                thread for thread in threads
                if datetime.fromisoformat(thread["created_at"]) >= start_date
            ]
            
            if not recent_threads:
                return {}
                
            # Analyse des threads
            total_threads = len(recent_threads)
            medical_threads = len([
                thread for thread in recent_threads
                if thread["is_medical_content"]
            ])
            
            # Analyse des réponses
            total_replies = sum(
                len(thread["replies"])
                for thread in recent_threads
            )
            medical_replies = sum(
                len([
                    reply
                    for reply in thread["replies"]
                    if reply["is_medical_content"]
                ])
                for thread in recent_threads
            )
            
            # Calcul des métriques d'engagement
            total_likes = sum(
                thread["metrics"]["likes"]
                for thread in recent_threads
            )
            total_reposts = sum(
                thread["metrics"]["reposts"]
                for thread in recent_threads
            )
            
            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat()
                },
                "threads": {
                    "total": total_threads,
                    "medical": medical_threads,
                    "avg_per_day": total_threads / days
                },
                "replies": {
                    "total": total_replies,
                    "medical": medical_replies,
                    "avg_per_thread": total_replies / total_threads if total_threads > 0 else 0
                },
                "engagement": {
                    "likes": total_likes,
                    "reposts": total_reposts,
                    "avg_likes_per_thread": total_likes / total_threads if total_threads > 0 else 0,
                    "avg_reposts_per_thread": total_reposts / total_threads if total_threads > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du compte @{username}: {e}")
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
                processed_data.append(item)
                
        return processed_data

    async def run(self, limit: int = 100) -> None:
        """
        Exécute le processus complet de scraping.
        
        Args:
            limit: Nombre maximum de résultats par compte
        """
        if not await self.connect():
            logger.error("Impossible de se connecter à Threads")
            return

        try:
            # Scraping des comptes médicaux
            for username in self.medical_accounts:
                try:
                    logger.info(f"Scraping du compte Threads @{username}")
                    
                    # Récupération des threads
                    threads = await self.fetch_data(username, limit)
                    if threads:
                        # Traitement des données
                        processed_threads = await self.process_data(threads)
                        
                        # Sauvegarde des données
                        await self.save_data(processed_threads, is_processed=True)
                        
                        # Analyse de l'activité du compte
                        activity_stats = await self.analyze_account_activity(username)
                        if activity_stats:
                            await self.save_data([activity_stats], is_processed=True)
                        
                        logger.info(f"Scraping du compte @{username} terminé avec succès")
                        
                except Exception as e:
                    logger.error(f"Erreur lors du scraping du compte @{username}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Erreur lors du scraping Threads: {e}")
