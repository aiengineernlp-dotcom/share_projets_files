"""
Module principal de la phase 1 de collecte de données.

RÔLE PRINCIPAL :
---------------
Ce module implémente la logique principale de la phase 1 de collecte de données.
Il définit les classes et méthodes nécessaires pour la collecte, le traitement
et l'analyse des données médicales provenant des réseaux sociaux.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Dépend de :
  * config/settings.py (configuration globale)
  * scrapers/social_media/*.py (scrapers)
  * processors/medical_analysis/*.py (analyseurs)
  * storage/database.py (gestion de la base de données)
  * nlp/language_detector.py (détection de langue)

STRUCTURE DU CONTENU :
--------------------
1. Imports et configuration
2. Classes principales :
   - DataCollector : Gestion de la collecte de données
   - DataProcessor : Traitement des données collectées
   - DataAnalyzer : Analyse des données traitées
3. Fonctions utilitaires :
   - validate_data() : Validation des données
   - export_results() : Export des résultats

FONCTIONS PRINCIPALES :
---------------------
- collect_data() : Collecte des données depuis les sources
- process_data() : Traitement des données collectées
- analyze_data() : Analyse des données traitées
- export_data() : Export des résultats

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il contient la logique principale de la phase 1
- Il définit les classes et méthodes essentielles
- Il assure la cohérence entre les différents composants
- Il est le cœur du système de collecte de données
"""

import spacy
from config.settings import logger
from scrapers.social_media.reddit_scraper import RedditScraper
from scrapers.social_media.twitter_scraper import TwitterScraper

async def run_reddit_scraper(nlp) -> dict:
    """
    Lance le scraper Reddit de manière asynchrone
    """
    try:
        scraper = RedditScraper(nlp)
        posts = scraper.scrape_medical_subreddits()
        urgent_posts = scraper.get_urgent_posts()
        
        return {
            "platform": "Reddit",
            "total_posts": len(posts),
            "urgent_posts": len(urgent_posts),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erreur lors du scraping Reddit: {e}")
        return {
            "platform": "Reddit",
            "status": "error",
            "error": str(e)
        }

async def run_twitter_scraper(nlp) -> dict:
    """
    Lance le scraper Twitter de manière asynchrone
    """
    try:
        scraper = TwitterScraper(nlp)
        posts = scraper.scrape_medical_hashtags()
        urgent_posts = scraper.get_urgent_tweets()
        
        return {
            "platform": "Twitter",
            "total_posts": len(posts),
            "urgent_posts": len(urgent_posts),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erreur lors du scraping Twitter: {e}")
        return {
            "platform": "Twitter",
            "status": "error",
            "error": str(e)
        }

def main():
    """
    Point d'entrée principal qui lance les scrapers séquentiellement
    """
    try:
        # Initialisation de spaCy
        nlp = spacy.load("en_core_web_sm")
        logger.info("Modèle spaCy chargé avec succès")
        
        # Lancement séquentiel des scrapers
        results = []
        
        # 1. Reddit
        logger.info("Démarrage du scraping Reddit...")
        reddit_result = run_reddit_scraper(nlp)
        results.append(reddit_result)
        
        # 2. Twitter
        logger.info("Démarrage du scraping Twitter...")
        twitter_result = run_twitter_scraper(nlp)
        results.append(twitter_result)
        
        # Affichage des résultats
        for result in results:
            platform = result["platform"]
            if result["status"] == "success":
                logger.info(f"{platform} - Posts collectés: {result['total_posts']}")
                logger.info(f"{platform} - Posts urgents: {result['urgent_posts']}")
            else:
                logger.error(f"{platform} - Erreur: {result['error']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la phase 1: {e}")
        return None

if __name__ == "__main__":
    main() 