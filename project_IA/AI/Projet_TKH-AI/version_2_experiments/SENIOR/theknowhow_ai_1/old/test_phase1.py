import os
import logging
import praw
import sqlite3
import spacy
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
import pytest
from datetime import datetime
from phase1_data_collection import DatabaseManager, DataCollector, DataAnalyzer

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# --- Configuration de Reddit API ---
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MyRedditBot/0.1")


# Modèle de données pour les posts
class Post(BaseModel):
    id: str
    title: str
    url: str
    created_utc: float = None


class Database:
    def __init__(self, db_path="phase1_data.db"):
        self.db_path = db_path
        self._create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    created_utc REAL
                )
                """)
                conn.commit()
                logger.info("Tables de base de données initialisées avec succès")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la création des tables: {e}")
            raise

    def insert_post(self, post: Post):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO posts VALUES (?, ?, ?, ?)",
                    (post.id, post.title, post.url, post.created_utc)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'insertion dans la base de données: {e}")
            return False

    def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, title, url, created_utc FROM posts ORDER BY created_utc DESC LIMIT ?",
                    (limit,)
                )
                posts = cursor.fetchall()
                return [
                    {"id": p[0], "title": p[1], "url": p[2], "created_utc": p[3]}
                    for p in posts
                ]
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des posts: {e}")
            return []


class RedditScraper:
    def __init__(self):
        # Vérification des identifiants
        if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
            logger.error("Les identifiants Reddit sont manquants")
            raise ValueError("Les identifiants Reddit doivent être définis dans le fichier .env")

        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
            logger.info("Connexion à l'API Reddit établie")
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à l'API Reddit: {e}")
            raise

        # Initialisation de NLP si nécessaire
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Modèle NLP chargé avec succès")
        except Exception as e:
            logger.warning(f"Impossible de charger le modèle NLP: {e}")
            self.nlp = None

    def scrape_subreddit(self, subreddit: str, query: str, limit: int = 10, db: Database = None):
        if not db:
            logger.error("Base de données non fournie")
            return []

        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            posts_scraped = 0

            logger.info(f"Recherche de '{query}' dans r/{subreddit}, limite: {limit}")

            for submission in subreddit_obj.search(query, limit=limit):
                post = Post(
                    id=submission.id,
                    title=submission.title,
                    url=submission.url,
                    created_utc=submission.created_utc
                )

                if db.insert_post(post):
                    posts_scraped += 1
                    logger.info(f"Post enregistré: {submission.title[:50]}...")

            logger.info(f"Scraping terminé: {posts_scraped} nouveaux posts enregistrés")
            return posts_scraped
        except Exception as e:
            logger.error(f"Erreur lors du scraping: {e}")
            return 0


# --- API FastAPI ---
app = FastAPI(title="Reddit Scraper API")
db = Database()
scraper = RedditScraper()


def get_db():
    return db


@app.get("/", tags=["Général"])
def read_root():
    return {"message": "Bienvenue sur l'API Reddit Scraper!"}


@app.get("/posts", response_model=List[Dict[str, Any]], tags=["Posts"])
def get_posts(db: Database = Depends(get_db), limit: int = 10):
    posts = db.get_recent_posts(limit)
    if not posts:
        logger.warning("Aucun post trouvé dans la base de données")
        return []
    return posts


@app.post("/scrape", tags=["Scraping"])
def scrape_endpoint(subreddit: str, query: str, limit: int = 10, db: Database = Depends(get_db)):
    try:
        posts_count = scraper.scrape_subreddit(subreddit, query, limit, db)
        return {"message": f"{posts_count} nouveaux posts ont été récupérés"}
    except Exception as e:
        logger.error(f"Erreur lors du scraping via l'API: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Création d'un fichier .env d'exemple si non existant
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""# Remplacez ces valeurs par vos identifiants Reddit
REDDIT_CLIENT_ID=votre_client_id
REDDIT_CLIENT_SECRET=votre_client_secret
REDDIT_USER_AGENT=MyRedditBot/0.1 by @YourUsername
""")
        logger.info("Fichier .env d'exemple créé. Veuillez le remplir avec vos identifiants.")

    # Scraping initial si les identifiants sont configurés
    if all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]) and REDDIT_CLIENT_ID != "votre_client_id":
        try:
            scraper.scrape_subreddit("AskDocs", "second opinion", 10, db)
        except Exception as e:
            logger.error(f"Erreur lors du scraping initial: {e}")

    # Lancement du serveur
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

