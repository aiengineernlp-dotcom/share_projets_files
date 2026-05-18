"""
Configuration globale et variables d'environnement.
"""

import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Définition du répertoire de base
BASE_DIR = Path(__file__).resolve().parent.parent

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - theknowhow_ai - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Empêcher la propagation des logs pour éviter la duplication
logger = logging.getLogger('theknowhow_ai')
logger.propagate = False

# Configuration Reddit
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
REDDIT_DB_PATH = os.getenv("REDDIT_DB_PATH", "phase1_data_collection/data/raw/social_media/reddit/sqlite/reddit.db")

REDDIT_CONFIG = {
    "client_id": REDDIT_CLIENT_ID,
    "client_secret": REDDIT_CLIENT_SECRET,
    "user_agent": REDDIT_USER_AGENT
}

# Configuration Twitter
TWITTER_CONFIG = {
    "bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
    "consumer_key": os.getenv("TWITTER_API_KEY"),
    "consumer_secret": os.getenv("TWITTER_API_SECRET"),
    "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
}

# Configuration Base de données
DATABASE_URL = os.getenv("DB_PATH", f"sqlite:///{os.path.join(BASE_DIR, 'data', 'database', 'sqlite', 'reddit.db')}")

# Configuration NLP
SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")

# Configuration API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "True").lower() == "true"

# Configuration des chemins
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Création des dossiers nécessaires
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "database"), exist_ok=True)

# Liste des pays du GCC
GCC_COUNTRIES = ["UAE", "Saudi Arabia", "Qatar", "Kuwait", "Bahrain", "Oman"]

# Vérification des variables d'environnement requises
required_env_vars = [
    "REDDIT_CLIENT_ID",
    "REDDIT_CLIENT_SECRET",
    "REDDIT_USER_AGENT",
    "TWITTER_BEARER_TOKEN",
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_TOKEN_SECRET"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Variables d'environnement manquantes : {', '.join(missing_vars)}")

