"""
Script principal pour lancer tous les scrapers séquentiellement
"""

import os
import sys
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import time
import sqlite3
from tqdm import tqdm

# Configuration du logging
def setup_logging():
    """Configure le système de logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f'phase1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def create_directories():
    """Crée tous les répertoires nécessaires"""
    logger = logging.getLogger(__name__)
    logger.info("Création des répertoires de données...")
    
    # Structure de base
    directories = {
        'raw': {
            'social_media': ['reddit', 'twitter', 'daily_medical_info'],
            'forums': ['medhelp', 'healthboards', 'patient_info', 'webmd', 'healthunlocked', 'yemen', 'dubai'],
            'websites': ['dailymedicalinfo', 'webteb', 'mawdoo3', 'qatar_living', 'altibbi', 
                        'sante_magazine', 'esante', 'vidal', 'doctissimo', 'ameli', 'mon_nouveau_scraper']
        },
        'processed': ['social_media', 'forums', 'websites']
    }
    
    base_dir = Path("data")
    for data_type, subdirs in directories.items():
        for category, sources in subdirs.items() if isinstance(subdirs, dict) else [(None, subdirs)]:
            for source in sources:
                path = base_dir / data_type / (category if category else '') / source / 'sqlite'
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Créé : {path}")

def setup_database_paths():
    """Configure les chemins des bases de données"""
    logger = logging.getLogger(__name__)
    logger.info("Configuration des chemins des bases de données...")
    
    # Chemins des bases de données
    DATABASE_PATHS = {
        'REDDIT_DB_PATH': 'phase1_data_collection/data/raw/social_media/reddit/sqlite/reddit.db',
        'TWITTER_DB_PATH': 'phase1_data_collection/data/raw/social_media/twitter/sqlite/twitter.db',
        'DAILYMEDICALINFO_DB_PATH': 'phase1_data_collection/data/raw/social_media/daily_medical_info/sqlite/daily_medical_info.db',
        'MEDHELP_DB_PATH': 'phase1_data_collection/data/raw/forums/medhelp/sqlite/medhelp.db',
        'HEALTHBOARDS_DB_PATH': 'phase1_data_collection/data/raw/forums/healthboards/sqlite/healthboards.db',
        'PATIENT_INFO_DB_PATH': 'phase1_data_collection/data/raw/forums/patient_info/sqlite/patient_info.db',
        'WEBMD_DB_PATH': 'phase1_data_collection/data/raw/forums/webmd/sqlite/webmd.db',
        'HEALTHUNLOCKED_DB_PATH': 'phase1_data_collection/data/raw/forums/healthunlocked/sqlite/healthunlocked.db',
        'YEMEN_FORUM_DB_PATH': 'phase1_data_collection/data/raw/forums/yemen/sqlite/yemen_forum.db',
        'DUBAI_FORUM_DB_PATH': 'phase1_data_collection/data/raw/forums/dubai/sqlite/dubai_forum.db',
        'DAILYMEDICALINFO_WEB_DB_PATH': 'phase1_data_collection/data/raw/websites/dailymedicalinfo/sqlite/dailymedicalinfo.db',
        'WEBTEB_DB_PATH': 'phase1_data_collection/data/raw/websites/webteb/sqlite/webteb.db',
        'MAWDOO3_DB_PATH': 'phase1_data_collection/data/raw/websites/mawdoo3/sqlite/mawdoo3.db',
        'QATAR_LIVING_DB_PATH': 'phase1_data_collection/data/raw/websites/qatar_living/sqlite/qatar_living.db',
        'ALTIBBI_DB_PATH': 'phase1_data_collection/data/raw/websites/altibbi/sqlite/altibbi.db',
        'SANTE_MAGAZINE_DB_PATH': 'phase1_data_collection/data/raw/websites/sante_magazine/sqlite/sante_magazine.db',
        'ESANTE_DB_PATH': 'phase1_data_collection/data/raw/websites/esante/sqlite/esante.db',
        'VIDAL_DB_PATH': 'phase1_data_collection/data/raw/websites/vidal/sqlite/vidal.db',
        'DOCTISSIMO_DB_PATH': 'phase1_data_collection/data/raw/websites/doctissimo/sqlite/doctissimo.db',
        'AMELI_DB_PATH': 'phase1_data_collection/data/raw/websites/ameli/sqlite/ameli.db',
        'MON_NOUVEAU_SCRAPER_DB_PATH': 'phase1_data_collection/data/raw/websites/mon_nouveau_scraper/sqlite/mon_nouveau_scraper.db'
    }
    
    for env_var, path in DATABASE_PATHS.items():
        os.environ[env_var] = path
        logger.info(f"Configuré {env_var} = {path}")

def run_scraper(scraper_path: str, timeout: int = 3600) -> Dict:
    """Lance un scraper et retourne les résultats"""
    logger = logging.getLogger(__name__)
    start_time = time.time()
    
    try:
        logger.info(f"Démarrage du scraper : {scraper_path}")
        
        # Exécution du scraper avec PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{env.get('PYTHONPATH', '')}:../"
        
        result = subprocess.run(
            ['python', scraper_path],
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Analyse des résultats
        execution_time = time.time() - start_time
        success = result.returncode == 0
        
        # Logging des résultats
        if result.stdout:
            logger.info(f"[{scraper_path}] {result.stdout.strip()}")
        if result.stderr:
            logger.error(f"[{scraper_path} - ERREURS] {result.stderr.strip()}")
            
        return {
            'success': success,
            'execution_time': execution_time,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout dépassé pour {scraper_path}")
        return {
            'success': False,
            'execution_time': timeout,
            'return_code': -1,
            'error': 'Timeout'
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du scraper {scraper_path}: {str(e)}")
        return {
            'success': False,
            'execution_time': time.time() - start_time,
            'return_code': -1,
            'error': str(e)
        }

def main():
    """Point d'entrée principal"""
    logger = setup_logging()
    
    try:
        logger.info("Démarrage de la phase 1 de collecte de données")
        
        # Initialisation
        create_directories()
        setup_database_paths()
        
        # Liste des scrapers à lancer
        scrapers = [
            # Réseaux sociaux
            'scrapers/social_media/reddit_scraper.py',
            'scrapers/social_media/twitter_scraper.py',
            'scrapers/social_media/daily_medical_info_scraper.py',
            
            # Forums
            'scrapers/forums/medhelp_scraper.py',
            'scrapers/forums/healthboards_scraper.py',
            'scrapers/forums/patient_info_scraper.py',
            'scrapers/forums/webmd_scraper.py',
            'scrapers/forums/healthunlocked_scraper.py',
            'scrapers/forums/yemen_forum_scraper.py',
            'scrapers/forums/dubai_forum_scraper.py',
            
            # Sites web
            'scrapers/websites/dailymedicalinfo_scraper.py',
            'scrapers/websites/webteb_scraper.py',
            'scrapers/websites/mawdoo3_scraper.py',
            'scrapers/websites/qatar_living_scraper.py',
            'scrapers/websites/altibbi_scraper.py',
            'scrapers/websites/sante_magazine_scraper.py',
            'scrapers/websites/esante_scraper.py',
            'scrapers/websites/vidal_scraper.py',
            'scrapers/websites/doctissimo_scraper.py',
            'scrapers/websites/ameli_scraper.py',
            'scrapers/websites/mon_nouveau_scraper.py'
        ]
        
        # Statistiques d'exécution
        stats = {
            'total': len(scrapers),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'total_time': 0
        }
        
        # Exécution séquentielle des scrapers
        for scraper in tqdm(scrapers, desc="Exécution des scrapers"):
            if os.path.exists(scraper):
                result = run_scraper(scraper)
                stats['total_time'] += result['execution_time']
                
                if result['success']:
                    stats['success'] += 1
                    logger.info(f"Scraper terminé avec succès : {scraper}")
                else:
                    stats['failed'] += 1
                    logger.error(f"Scraper échoué : {scraper}")
            else:
                stats['skipped'] += 1
                logger.warning(f"Scraper non trouvé : {scraper}")
            
            time.sleep(5)  # Pause entre chaque scraper
        
        # Résumé final
        logger.info("\nRésumé de l'exécution :")
        logger.info(f"Total des scrapers : {stats['total']}")
        logger.info(f"Succès : {stats['success']}")
        logger.info(f"Échecs : {stats['failed']}")
        logger.info(f"Ignorés : {stats['skipped']}")
        logger.info(f"Temps total d'exécution : {stats['total_time']:.2f} secondes")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la phase 1 : {str(e)}")
        raise

if __name__ == "__main__":
    main()