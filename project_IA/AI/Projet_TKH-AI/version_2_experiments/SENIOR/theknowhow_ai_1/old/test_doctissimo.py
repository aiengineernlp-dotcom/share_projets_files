#!/usr/bin/env python3
"""
Script pour tester le scraper Doctissimo.
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime

# Ajouter le répertoire racine au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))  # Remonter de src/scripts à la racine
sys.path.insert(0, root_dir)

# Définir les chemins
DATA_DIR = os.path.join(root_dir, "data")
LOG_DIR = os.path.join(DATA_DIR, "log")
OUTPUT_DIR = os.path.join(DATA_DIR, "databases")
MEDICAL_WEBSITES_DIR = os.path.join(OUTPUT_DIR, "medical_websites")
DOCTISSIMO_DIR = os.path.join(MEDICAL_WEBSITES_DIR, "doctissimo")

# Créer les dossiers nécessaires
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MEDICAL_WEBSITES_DIR, exist_ok=True)
os.makedirs(DOCTISSIMO_DIR, exist_ok=True)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "doctissimo_test.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("doctissimo_test")

# Importer le scraper Doctissimo
try:
    from src.core.phase_1_data_collection.scrapers.medical_websites.doctissimo_scraper import DoctissimoScraper
    logger.info("Scraper Doctissimo importé avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'import du scraper Doctissimo: {e}")
    sys.exit(1)

async def main():
    """Fonction principale pour tester le scraper Doctissimo."""
    logger.info("Démarrage du test du scraper Doctissimo")
    
    try:
        # Initialiser le scraper
        scraper = DoctissimoScraper()
        scraper.max_articles = 5  # Limiter à 5 articles pour le test
        logger.info("Scraper Doctissimo initialisé")
        
        # Connexion
        await scraper.initialize()
        logger.info("Connexion établie")
        
        # Collecter les données
        for category in scraper.categories[:1]:  # Tester seulement la première catégorie
            logger.info(f"Collecte des articles de la catégorie: {category}")
            urls = await scraper.get_article_urls(category)
            logger.info(f"URLs trouvées: {len(urls)}")
            
            for url in urls[:2]:  # Tester seulement les 2 premiers articles
                logger.info(f"Traitement de l'URL: {url}")
                article_data = await scraper.scrape_page(url)
                if article_data:
                    # Sauvegarde des données
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"doctissimo_test_{timestamp}.json"
                    filepath = os.path.join(DOCTISSIMO_DIR, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(article_data, f, ensure_ascii=False, indent=2)
                        
                    logger.info(f"Article sauvegardé dans {filepath}")
        
        await scraper.cleanup()
        logger.info("Test terminé avec succès")
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors du test du scraper Doctissimo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("Démarrage du test du scraper Doctissimo...")
    exit_code = asyncio.run(main())
    print(f"Test terminé avec code de sortie {exit_code}. Vérifiez les logs pour plus de détails.") 