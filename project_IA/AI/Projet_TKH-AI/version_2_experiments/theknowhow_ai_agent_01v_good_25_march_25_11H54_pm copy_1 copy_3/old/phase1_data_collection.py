"""Module de collecte et d'analyse des données."""

import os
import logging
import praw
import sqlite3
import spacy
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime


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


class DatabaseManager:
    """Gestionnaire de base de données pour la phase 1."""
    
    def __init__(self, db_path: str):
        """Initialise le gestionnaire de base de données.
        
        Args:
            db_path (str): Chemin vers le fichier de base de données
        """
        self.db_path = db_path
        self._create_tables()
    
    def get_connection(self):
        """Obtient une connexion à la base de données.
        
        Returns:
            sqlite3.Connection: Connexion à la base de données
        """
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Crée les tables de la base de données"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL,
                overall_score REAL NOT NULL CHECK (overall_score >= 0 AND overall_score <= 1),
                created_utc REAL NOT NULL
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS gcc_users (
                post_id INTEGER PRIMARY KEY,
                country TEXT NOT NULL,
                city TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
            """)
            conn.commit()
    
    def _validate_post_data(self, post_data):
        """Valide les données d'un post"""
        if not isinstance(post_data, dict):
            raise ValueError("Les données du post doivent être un dictionnaire")
        
        required_fields = ["id", "title", "author", "category", "overall_score", "created_utc"]
        for field in required_fields:
            if field not in post_data:
                raise ValueError(f"Le champ {field} est requis")
        
        if not post_data["title"]:
            raise ValueError("Le titre ne peut pas être vide")
            
        if not post_data["author"]:
            raise ValueError("L'auteur ne peut pas être vide")
        
        if post_data["category"] not in ["Urgent", "Non-Urgent"]:
            raise ValueError("La catégorie doit être 'Urgent' ou 'Non-Urgent'")
        
        if not isinstance(post_data["overall_score"], (int, float)) or not 0 <= post_data["overall_score"] <= 1:
            raise ValueError("Le score doit être un nombre entre 0 et 1")
    
    def insert_post(self, post_data: Dict[str, Any]) -> bool:
        """Insère un nouveau post dans la base de données.
        
        Args:
            post_data (Dict[str, Any]): Données du post à insérer
            
        Returns:
            bool: True si l'insertion a réussi, False sinon
        """
        try:
            self._validate_post_data(post_data)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO posts (id, title, author, category, overall_score, created_utc) VALUES (?, ?, ?, ?, ?, ?)",
                    (post_data["id"], post_data["title"], post_data["author"], post_data["category"], 
                     post_data["overall_score"], post_data["created_utc"])
                )
                conn.commit()
                return True
        except (sqlite3.Error, ValueError) as e:
            logger.error(f"Erreur lors de l'insertion du post: {e}")
            return False
    
    def _validate_user_data(self, user_data):
        """Valide les données d'un utilisateur"""
        if not isinstance(user_data, dict):
            raise ValueError("Les données de l'utilisateur doivent être un dictionnaire")
        
        required_fields = ["post_id", "country", "city"]
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Le champ {field} est requis")
        
        if not user_data["country"] or not user_data["city"]:
            raise ValueError("Le pays et la ville ne peuvent pas être vides")
    
    def insert_user(self, user_data: Dict[str, Any]) -> bool:
        """Insère les données d'un utilisateur dans la base de données.
        
        Args:
            user_data (Dict[str, Any]): Données de l'utilisateur à insérer
            
        Returns:
            bool: True si l'insertion a réussi, False sinon
        """
        try:
            self._validate_user_data(user_data)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO gcc_users (post_id, country, city) VALUES (?, ?, ?)",
                    (user_data["post_id"], user_data["country"], user_data["city"])
                )
                conn.commit()
                return True
        except (sqlite3.Error, ValueError) as e:
            logger.error(f"Erreur lors de l'insertion de l'utilisateur: {e}")
            return False
    
    def get_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les posts les plus récents.
        
        Args:
            limit (int): Nombre maximum de posts à récupérer
            
        Returns:
            List[Dict[str, Any]]: Liste des posts
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM posts ORDER BY created_utc DESC LIMIT ?",
                    (limit,)
                )
                posts = cursor.fetchall()
                return [
                    {
                        "id": p[0],
                        "author": p[1],
                        "category": p[2],
                        "overall_score": p[3],
                        "created_utc": p[4]
                    }
                    for p in posts
                ]
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des posts: {e}")
            return []

    def analyze_data(self):
        """Analyse les données collectées"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Statistiques générales
            cursor.execute("""
            SELECT 
                COUNT(*) as total_posts,
                AVG(overall_score) as avg_score,
                COUNT(CASE WHEN category = 'Urgent' THEN 1 END) as urgent_count,
                COUNT(CASE WHEN category = 'Non-Urgent' THEN 1 END) as non_urgent_count
            FROM posts
            """)
            stats = cursor.fetchone()
            
            # Distribution par pays
            cursor.execute("""
            SELECT country, COUNT(*) as count
            FROM gcc_users
            GROUP BY country
            """)
            country_distribution = cursor.fetchall()
            
            # Distribution par ville
            cursor.execute("""
            SELECT city, COUNT(*) as count
            FROM gcc_users
            GROUP BY city
            """)
            city_distribution = cursor.fetchall()
            
            # Distribution des scores
            cursor.execute("""
            SELECT 
                CASE 
                    WHEN overall_score >= 0.8 THEN 'High'
                    WHEN overall_score >= 0.5 THEN 'Medium'
                    ELSE 'Low'
                END as score_range,
                COUNT(*) as count
            FROM posts
            GROUP BY score_range
            """)
            score_distribution = cursor.fetchall()
            
            return {
                "total_posts": stats[0],
                "average_score": stats[1],
                "urgent_posts": stats[2],
                "non_urgent_posts": stats[3],
                "category_distribution": {
                    "Urgent": stats[2],
                    "Non-Urgent": stats[3]
                },
                "country_distribution": dict(country_distribution),
                "city_distribution": dict(city_distribution),
                "score_distribution": dict(score_distribution)
            }


class DataCollector:
    """Collecteur de données pour la phase 1."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialise le collecteur de données.
        
        Args:
            db_manager (DatabaseManager): Instance du gestionnaire de base de données
        """
        self.db_manager = db_manager
    
    def collect_post(self, post_data: Dict[str, Any]) -> bool:
        """Collecte et sauvegarde les données d'un post.
        
        Args:
            post_data (Dict[str, Any]): Données du post à collecter
            
        Returns:
            bool: True si la collecte a réussi, False sinon
        """
        return self.db_manager.insert_post(post_data)
    
    def collect_user(self, user_data: Dict[str, Any]) -> bool:
        """Collecte et sauvegarde les données d'un utilisateur.
        
        Args:
            user_data (Dict[str, Any]): Données de l'utilisateur à collecter
            
        Returns:
            bool: True si la collecte a réussi, False sinon
        """
        return self.db_manager.insert_user(user_data)


class DataAnalyzer:
    """Analyseur de données pour la phase 1."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialise l'analyseur de données.
        
        Args:
            db_manager (DatabaseManager): Instance du gestionnaire de base de données
        """
        self.db_manager = db_manager
    
    def analyze_posts(self, limit: int = 10) -> Dict[str, Any]:
        """Analyse les posts récents.
        
        Args:
            limit (int): Nombre maximum de posts à analyser
            
        Returns:
            Dict[str, Any]: Résultats de l'analyse
        """
        posts = self.db_manager.get_posts(limit)
        
        if not posts:
            return {
                "total_posts": 0,
                "average_score": 0.0,
                "categories": {}
            }
        
        # Calcul des statistiques
        total_posts = len(posts)
        average_score = sum(p["overall_score"] for p in posts) / total_posts
        
        # Distribution par catégorie
        categories = {}
        for post in posts:
            category = post["category"]
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_posts": total_posts,
            "average_score": average_score,
            "categories": categories
        }

    def analyze_data(self):
        """Analyse les données collectées"""
        return self.db_manager.analyze_data()


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

    def scrape_subreddit(self, subreddit: str, query: str, limit: int = 10, db: DatabaseManager = None):
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
db_manager = DatabaseManager("phase1_data.db")
scraper = RedditScraper()


def get_db():
    return db_manager


@app.get("/", tags=["Général"])
def read_root():
    return {"message": "Bienvenue sur l'API Reddit Scraper!"}


@app.get("/posts", response_model=List[Dict[str, Any]], tags=["Posts"])
def get_posts(db: DatabaseManager = Depends(get_db), limit: int = 10):
    posts = db.get_posts(limit)
    if not posts:
        logger.warning("Aucun post trouvé dans la base de données")
        return []
    return posts


@app.post("/scrape", tags=["Scraping"])
def scrape_endpoint(subreddit: str, query: str, limit: int = 10, db: DatabaseManager = Depends(get_db)):
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
            scraper.scrape_subreddit("AskDocs", "second opinion", 10, db_manager)
        except Exception as e:
            logger.error(f"Erreur lors du scraping initial: {e}")

    # Lancement du serveur
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)