@pytest.fixture
def db_manager():
    """Fixture pour le gestionnaire de base de données"""
    db_path = "test_phase1_data.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    manager = DatabaseManager(db_path)
    yield manager
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def data_collector(db_manager):
    """Fixture pour le collecteur de données"""
    return DataCollector(db_manager)

@pytest.fixture
def data_analyzer(db_manager):
    """Fixture pour l'analyseur de données"""
    return DataAnalyzer(db_manager)

def test_data_collection(db_manager, data_collector):
    """Test la collecte de données"""
    # Simuler des données de test
    test_post = {
        "id": 1,
        "author": "test_user",
        "category": "Urgent",
        "overall_score": 0.8,
        "created_utc": datetime.now().timestamp()
    }
    
    test_user = {
        "post_id": 1,
        "country": "UAE",
        "city": "Dubai"
    }
    
    # Collecter les données
    data_collector.collect_post(test_post)
    data_collector.collect_user(test_user)
    
    # Vérifier que les données ont été sauvegardées
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts WHERE id = ?", (1,))
        post = cursor.fetchone()
        assert post is not None
        assert post[1] == "test_user"
        assert post[2] == "Urgent"
        assert post[3] == 0.8
        
        cursor.execute("SELECT * FROM gcc_users WHERE post_id = ?", (1,))
        user = cursor.fetchone()
        assert user is not None
        assert user[1] == "UAE"
        assert user[2] == "Dubai"

def test_data_analysis(db_manager, data_analyzer):
    """Test l'analyse des données"""
    # Insérer des données de test
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO posts (id, author, category, overall_score, created_utc)
        VALUES (1, 'user1', 'Urgent', 0.8, ?),
               (2, 'user2', 'Non-Urgent', 0.3, ?)
        """, (datetime.now().timestamp(), datetime.now().timestamp()))
        
        cursor.execute("""
        INSERT INTO gcc_users (post_id, country, city)
        VALUES (1, 'UAE', 'Dubai'),
               (2, 'KSA', 'Riyadh')
        """)
        conn.commit()
    
    # Analyser les données
    analysis = data_analyzer.analyze_data()
    
    # Vérifier les résultats de l'analyse
    assert "total_posts" in analysis
    assert analysis["total_posts"] == 2
    
    assert "urgent_posts" in analysis
    assert analysis["urgent_posts"] == 1
    
    assert "country_distribution" in analysis
    assert analysis["country_distribution"] == {"UAE": 1, "KSA": 1}
    
    assert "average_score" in analysis
    assert 0.5 <= analysis["average_score"] <= 0.6

def test_data_validation(db_manager, data_collector):
    """Test la validation des données"""
    # Test avec des données invalides
    invalid_post = {
        "id": 1,
        "author": "",  # Auteur vide
        "category": "Invalid",  # Catégorie invalide
        "overall_score": 1.5,  # Score hors limites
        "created_utc": datetime.now().timestamp()
    }

    # Vérifier que la validation lève une ValueError
    with pytest.raises(ValueError):
        db_manager._validate_post_data(invalid_post)

def test_data_aggregation(db_manager, data_analyzer):
    """Test l'agrégation des données"""
    # Insérer des données de test avec différents scores
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        for i in range(5):
            cursor.execute("""
            INSERT INTO posts (id, author, category, overall_score, created_utc)
            VALUES (?, ?, ?, ?, ?)
            """, (i, f"user{i}", "Urgent", 0.8, datetime.now().timestamp()))
        conn.commit()
    
    # Analyser les agrégations
    analysis = data_analyzer.analyze_data()
    
    # Vérifier les statistiques
    assert analysis["total_posts"] == 5
    assert analysis["urgent_posts"] == 5
    assert analysis["average_score"] == 0.8
    assert "score_distribution" in analysis
    assert len(analysis["score_distribution"]) > 0