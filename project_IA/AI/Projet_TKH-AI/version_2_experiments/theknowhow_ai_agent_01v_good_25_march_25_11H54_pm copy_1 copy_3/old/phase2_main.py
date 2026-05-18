import logging
import os
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv
from database_manager import init_db, save_post
from data_collection import RedditScraper
from modules.nlp import NLPProcessor, EntityExtractor

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logger
logger = logging.getLogger(__name__)

# Vérification des variables d'environnement
logger.info("Vérification des variables d'environnement Reddit:")
logger.info(f"REDDIT_CLIENT_ID: {'Configuré' if os.getenv('REDDIT_CLIENT_ID') else 'Non configuré'}")
logger.info(f"REDDIT_CLIENT_SECRET: {'Configuré' if os.getenv('REDDIT_CLIENT_SECRET') else 'Non configuré'}")
logger.info(f"REDDIT_USER_AGENT: {'Configuré' if os.getenv('REDDIT_USER_AGENT') else 'Non configuré'}")

def main():
    """Fonction principale pour la collecte et l'analyse des données."""
    try:
        # Initialisation de la base de données
        logger.info("Initialisation de la base de données...")
        init_db()
        logger.info("Base de données initialisée avec succès")
        
        # Configuration du scraper Reddit
        logger.info("Configuration du scraper Reddit...")
        scraper = RedditScraper()
        
        # Configuration des processeurs NLP
        logger.info("Configuration des processeurs NLP...")
        nlp_processor = NLPProcessor()
        entity_extractor = EntityExtractor()
        
        # Définition des subreddits et des requêtes
        subreddits = ["AskDocs", "DiagnoseMe", "medical_advice"]
        queries = ["help", "diagnose", "advice", "symptoms"]
        
        # Collecte des posts
        total_posts = 0
        for subreddit in subreddits:
            logger.info(f"\nTraitement des posts de r/{subreddit}:")
            posts = scraper.scrape_subreddit(subreddit, " ".join(queries))
            
            for post in posts:
                try:
                    # Analyse du texte avec NLP
                    text = post["title"] + " " + post["body"]
                    nlp_results = nlp_processor.analyze_post(post["title"], post["body"])
                    entities = entity_extractor.extract_entities(text)
                    
                    # Préparation des données pour la sauvegarde
                    post_data = {
                        "id": post["id"],
                        "title": post["title"],
                        "body": post["body"],
                        "url": post["url"],
                        "created_utc": post["created_utc"],
                        "subreddit": subreddit,
                        "author": post["author"],
                        "category": nlp_results["category"],
                        "second_opinion_score": nlp_results["second_opinion_score"],
                        "urgency_score": nlp_results["urgency_score"],
                        "medical_relevance_score": nlp_results["medical_relevance_score"],
                        "sentiment_score": nlp_results["sentiment_score"],
                        "overall_score": nlp_results["overall_score"],
                        "country": None,  # À implémenter avec géolocalisation
                        "city": None,     # À implémenter avec géolocalisation
                        "region": None,   # À implémenter avec géolocalisation
                        "latitude": None, # À implémenter avec géolocalisation
                        "longitude": None # À implémenter avec géolocalisation
                    }
                    
                    # Sauvegarde dans la base de données
                    if save_post(post_data):
                        total_posts += 1
                        logger.info(f"Post sauvegardé: {post['title'][:50]}... (Catégorie: {nlp_results['category']})")
                    else:
                        logger.error(f"Erreur lors de la sauvegarde du post: {post['title'][:50]}...")
                        
                except Exception as e:
                    logger.error(f"Erreur lors du traitement : {e}")
                    continue
                    
        logger.info(f"\nTotal des posts sauvegardés : {total_posts}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution : {e}")
        raise

if __name__ == "__main__":
    main() 