# Chemins des bases de données
DATABASE_PATHS = {
    'reddit': os.getenv('REDDIT_DB_PATH', 'phase1_data_collection/data/raw/social_media/reddit/sqlite/reddit.db'),
    'twitter': os.getenv('TWITTER_DB_PATH', 'phase1_data_collection/data/raw/social_media/twitter/sqlite/twitter.db'),
    'facebook': os.getenv('FACEBOOK_DB_PATH', 'phase1_data_collection/data/raw/social_media/facebook/sqlite/facebook.db'),
    'instagram': os.getenv('INSTAGRAM_DB_PATH', 'phase1_data_collection/data/raw/social_media/instagram/sqlite/instagram.db'),
    'linkedin': os.getenv('LINKEDIN_DB_PATH', 'phase1_data_collection/data/raw/social_media/linkedin/sqlite/linkedin.db'),
    'tiktok': os.getenv('TIKTOK_DB_PATH', 'phase1_data_collection/data/raw/social_media/tiktok/sqlite/tiktok.db'),
    'youtube': os.getenv('YOUTUBE_DB_PATH', 'phase1_data_collection/data/raw/social_media/youtube/sqlite/youtube.db'),
    'telegram': os.getenv('TELEGRAM_DB_PATH', 'phase1_data_collection/data/raw/social_media/telegram/sqlite/telegram.db'),
    'whatsapp': os.getenv('WHATSAPP_DB_PATH', 'phase1_data_collection/data/raw/social_media/whatsapp/sqlite/whatsapp.db'),
    'threads': os.getenv('THREADS_DB_PATH', 'phase1_data_collection/data/raw/social_media/threads/sqlite/threads.db'),
    'mastodon': os.getenv('MASTODON_DB_PATH', 'phase1_data_collection/data/raw/social_media/mastodon/sqlite/mastodon.db'),
    'wechat': os.getenv('WECHAT_DB_PATH', 'phase1_data_collection/data/raw/social_media/wechat/sqlite/wechat.db'),
    'quora': os.getenv('QUORA_DB_PATH', 'phase1_data_collection/data/raw/social_media/quora/sqlite/quora.db'),
    'doctissimo': os.getenv('DOCTISSIMO_DB_PATH', 'phase1_data_collection/data/raw/forums/doctissimo/sqlite/doctissimo.db'),
    'sante_forum': os.getenv('SANTE_FORUM_DB_PATH', 'phase1_data_collection/data/raw/forums/sante_forum/sqlite/sante_forum.db'),
    'allodocteurs': os.getenv('ALLODOCTEURS_DB_PATH', 'phase1_data_collection/data/raw/forums/allodocteurs/sqlite/allodocteurs.db'),
    'onmeda': os.getenv('ONMEDA_DB_PATH', 'phase1_data_collection/data/raw/forums/onmeda/sqlite/onmeda.db'),
    'forum_sante': os.getenv('FORUM_SANTE_DB_PATH', 'phase1_data_collection/data/raw/forums/forum_sante/sqlite/forum_sante.db'),
    'ameli': os.getenv('AMELI_DB_PATH', 'phase1_data_collection/data/raw/websites/ameli/sqlite/ameli.db'),
    'sante_gouv': os.getenv('SANTE_GOUV_DB_PATH', 'phase1_data_collection/data/raw/websites/sante_gouv/sqlite/sante_gouv.db'),
    'medecin_fr': os.getenv('MEDECIN_FR_DB_PATH', 'phase1_data_collection/data/raw/websites/medecin_fr/sqlite/medecin_fr.db'),
    'vidal': os.getenv('VIDAL_DB_PATH', 'phase1_data_collection/data/raw/websites/vidal/sqlite/vidal.db'),
    'medicalnews': os.getenv('MEDICALNEWS_DB_PATH', 'phase1_data_collection/data/raw/websites/medicalnews/sqlite/medicalnews.db'),
    'passeportsante': os.getenv('PASSEPORTSANTE_DB_PATH', 'phase1_data_collection/data/raw/websites/passeportsante/sqlite/passeportsante.db'),
    'sante_magazine': os.getenv('SANTE_MAGAZINE_DB_PATH', 'phase1_data_collection/data/raw/websites/sante_magazine/sqlite/sante_magazine.db'),
    'top_sante': os.getenv('TOP_SANTE_DB_PATH', 'phase1_data_collection/data/raw/websites/top_sante/sqlite/top_sante.db'),
    'doctissimo_web': os.getenv('DOCTISSIMO_WEB_DB_PATH', 'phase1_data_collection/data/raw/websites/doctissimo_web/sqlite/doctissimo_web.db'),
    'medisite': os.getenv('MEDISITE_DB_PATH', 'phase1_data_collection/data/raw/websites/medisite/sqlite/medisite.db'),
    'webteb': os.getenv('WEBTEB_DB_PATH', 'phase1_data_collection/data/raw/websites/webteb/sqlite/webteb.db'),
    'dailymedicalinfo': os.getenv('DAILYMEDICALINFO_DB_PATH', 'phase1_data_collection/data/raw/websites/dailymedicalinfo/sqlite/dailymedicalinfo.db'),
    'qatar_living': os.getenv('QATAR_LIVING_DB_PATH', 'phase1_data_collection/data/raw/websites/qatar_living/sqlite/qatar_living.db'),
    'mawdoo3': os.getenv('MAWDOO3_DB_PATH', 'phase1_data_collection/data/raw/websites/mawdoo3/sqlite/mawdoo3.db'),
    'altibbi': os.getenv('ALTIBBI_DB_PATH', 'phase1_data_collection/data/raw/websites/altibbi/sqlite/altibbi.db'),
    'esante': os.getenv('ESANTE_DB_PATH', 'phase1_data_collection/data/raw/websites/esante/sqlite/esante.db'),
    'gcc_moh': os.getenv('GCC_MOH_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/moh/sqlite/moh.db'),
    'gcc_dha': os.getenv('GCC_DHA_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/dha/sqlite/dha.db'),
    'gcc_hmc': os.getenv('GCC_HMC_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/hmc/sqlite/hmc.db'),
    'gcc_sidra': os.getenv('GCC_SIDRA_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/sidra/sqlite/sidra.db'),
    'gcc_kfmc': os.getenv('GCC_KFMC_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/kfmc/sqlite/kfmc.db'),
    'gcc_kkuh': os.getenv('GCC_KKUH_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/kkuh/sqlite/kkuh.db'),
    'gcc_squ': os.getenv('GCC_SQU_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/squ/sqlite/squ.db'),
    'gcc_ku': os.getenv('GCC_KU_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/ku/sqlite/ku.db'),
    'gcc_uaeu': os.getenv('GCC_UAEU_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/uaeu/sqlite/uaeu.db'),
    'gcc_kau': os.getenv('GCC_KAU_DB_PATH', 'phase1_data_collection/data/raw/websites/gcc/kau/sqlite/kau.db')
}

