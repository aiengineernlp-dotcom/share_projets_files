#!/usr/bin/env python3
"""
Script de collecte de données médicales depuis Reddit.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Ajout du chemin src/ au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from core.data_collection.scrapers.social.reddit_scraper import RedditScraper
from core.utils.config import load_config

def setup_logging():
    """Configure le système de logging."""
    log_dir = Path("data/logs/data/scraping")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f"reddit_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )

def parse_arguments():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description="Collecte de données médicales depuis Reddit")
    
    parser.add_argument(
        "--subreddits",
        type=str,
        nargs="+",
        default=["AskDocs", "medical", "Health", "AskDoctorSmeeee"],
        help="Liste des subreddits à scraper"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Nombre maximum de posts à collecter par subreddit"
    )
    
    parser.add_argument(
        "--comments",
        action="store_true",
        help="Collecter aussi les commentaires"
    )
    
    return parser.parse_args()

def main():
    """Point d'entrée principal du script."""
    # Configuration
    setup_logging()
    args = parse_arguments()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialisation du scraper
        scraper = RedditScraper()
        logger.info(f"Démarrage de la collecte depuis les subreddits: {', '.join(args.subreddits)}")
        
        # Collecte des posts
        posts = scraper.search_medical_posts(args.subreddits, args.limit)
        logger.info(f"Collecté {len(posts)} posts médicaux")
        
        # Collecte des commentaires si demandé
        if args.comments:
            total_comments = 0
            for post in posts:
                comments = scraper.collect_comments(post['id'])
                total_comments += len(comments)
                logger.info(f"Collecté {len(comments)} commentaires pour le post {post['id']}")
            logger.info(f"Total des commentaires collectés: {total_comments}")
            
        logger.info("Collecte terminée avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la collecte: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 