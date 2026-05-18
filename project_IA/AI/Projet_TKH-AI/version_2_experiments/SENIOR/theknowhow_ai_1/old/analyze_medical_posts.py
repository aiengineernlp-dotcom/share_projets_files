#!/usr/bin/env python3
"""
Script pour analyser les posts médicaux collectés.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from src.core.data_collection.preprocessing.text_processor import TextProcessor
from src.core.data_collection.analysis.medical_analyzer import MedicalAnalyzer
from src.core.data_collection.storage.sqlite_storage import SQLiteStorage

def setup_logging(log_dir: Path) -> None:
    """Configure la journalisation."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def parse_arguments() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Analyse les posts médicaux collectés."
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help="Nombre de posts à traiter par lot"
    )
    parser.add_argument(
        '--min-relevance',
        type=float,
        default=0.5,
        help="Score minimum de pertinence pour conserver un post"
    )
    return parser.parse_args()

def process_batch(
    processor: TextProcessor,
    analyzer: MedicalAnalyzer,
    posts: List[Dict[str, Any]],
    min_relevance: float
) -> List[Dict[str, Any]]:
    """Traite un lot de posts."""
    processed_posts = []
    
    for post in posts:
        try:
            # Prétraitement
            processed_data = processor.process_medical_post(post)
            
            # Analyse
            analyzed_data = analyzer.analyze_post(processed_data)
            
            # Filtre sur la pertinence
            if analyzed_data['relevance_score'] >= min_relevance:
                processed_posts.append(analyzed_data)
                
        except Exception as e:
            logging.error(f"Erreur lors du traitement du post {post.get('id')}: {str(e)}")
            continue
            
    return processed_posts

def main() -> None:
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Configuration
    project_root = Path(__file__).parent.parent.parent
    log_dir = project_root / "data" / "logs" / "analysis"
    setup_logging(log_dir)
    
    # Initialisation des composants
    storage = SQLiteStorage(project_root / "data" / "databases" / "medical_posts.db")
    processor = TextProcessor()
    analyzer = MedicalAnalyzer()
    
    logging.info("Démarrage de l'analyse des posts médicaux")
    
    try:
        # Récupération des posts non traités
        unprocessed_posts = storage.get_unprocessed_posts()
        total_posts = len(unprocessed_posts)
        logging.info(f"Nombre total de posts à analyser : {total_posts}")
        
        # Traitement par lots
        processed_count = 0
        for i in range(0, total_posts, args.batch_size):
            batch = unprocessed_posts[i:i + args.batch_size]
            
            # Traitement du lot
            processed_batch = process_batch(
                processor,
                analyzer,
                batch,
                args.min_relevance
            )
            
            # Sauvegarde des résultats
            for post in processed_batch:
                storage.save_analyzed_post(post)
                processed_count += 1
                
            # Mise à jour du statut
            for post in batch:
                storage.mark_post_as_processed(post['id'])
                
            logging.info(
                f"Progression : {i + len(batch)}/{total_posts} posts traités "
                f"({processed_count} conservés)"
            )
            
        logging.info("Analyse terminée avec succès")
        logging.info(f"Total des posts conservés : {processed_count}")
        
    except Exception as e:
        logging.error(f"Erreur lors de l'analyse : {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 