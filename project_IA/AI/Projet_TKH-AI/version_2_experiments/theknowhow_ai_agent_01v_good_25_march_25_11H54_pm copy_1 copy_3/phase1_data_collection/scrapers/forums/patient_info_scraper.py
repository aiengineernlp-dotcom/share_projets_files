"""
Scraper pour le forum Patient.info.

RÔLE PRINCIPAL :
---------------
Ce module implémente le scraper pour le forum Patient.info.
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

2. Classe PatientInfoScraper :
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
- scrape_patient_info() : Fonction principale
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
from config.forums.patient_info_config import (
    BASE_CONFIG,
    CATEGORIES,
    SORT_OPTIONS,
    DB_CONFIG,
    HTTP_HEADERS,
    KEYWORDS,
    TIMEOUT_CONFIG,
    ANALYSIS_CONFIG,
    UK_SPECIFIC as UK_CONFIG
)

class PatientInfoScraper(BaseScraper):
    """Scraper pour Patient.info avec protections intégrées."""
    
    def __init__(self):
        """Initialise le scraper Patient.info."""
        super().__init__("patient_info")
        self.base_url = BASE_CONFIG["base_url"]
        self.db_connection = self._init_database()

    def _init_database(self) -> sqlite3.Connection:
        """Initialise la base de données SQLite."""
        connection = sqlite3.connect(DB_CONFIG["db_path"])
        cursor = connection.cursor()
        
        # Création de la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_info_posts (
                post_id TEXT PRIMARY KEY,
                author_id TEXT,
                category_name TEXT,
                title TEXT,
                body TEXT,
                created_at TIMESTAMP,
                url TEXT,
                medical_relevance_score FLOAT,
                urgency_score FLOAT,
                has_professional_reply BOOLEAN,
                professional_id TEXT,
                professional_response TEXT,
                professional_response_date TIMESTAMP,
                nhs_related BOOLEAN,
                uk_region TEXT,
                views_count INTEGER,
                replies_count INTEGER,
                language TEXT,
                scraped_at TIMESTAMP
            )
        """)
        
        # Création des index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON patient_info_posts(category_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON patient_info_posts(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_medical_score ON patient_info_posts(medical_relevance_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urgency ON patient_info_posts(urgency_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_professional ON patient_info_posts(has_professional_reply)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nhs ON patient_info_posts(nhs_related)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_region ON patient_info_posts(uk_region)")
        
        connection.commit()
        return connection

    async def scrape_category(self, category: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape les posts d'une catégorie spécifique.
        
        Args:
            category: Configuration de la catégorie à scraper
            
        Returns:
            List[Dict[str, Any]]: Liste des posts scrapés
        """
        posts = []
        for sort_option in SORT_OPTIONS:
            page = 1
            while page <= BASE_CONFIG["max_pages_per_category"]:
                url = f"{self.base_url}/forums/{category['url_slug']}"
                params = {
                    "page": page,
                    "sort": sort_option["param"]
                }
                
                response = await self.make_request(url, params=params)
                if not response:
                    break
                
                new_posts = self._parse_posts_page(response.text, category["name"])
                if not new_posts:
                    break
                
                posts.extend(new_posts)
                page += 1
                
                # Vérification du nombre de posts
                if len(posts) >= BASE_CONFIG["batch_size"]:
                    break
        
        return posts

    def _parse_posts_page(self, html: str, category_name: str) -> List[Dict[str, Any]]:
        """
        Parse une page de posts.
        
        Args:
            html: Contenu HTML de la page
            category_name: Nom de la catégorie
            
        Returns:
            List[Dict[str, Any]]: Liste des posts parsés
        """
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        for post_element in soup.select('.discussion-thread'):  # Sélecteur CSS à adapter
            try:
                post = {
                    'post_id': post_element.get('data-thread-id'),
                    'author_id': post_element.select_one('.author').get('data-user-id'),
                    'category_name': category_name,
                    'title': post_element.select_one('.thread-title').text.strip(),
                    'body': post_element.select_one('.thread-content').text.strip(),
                    'created_at': self._parse_date(post_element.select_one('.post-date').text.strip()),
                    'url': self.base_url + post_element.select_one('.thread-link')['href'],
                    'medical_relevance_score': self._calculate_medical_relevance(post_element.text),
                    'urgency_score': self._calculate_urgency(post_element.text),
                    'has_professional_reply': bool(post_element.select_one('.professional-response')),
                    'professional_id': self._get_professional_id(post_element),
                    'professional_response': self._get_professional_response(post_element),
                    'professional_response_date': self._get_professional_response_date(post_element),
                    'nhs_related': self._is_nhs_related(post_element.text),
                    'uk_region': self._extract_uk_region(post_element.text),
                    'views_count': self._parse_views_count(post_element),
                    'replies_count': self._parse_replies_count(post_element),
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
        # À adapter selon le format de date de Patient.info
        return datetime.now()  # Temporaire

    def _get_professional_id(self, post_element) -> Optional[str]:
        """Extrait l'ID du professionnel si présent."""
        prof_elem = post_element.select_one('.professional-response')
        return prof_elem.get('data-professional-id') if prof_elem else None

    def _get_professional_response(self, post_element) -> Optional[str]:
        """Extrait la réponse du professionnel si présente."""
        prof_resp = post_element.select_one('.professional-response-content')
        return prof_resp.text.strip() if prof_resp else None

    def _get_professional_response_date(self, post_element) -> Optional[datetime]:
        """Extrait la date de réponse du professionnel si présente."""
        date_elem = post_element.select_one('.professional-response-date')
        return self._parse_date(date_elem.text.strip()) if date_elem else None

    def _is_nhs_related(self, text: str) -> bool:
        """Détermine si le post est lié au NHS."""
        nhs_keywords = UK_CONFIG["nhs_keywords"]
        return any(keyword.lower() in text.lower() for keyword in nhs_keywords)

    def _extract_uk_region(self, text: str) -> Optional[str]:
        """Extrait la région UK mentionnée dans le texte."""
        for region in UK_CONFIG["regions"]:
            if region.lower() in text.lower():
                return region
        return None

    def _parse_views_count(self, post_element) -> int:
        """Parse le nombre de vues."""
        views_elem = post_element.select_one('.views-count')
        try:
            return int(views_elem.text.strip().split()[0]) if views_elem else 0
        except (ValueError, IndexError):
            return 0

    def _parse_replies_count(self, post_element) -> int:
        """Parse le nombre de réponses."""
        replies_elem = post_element.select_one('.replies-count')
        try:
            return int(replies_elem.text.strip().split()[0]) if replies_elem else 0
        except (ValueError, IndexError):
            return 0

    async def scrape_posts(self):
        """Scrape tous les posts des catégories configurées."""
        try:
            for category in CATEGORIES:
                self.logger.info(f"Scraping de la catégorie: {category['name']}")
                posts = await self.scrape_category(category)
                
                # Sauvegarde des posts dans la base de données
                cursor = self.db_connection.cursor()
                for post in posts:
                    cursor.execute("""
                        INSERT OR REPLACE INTO patient_info_posts
                        (post_id, author_id, category_name, title, body, created_at,
                         url, medical_relevance_score, urgency_score, has_professional_reply,
                         professional_id, professional_response, professional_response_date,
                         nhs_related, uk_region, views_count, replies_count,
                         language, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        post['post_id'], post['author_id'], post['category_name'],
                        post['title'], post['body'], post['created_at'], post['url'],
                        post['medical_relevance_score'], post['urgency_score'],
                        post['has_professional_reply'], post['professional_id'],
                        post['professional_response'], post['professional_response_date'],
                        post['nhs_related'], post['uk_region'],
                        post['views_count'], post['replies_count'],
                        post['language'], post['scraped_at']
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