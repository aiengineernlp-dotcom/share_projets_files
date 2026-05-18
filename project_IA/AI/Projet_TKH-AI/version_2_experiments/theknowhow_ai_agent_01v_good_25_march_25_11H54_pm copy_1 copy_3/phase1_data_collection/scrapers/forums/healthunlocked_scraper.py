"""
Scraper pour le forum HealthUnlocked.

RÔLE PRINCIPAL :
---------------
Ce module implémente le scraper pour le forum HealthUnlocked.
Il collecte et analyse les discussions médicales du forum, en se
concentrant sur les posts pertinents pour l'analyse médicale.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * run_phase1.py (exécution du scraper)
  * phase1.py (intégration dans la phase 1)

- Dépend de :
  * config/settings.py (configuration)
  * processors/medical_analysis/*.py (analyse médicale)
  * nlp/analysis/text_analyzer.py (analyse de texte)

STRUCTURE DU CONTENU :
--------------------
1. Configuration :
   - Paramètres de scraping
   - URLs des forums
   - Filtres de contenu
   - Seuils d'analyse

2. Classe HealthUnlockedScraper :
   - Initialisation
   - Authentification
   - Configuration des requêtes
   - Gestion des sessions

3. Méthodes de scraping :
   - scrape_forum() : Scraping principal
   - extract_posts() : Extraction des posts
   - process_post() : Traitement des posts
   - save_results() : Sauvegarde des résultats

4. Utilitaires :
   - format_date() : Formatage des dates
   - clean_text() : Nettoyage du texte
   - check_relevance() : Vérification de pertinence
   - handle_errors() : Gestion des erreurs

FONCTIONS PRINCIPALES :
---------------------
- scrape_healthunlocked() : Fonction principale
- analyze_post() : Analyse des posts
- categorize_post() : Catégorisation
- export_data() : Export des données

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il collecte des données médicales importantes
- Il complète les sources de données
- Il enrichit l'analyse médicale
- Il est essentiel pour la phase 1
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Any
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from config.forums.healthunlocked_config import (
    BASE_CONFIG,
    COMMUNITIES,
    SORT_OPTIONS,
    DB_CONFIG
)

class HealthUnlockedScraper(BaseScraper):
    """Scraper pour HealthUnlocked avec protections intégrées."""
    
    def __init__(self):
        """Initialise le scraper HealthUnlocked."""
        super().__init__("healthunlocked")
        self.base_url = BASE_CONFIG["base_url"]
        self.db_connection = self._init_database()

    def _init_database(self) -> sqlite3.Connection:
        """Initialise la base de données SQLite."""
        connection = sqlite3.connect(DB_CONFIG["db_path"])
        cursor = connection.cursor()
        
        # Création de la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS healthunlocked_posts (
                post_id TEXT PRIMARY KEY,
                author_id TEXT,
                community_name TEXT,
                title TEXT,
                body TEXT,
                created_at TIMESTAMP,
                url TEXT,
                medical_relevance_score FLOAT,
                urgency_score FLOAT,
                has_expert_reply BOOLEAN,
                language TEXT,
                scraped_at TIMESTAMP
            )
        """)
        
        # Création des index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_community ON healthunlocked_posts(community_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON healthunlocked_posts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_medical_score ON healthunlocked_posts(medical_relevance_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urgency ON healthunlocked_posts(urgency_score)")
        
        connection.commit()
        return connection

    async def scrape_community(self, community: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape les posts d'une communauté spécifique.
        
        Args:
            community: Configuration de la communauté à scraper
            
        Returns:
            List[Dict[str, Any]]: Liste des posts scrapés
        """
        posts = []
        for sort_option in SORT_OPTIONS:
            page = 1
            while page <= BASE_CONFIG["max_pages_per_community"]:
                url = f"{self.base_url}/communities/{community['url_slug']}/posts"
                params = {
                    "page": page,
                    "sort": sort_option["param"]
                }
                
                response = await self.make_request(url, params=params)
                if not response:
                    break
                
                new_posts = self._parse_posts_page(response.text, community["name"])
                if not new_posts:
                    break
                
                posts.extend(new_posts)
                page += 1
                
                # Vérification du nombre de posts
                if len(posts) >= BASE_CONFIG["batch_size"]:
                    break
        
        return posts

    def _parse_posts_page(self, html: str, community_name: str) -> List[Dict[str, Any]]:
        """
        Parse une page de posts.
        
        Args:
            html: Contenu HTML de la page
            community_name: Nom de la communauté
            
        Returns:
            List[Dict[str, Any]]: Liste des posts parsés
        """
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        for post_element in soup.select('.post-item'):  # Sélecteur CSS à adapter
            try:
                post = {
                    'post_id': post_element.get('data-post-id'),
                    'author_id': post_element.select_one('.author-link').get('href').split('/')[-1],
                    'community_name': community_name,
                    'title': post_element.select_one('.post-title').text.strip(),
                    'body': post_element.select_one('.post-content').text.strip(),
                    'created_at': self._parse_date(post_element.select_one('.post-date').text.strip()),
                    'url': self.base_url + post_element.select_one('.post-link')['href'],
                    'medical_relevance_score': self._calculate_medical_relevance(post_element.text),
                    'urgency_score': self._calculate_urgency(post_element.text),
                    'has_expert_reply': bool(post_element.select_one('.expert-reply')),
                    'language': 'en',  # À améliorer avec détection de langue
                    'scraped_at': datetime.now()
                }
                posts.append(post)
            except Exception as e:
                self.logger.error(f"Erreur lors du parsing d'un post: {str(e)}")
                continue
        
        return posts

    def _calculate_medical_relevance(self, text: str) -> float:
        """Calcule le score de pertinence médicale."""
        # À implémenter avec NLP
        return 0.5

    def _calculate_urgency(self, text: str) -> float:
        """Calcule le score d'urgence."""
        # À implémenter avec NLP
        return 0.3

    def _parse_date(self, date_str: str) -> datetime:
        """Parse une date depuis une chaîne."""
        # À adapter selon le format de date de HealthUnlocked
        return datetime.now()  # Temporaire

    async def scrape_posts(self):
        """Scrape tous les posts des communautés configurées."""
        try:
            for community in COMMUNITIES:
                self.logger.info(f"Scraping de la communauté: {community['name']}")
                posts = await self.scrape_community(community)
                
                # Sauvegarde des posts dans la base de données
                cursor = self.db_connection.cursor()
                for post in posts:
                    cursor.execute("""
                        INSERT OR REPLACE INTO healthunlocked_posts
                        (post_id, author_id, community_name, title, body, created_at,
                         url, medical_relevance_score, urgency_score, has_expert_reply,
                         language, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        post['post_id'], post['author_id'], post['community_name'],
                        post['title'], post['body'], post['created_at'], post['url'],
                        post['medical_relevance_score'], post['urgency_score'],
                        post['has_expert_reply'], post['language'], post['scraped_at']
                    ))
                
                self.db_connection.commit()
                
                # Vacuum périodique de la base
                if self.request_count % DB_CONFIG["vacuum_frequency"] == 0:
                    self.db_connection.execute("VACUUM")
        
        except Exception as e:
            self.logger.error(f"Erreur lors du scraping: {str(e)}")
            raise
        
        finally:
            self.close()

    def close(self):
        """Ferme proprement le scraper et la connexion à la base de données."""
        super().close()
        if hasattr(self, 'db_connection'):
            self.db_connection.close() 