# Chemins pour le stockage des données au format JSON
JSON_STORAGE_PATHS = {
    'reddit': os.getenv('REDDIT_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/reddit/json'),
    'twitter': os.getenv('TWITTER_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/twitter/json'),
    'facebook': os.getenv('FACEBOOK_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/facebook/json'),
    'instagram': os.getenv('INSTAGRAM_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/instagram/json'),
    'linkedin': os.getenv('LINKEDIN_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/linkedin/json'),
    'tiktok': os.getenv('TIKTOK_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/tiktok/json'),
    'youtube': os.getenv('YOUTUBE_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/youtube/json'),
    'telegram': os.getenv('TELEGRAM_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/telegram/json'),
    'whatsapp': os.getenv('WHATSAPP_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/whatsapp/json'),
    'threads': os.getenv('THREADS_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/threads/json'),
    'mastodon': os.getenv('MASTODON_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/mastodon/json'),
    'wechat': os.getenv('WECHAT_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/wechat/json'),
    'quora': os.getenv('QUORA_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/quora/json'),
    'doctissimo': os.getenv('DOCTISSIMO_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/doctissimo/json'),
    'sante_forum': os.getenv('SANTE_FORUM_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/sante_forum/json'),
    'allodocteurs': os.getenv('ALLODOCTEURS_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/allodocteurs/json'),
    'onmeda': os.getenv('ONMEDA_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/onmeda/json'),
    'forum_sante': os.getenv('FORUM_SANTE_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/forum_sante/json'),
    'ameli': os.getenv('AMELI_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/ameli/json'),
    'sante_gouv': os.getenv('SANTE_GOUV_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/sante_gouv/json'),
    'medecin_fr': os.getenv('MEDECIN_FR_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/medecin_fr/json'),
    'vidal': os.getenv('VIDAL_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/vidal/json'),
    'medicalnews': os.getenv('MEDICALNEWS_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/medicalnews/json'),
    'passeportsante': os.getenv('PASSEPORTSANTE_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/passeportsante/json'),
    'sante_magazine': os.getenv('SANTE_MAGAZINE_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/sante_magazine/json'),
    'top_sante': os.getenv('TOP_SANTE_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/top_sante/json'),
    'doctissimo_web': os.getenv('DOCTISSIMO_WEB_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/doctissimo_web/json'),
    'medisite': os.getenv('MEDISITE_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/medisite/json'),
    'gcc_moh': os.getenv('GCC_MOH_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/moh/json'),
    'gcc_dha': os.getenv('GCC_DHA_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/dha/json'),
    'gcc_hmc': os.getenv('GCC_HMC_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/hmc/json'),
    'gcc_sidra': os.getenv('GCC_SIDRA_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/sidra/json'),
    'gcc_kfmc': os.getenv('GCC_KFMC_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/kfmc/json'),
    'gcc_kkuh': os.getenv('GCC_KKUH_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/kkuh/json'),
    'gcc_squ': os.getenv('GCC_SQU_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/squ/json'),
    'gcc_ku': os.getenv('GCC_KU_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/ku/json'),
    'gcc_uaeu': os.getenv('GCC_UAEU_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/uaeu/json'),
    'gcc_kau': os.getenv('GCC_KAU_JSON_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/kau/json')
}

