"""
Pipeline complet pour la Phase 1 : Collecte et Analyse des Données.
Ce module coordonne l'ensemble du processus de la Phase 1, de la collecte à l'analyse.
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Import des modules de collecte
from src.core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper import DoctissimoScraper
from src.core.phase_1_data_collection.scrapers.social_media.reddit_scraper import RedditScraper
from src.core.phase_1_data_collection.scrapers.social_media.twitter_scraper import TwitterScraper

# Import des modules de prétraitement
from src.core.phase_1_data_collection.preprocessing.text_processor import TextProcessor

# Import des modules d'analyse
from src.core.phase_1_data_collection.analysis.medical_analyzer import MedicalAnalyzer
from src.utils.nlp import NLPProcessor

# Import des modules de nettoyage
from src.core.phase_1_data_collection.processors.data_cleaner import DataCleaner

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/logs/phase1_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("phase1_pipeline")

class Phase1Pipeline:
    """Pipeline complet pour la Phase 1 du projet."""
    
    def __init__(self):
        """Initialise le pipeline de la Phase 1."""
        # Initialisation des chemins
        self.data_dir = "data"
        self.processed_dir = os.path.join(self.data_dir, "processed")
        self.raw_dir = os.path.join(self.data_dir, "databases")
        
        # Création des dossiers nécessaires
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Initialisation des scrapers
        self.scrapers = {
            "doctissimo": DoctissimoScraper(),
            "reddit": RedditScraper(),
            "twitter": TwitterScraper()
        }
        
        # Initialisation des processeurs
        self.text_processor = TextProcessor()
        self.medical_analyzer = MedicalAnalyzer()
        self.data_cleaner = DataCleaner()
        self.nlp_processor = NLPProcessor()
        
        # Mots-clés pour la recherche d'avis médicaux
        self.medical_opinion_keywords = [
            "second opinion", "deuxième avis", "diagnosis confirmation",
            "doctor advice", "medical uncertainty", "doute diagnostic",
            "consultation médicale", "avis médical", "expertise médicale"
        ]
        
        # Mots-clés pour filtrer les contenus liés au second avis médical
        self.second_opinion_keywords = [
            "second opinion", "deuxième avis", "second avis", "autre avis médical", 
            "consulter un autre médecin", "avis spécialiste", "contre-expertise médicale", 
            "diagnostic contradictoire", "opinion médicale différente", "consultation spécialisée", 
            "erreur médicale", "diagnostic erroné", "remise en question diagnostic", 
            "doute diagnostic", "confirmation diagnostic", "validation traitement", 
            "désaccord médical", "conflit médical", "avis contradictoires", 
            "plusieurs médecins", "expertise médicale", "need another doctor", 
            "different medical opinion", "conflicting diagnosis", "alternative medical opinion", 
            "disagree with doctor", "doctor was wrong", "seeking medical confirmation", 
            "validate diagnosis", "unsure about diagnosis", "medical misdiagnosis", 
            "doctor disagreement", "medical consultation", "specialist opinion", 
            "medical expert opinion", "contradicting medical advice", "questioning treatment", 
            "medical error", "wrong treatment", "medical consultation advice", "trust doctor opinion"
        ]
        
        logger.info("Pipeline de la Phase 1 initialisé")
    
    async def collect_data(self):
        """Collecte les données depuis toutes les sources."""
        logger.info("Début de la collecte de données")
        
        for source, scraper in self.scrapers.items():
            try:
                logger.info(f"Collecte depuis {source}")
                await scraper.run()
                logger.info(f"Collecte depuis {source} terminée")
            except Exception as e:
                logger.error(f"Erreur lors de la collecte depuis {source}: {e}")
        
        logger.info("Collecte de données terminée")
    
    async def process_data(self):
        """Prétraite et analyse les données collectées."""
        logger.info("Début du prétraitement et de l'analyse des données")
        
        # Traitement des données de Doctissimo
        await self._process_doctissimo_data()
        
        # Traitement des données de Reddit
        await self._process_reddit_data()
        
        # Traitement des données de Twitter
        await self._process_twitter_data()
        
        # Filtrer et mettre en évidence les contenus liés au second avis médical
        await self.filter_second_opinion_content()
        
        logger.info("Prétraitement et analyse des données terminés")
    
    async def _process_doctissimo_data(self):
        """Traite les données collectées depuis Doctissimo."""
        doctissimo_dir = os.path.join(self.raw_dir, "medical_websites", "doctissimo")
        processed_dir = os.path.join(self.processed_dir, "doctissimo")
        os.makedirs(processed_dir, exist_ok=True)
        
        logger.info(f"Traitement des données Doctissimo depuis {doctissimo_dir}")
        
        # Parcours des fichiers JSON
        for filename in os.listdir(doctissimo_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(doctissimo_dir, filename)
                
                try:
                    # Chargement des données
                    with open(file_path, 'r', encoding='utf-8') as f:
                        article_data = json.load(f)
                    
                    # Nettoyage du texte
                    if 'content' in article_data:
                        article_data['cleaned_content'] = self.data_cleaner.clean_text(article_data['content'])
                    
                    # Prétraitement du texte
                    if 'cleaned_content' in article_data and article_data['cleaned_content']:
                        article_data['processed_content'] = self.text_processor.preprocess_text(article_data['cleaned_content'])
                    
                    # Analyse médicale
                    if 'processed_content' in article_data and article_data['processed_content']:
                        analysis_results = self.medical_analyzer.analyze_post(article_data)
                        article_data.update(analysis_results)
                    
                    # Vérification des mots-clés d'avis médical
                    article_data['is_medical_opinion_related'] = self._check_medical_opinion_keywords(article_data)
                    
                    # Sauvegarde des données traitées
                    processed_file = os.path.join(processed_dir, f"processed_{filename}")
                    with open(processed_file, 'w', encoding='utf-8') as f:
                        json.dump(article_data, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"Article {filename} traité et sauvegardé")
                    
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de {filename}: {e}")
    
    async def _process_reddit_data(self):
        """Traite les données collectées depuis Reddit."""
        reddit_dir = os.path.join(self.raw_dir, "social_media", "reddit")
        processed_dir = os.path.join(self.processed_dir, "reddit")
        os.makedirs(processed_dir, exist_ok=True)
        
        logger.info(f"Traitement des données Reddit depuis {reddit_dir}")
        
        # Implémentation similaire à _process_doctissimo_data pour Reddit
        # À adapter selon la structure des données Reddit
    
    async def _process_twitter_data(self):
        """Traite les données collectées depuis Twitter."""
        twitter_dir = os.path.join(self.raw_dir, "social_media", "twitter")
        processed_dir = os.path.join(self.processed_dir, "twitter")
        os.makedirs(processed_dir, exist_ok=True)
        
        logger.info(f"Traitement des données Twitter depuis {twitter_dir}")
        
        # Implémentation similaire à _process_doctissimo_data pour Twitter
        # À adapter selon la structure des données Twitter
    
    def _check_medical_opinion_keywords(self, data: Dict[str, Any]) -> bool:
        """
        Vérifie si le contenu contient des mots-clés liés à la recherche d'avis médical.
        
        Args:
            data: Données de l'article ou du post
            
        Returns:
            bool: True si des mots-clés sont trouvés, False sinon
        """
        content = ""
        if 'processed_content' in data and data['processed_content']:
            content = data['processed_content']
        elif 'cleaned_content' in data and data['cleaned_content']:
            content = data['cleaned_content']
        elif 'content' in data and data['content']:
            content = data['content']
        elif 'title' in data and data['title']:
            content = data['title']
        
        if not content:
            return False
        
        content = content.lower()
        
        for keyword in self.medical_opinion_keywords:
            if keyword.lower() in content:
                return True
        
        return False
    
    async def filter_second_opinion_content(self):
        """Filtre et met en évidence les contenus liés au second avis médical."""
        logger.info("Filtrage des contenus liés au second avis médical")
        
        # Créer le répertoire pour les données filtrées s'il n'existe pas
        os.makedirs("data/processed/second_opinion", exist_ok=True)
        
        # Filtrer les données Reddit
        await self._filter_reddit_data()
        
        # Filtrer les articles médicaux
        await self._filter_medical_articles()
        
        logger.info("Filtrage des contenus terminé")
    
    async def _filter_reddit_data(self):
        """Filtre les données Reddit liées au second avis médical."""
        try:
            # Utiliser SQLite pour filtrer les données
            from src.core.phase_1_data_collection.storage.sqlite_storage import SQLiteStorage
            
            # Chemin vers la base de données Reddit
            db_path = os.environ.get('REDDIT_DB_PATH', 'data/databases/social_media/reddit/reddit_data.db')
            if os.path.isdir(db_path):
                db_path = os.path.join(db_path, 'reddit_data.db')
            
            storage = SQLiteStorage(db_path)
            
            # Construire la requête SQL pour filtrer les contenus
            query_parts = []
            for keyword in self.second_opinion_keywords:
                # Échapper les apostrophes dans les mots-clés
                escaped_keyword = keyword.replace("'", "''")
                query_parts.append(f"title LIKE '%{escaped_keyword}%' OR content LIKE '%{escaped_keyword}%'")
            
            query = f"""
                SELECT * FROM reddit_data 
                WHERE {' OR '.join(query_parts)}
            """
            
            # Exécuter la requête
            with storage._get_connection() as conn:
                conn.row_factory = storage._dict_factory
                cursor = conn.cursor()
                cursor.execute(query)
                filtered_data = cursor.fetchall()
            
            # Sauvegarder les résultats filtrés
            output_file = "data/processed/second_opinion/reddit_second_opinion.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Données Reddit filtrées: {len(filtered_data)} éléments liés au second avis médical")
            logger.info(f"Données sauvegardées dans {output_file}")
            
        except Exception as e:
            logger.error(f"Erreur lors du filtrage des données Reddit: {e}")
    
    async def _filter_medical_articles(self):
        """Filtre les articles médicaux liés au second avis médical."""
        try:
            # Utiliser SQLite pour filtrer les données
            from src.core.phase_1_data_collection.storage.sqlite_storage import SQLiteStorage
            
            # Chemin vers la base de données des articles médicaux
            db_path = os.environ.get('MEDICAL_DB_PATH', 'data/databases/medical_websites/medical_data.db')
            
            storage = SQLiteStorage(db_path)
            
            # Construire la requête SQL pour filtrer les contenus
            query_parts = []
            for keyword in self.second_opinion_keywords:
                # Échapper les apostrophes dans les mots-clés
                escaped_keyword = keyword.replace("'", "''")
                query_parts.append(f"title LIKE '%{escaped_keyword}%' OR content LIKE '%{escaped_keyword}%'")
            
            query = f"""
                SELECT * FROM medical_articles 
                WHERE {' OR '.join(query_parts)}
            """
            
            # Exécuter la requête
            with storage._get_connection() as conn:
                conn.row_factory = storage._dict_factory
                cursor = conn.cursor()
                cursor.execute(query)
                filtered_data = cursor.fetchall()
            
            # Sauvegarder les résultats filtrés
            output_file = "data/processed/second_opinion/medical_articles_second_opinion.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Articles médicaux filtrés: {len(filtered_data)} éléments liés au second avis médical")
            logger.info(f"Données sauvegardées dans {output_file}")
            
        except Exception as e:
            logger.error(f"Erreur lors du filtrage des articles médicaux: {e}")
    
    async def analyze_data(self):
        """Analyse les données collectées pour identifier les posts pertinents."""
        logger.info("Début de l'analyse des données")
        
        # Analyse des posts Reddit
        try:
            reddit_db_path = os.path.join(self.raw_dir, "social_media", "reddit", "reddit_data.db")
            if os.path.exists(reddit_db_path):
                from src.core.phase_1_data_collection.storage.sqlite_storage import SQLiteStorage
                storage = SQLiteStorage(reddit_db_path)
                
                # Récupérer les posts non analysés
                try:
                    posts = storage.get_all_posts()
                    logger.info(f"Analyse de {len(posts)} posts Reddit")
                    
                    analyzed_posts = []
                    second_opinion_posts = []
                    
                    for post in posts:
                        # Prétraitement du texte
                        title = post.get('title', '')
                        content = post.get('selftext', '')
                        
                        # Analyse NLP pour la classification
                        analysis = self.nlp_processor.analyze_post(title, content)
                        
                        # Ajouter l'analyse au post
                        post['analysis'] = analysis
                        analyzed_posts.append(post)
                        
                        # Filtrer les posts liés au second avis médical
                        if analysis['category'] != "General Medical Question":
                            second_opinion_posts.append(post)
                            logger.info(f"Post classifié comme '{analysis['category']}': {title[:50]}...")
                    
                    # Sauvegarder les résultats
                    os.makedirs(self.processed_dir, exist_ok=True)
                    output_file = os.path.join(self.processed_dir, "analyzed_reddit_posts.json")
                    with open(output_file, 'w') as f:
                        json.dump(analyzed_posts, f, indent=2)
                    
                    second_opinion_file = os.path.join(self.processed_dir, "second_opinion_posts.json")
                    with open(second_opinion_file, 'w') as f:
                        json.dump(second_opinion_posts, f, indent=2)
                    
                    logger.info(f"Analyse terminée. {len(second_opinion_posts)} posts liés au second avis médical identifiés.")
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des posts Reddit: {e}")
                    logger.info("Vérifiez que la base de données a été correctement créée et contient des données.")
            else:
                logger.warning(f"Base de données Reddit non trouvée: {reddit_db_path}")
                logger.info("Exécutez d'abord la collecte de données avec --collect-only")
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des posts Reddit: {e}")
        
        # Analyse des articles médicaux
        try:
            medical_db_path = os.path.join(self.raw_dir, "medical_websites", "medical_data.db")
            if os.path.exists(medical_db_path):
                from src.core.phase_1_data_collection.storage.sqlite_storage import SQLiteStorage
                storage = SQLiteStorage(medical_db_path)
                
                # Récupérer les articles non analysés
                try:
                    articles = storage.get_all_articles()
                    logger.info(f"Analyse de {len(articles)} articles médicaux")
                    
                    analyzed_articles = []
                    second_opinion_articles = []
                    
                    for article in articles:
                        # Prétraitement du texte
                        title = article.get('title', '')
                        content = article.get('content', '')
                        
                        # Analyse NLP pour la classification
                        analysis = self.nlp_processor.analyze_post(title, content)
                        
                        # Ajouter l'analyse à l'article
                        article['analysis'] = analysis
                        analyzed_articles.append(article)
                        
                        # Filtrer les articles liés au second avis médical
                        if analysis['category'] != "General Medical Question":
                            second_opinion_articles.append(article)
                            logger.info(f"Article classifié comme '{analysis['category']}': {title[:50]}...")
                    
                    # Sauvegarder les résultats
                    os.makedirs(self.processed_dir, exist_ok=True)
                    output_file = os.path.join(self.processed_dir, "analyzed_medical_articles.json")
                    with open(output_file, 'w') as f:
                        json.dump(analyzed_articles, f, indent=2)
                    
                    second_opinion_file = os.path.join(self.processed_dir, "second_opinion_articles.json")
                    with open(second_opinion_file, 'w') as f:
                        json.dump(second_opinion_articles, f, indent=2)
                    
                    logger.info(f"Analyse terminée. {len(second_opinion_articles)} articles liés au second avis médical identifiés.")
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des articles médicaux: {e}")
                    logger.info("Vérifiez que la base de données a été correctement créée et contient des données.")
            else:
                logger.warning(f"Base de données médicale non trouvée: {medical_db_path}")
                logger.info("Exécutez d'abord la collecte de données avec --collect-only")
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des articles médicaux: {e}")
        
        logger.info("Analyse des données terminée")
    
    async def run(self):
        """Exécute l'ensemble du pipeline de la Phase 1."""
        logger.info("Démarrage du pipeline de la Phase 1")
        
        # Étape 1: Collecte des données
        await self.collect_data()
        
        # Étape 2: Prétraitement et analyse des données
        await self.process_data()
        
        # Étape 3: Analyse des données
        await self.analyze_data()
        
        logger.info("Pipeline de la Phase 1 terminé")

async def main():
    """Point d'entrée principal."""
    pipeline = Phase1Pipeline()
    await pipeline.run()

if __name__ == "__main__":
    asyncio.run(main()) 