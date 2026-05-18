import sqlite3
from typing import Dict, Any, List
import os
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "phase2_data.db")

def init_db():
    """Initialise la base de données avec les tables nécessaires."""
    try:
        # Créer le répertoire data s'il n'existe pas
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Table des posts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                title TEXT,
                body TEXT,
                url TEXT,
                created_utc REAL,
                subreddit TEXT,
                author TEXT,
                category TEXT,
                second_opinion_score REAL,
                urgency_score REAL,
                medical_relevance_score REAL,
                sentiment_score REAL,
                overall_score REAL,
                country TEXT,
                city TEXT,
                region TEXT,
                latitude REAL,
                longitude REAL
            )
            """)

            # Table pour les utilisateurs du GCC
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS gcc_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT,
                country TEXT,
                city TEXT,
                region TEXT,
                latitude REAL,
                longitude REAL,
                created_at REAL,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
            """)

            # Table pour les réponses
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT,
                response_text TEXT, 
                sent_time REAL,
                response_status TEXT,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
            """)

            conn.commit()
            logger.info("Base de données initialisée avec succès")
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise

def save_post(post_data: Dict[str, Any]) -> bool:
    """Sauvegarde un post dans la base de données."""
    try:
        # Créer le répertoire data s'il n'existe pas
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Vérifier que tous les champs requis sont présents
            required_fields = [
                "id", "title", "body", "url", "created_utc", "subreddit", "author",
                "category", "second_opinion_score", "urgency_score", "medical_relevance_score",
                "sentiment_score", "overall_score", "country", "city", "region",
                "latitude", "longitude"
            ]
            
            missing_fields = [field for field in required_fields if field not in post_data]
            if missing_fields:
                logger.error(f"Champs manquants dans les données du post: {missing_fields}")
                return False
            
            cursor.execute("""
            INSERT OR IGNORE INTO posts 
            (id, title, body, url, created_utc, subreddit, author, category, 
            second_opinion_score, urgency_score, medical_relevance_score, 
            sentiment_score, overall_score, country, city, region, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_data["id"],
                post_data["title"],
                post_data["body"],
                post_data["url"],
                post_data["created_utc"],
                post_data["subreddit"],
                post_data["author"],
                post_data["category"],
                post_data["second_opinion_score"],
                post_data["urgency_score"],
                post_data["medical_relevance_score"],
                post_data["sentiment_score"],
                post_data["overall_score"],
                post_data["country"],
                post_data["city"],
                post_data["region"],
                post_data["latitude"],
                post_data["longitude"]
            ))
            
            if cursor.rowcount > 0:
                logger.info(f"Post sauvegardé avec succès: {post_data['id']}")
                return True
            else:
                logger.warning(f"Post ignoré (déjà existant): {post_data['id']}")
                return False
                
    except sqlite3.Error as e:
        logger.error(f"Erreur SQLite lors de la sauvegarde du post {post_data.get('id', 'unknown')}: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la sauvegarde du post {post_data.get('id', 'unknown')}: {e}")
        return False

def get_posts(limit: int = 50, min_score: float = 0.0, category: str = None) -> List[Dict[str, Any]]:
    """Récupère les posts de la base de données avec des filtres optionnels."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            query = """
            SELECT * FROM posts 
            WHERE overall_score >= ?
            """
            params = [min_score]
            
            if category:
                query += " AND category = ?"
                params.append(category)
                
            query += " ORDER BY overall_score DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération des posts: {e}")
        return []

def get_stats() -> Dict[str, Any]:
    """Récupère les statistiques de la base de données."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Nombre total de posts
            cursor.execute("SELECT COUNT(*) FROM posts")
            total_posts = cursor.fetchone()[0]
            
            # Score moyen
            cursor.execute("SELECT AVG(overall_score) FROM posts")
            avg_score = cursor.fetchone()[0] or 0.0
            
            # Répartition par catégorie
            cursor.execute("""
            SELECT category, COUNT(*) 
            FROM posts 
            GROUP BY category
            """)
            categories = dict(cursor.fetchall())
            
            # Répartition par niveau d'urgence
            cursor.execute("""
            SELECT 
                CASE 
                    WHEN urgency_score >= 0.7 THEN 'Très Urgent'
                    WHEN urgency_score >= 0.4 THEN 'Urgent'
                    ELSE 'Normal'
                END as urgency_level,
                COUNT(*) as count
            FROM posts 
            GROUP BY urgency_level
            """)
            urgency_levels = dict(cursor.fetchall())
            
            return {
                "total_posts": total_posts,
                "avg_score": avg_score,
                "categories": categories,
                "urgency_levels": urgency_levels
            }
            
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return {
            "total_posts": 0,
            "avg_score": 0.0,
            "categories": {},
            "urgency_levels": {}
        } 