# Chemins pour le stockage des données au format CSV
CSV_STORAGE_PATHS = {
    'reddit': os.getenv('REDDIT_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/reddit/csv'),
    'twitter': os.getenv('TWITTER_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/twitter/csv'),
    'facebook': os.getenv('FACEBOOK_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/facebook/csv'),
    'instagram': os.getenv('INSTAGRAM_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/instagram/csv'),
    'linkedin': os.getenv('LINKEDIN_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/linkedin/csv'),
    'tiktok': os.getenv('TIKTOK_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/tiktok/csv'),
    'youtube': os.getenv('YOUTUBE_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/youtube/csv'),
    'telegram': os.getenv('TELEGRAM_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/telegram/csv'),
    'whatsapp': os.getenv('WHATSAPP_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/whatsapp/csv'),
    'threads': os.getenv('THREADS_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/threads/csv'),
    'mastodon': os.getenv('MASTODON_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/mastodon/csv'),
    'wechat': os.getenv('WECHAT_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/wechat/csv'),
    'quora': os.getenv('QUORA_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/social_media/quora/csv'),
    'doctissimo': os.getenv('DOCTISSIMO_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/doctissimo/csv'),
    'sante_forum': os.getenv('SANTE_FORUM_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/sante_forum/csv'),
    'allodocteurs': os.getenv('ALLODOCTEURS_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/allodocteurs/csv'),
    'onmeda': os.getenv('ONMEDA_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/onmeda/csv'),
    'forum_sante': os.getenv('FORUM_SANTE_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/forums/forum_sante/csv'),
    'ameli': os.getenv('AMELI_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/ameli/csv'),
    'sante_gouv': os.getenv('SANTE_GOUV_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/sante_gouv/csv'),
    'medecin_fr': os.getenv('MEDECIN_FR_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/medecin_fr/csv'),
    'vidal': os.getenv('VIDAL_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/vidal/csv'),
    'medicalnews': os.getenv('MEDICALNEWS_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/medicalnews/csv'),
    'passeportsante': os.getenv('PASSEPORTSANTE_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/passeportsante/csv'),
    'sante_magazine': os.getenv('SANTE_MAGAZINE_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/sante_magazine/csv'),
    'top_sante': os.getenv('TOP_SANTE_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/top_sante/csv'),
    'doctissimo_web': os.getenv('DOCTISSIMO_WEB_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/doctissimo_web/csv'),
    'medisite': os.getenv('MEDISITE_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/medisite/csv'),
    'gcc_moh': os.getenv('GCC_MOH_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/moh/csv'),
    'gcc_dha': os.getenv('GCC_DHA_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/dha/csv'),
    'gcc_hmc': os.getenv('GCC_HMC_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/hmc/csv'),
    'gcc_sidra': os.getenv('GCC_SIDRA_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/sidra/csv'),
    'gcc_kfmc': os.getenv('GCC_KFMC_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/kfmc/csv'),
    'gcc_kkuh': os.getenv('GCC_KKUH_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/kkuh/csv'),
    'gcc_squ': os.getenv('GCC_SQU_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/squ/csv'),
    'gcc_ku': os.getenv('GCC_KU_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/ku/csv'),
    'gcc_uaeu': os.getenv('GCC_UAEU_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/uaeu/csv'),
    'gcc_kau': os.getenv('GCC_KAU_CSV_STORAGE_PATH', 'phase1_data_collection/data/raw/websites/gcc/kau/csv')
} 