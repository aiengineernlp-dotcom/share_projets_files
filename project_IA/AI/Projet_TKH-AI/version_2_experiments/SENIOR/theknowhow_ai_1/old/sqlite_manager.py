"""Module de gestion de la base de données pour la phase 1."""

import sqlite3
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestionnaire de base de données pour la phase 1."""
    
    def __init__(self, db_path: str):
        """Initialise le gestionnaire de base de données.
        
        Args:
            db_path (str): Chemin versm le fichier de base de données
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_db()
    
    def _init_db(self):
        """Initialise la base de données avec les tables et index nécessaires."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des posts
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS posts (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        text TEXT,
                        created_utc TIMESTAMP NOT NULL,
                        score INTEGER NOT NULL,
                        num_comments INTEGER NOT NULL,
                        url TEXT,
                        subreddit TEXT NOT NULL,
                        query TEXT NOT NULL,
                        urgency TEXT NOT NULL,
                        relevance_score REAL NOT NULL,
                        collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Index pour optimiser les requêtes fréquentes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_subreddit ON posts(subreddit)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_query ON posts(query)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_utc ON posts(created_utc)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_urgency ON posts(urgency)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_relevance ON posts(relevance_score)')
                
                # Table des statistiques
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS collection_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        subreddit TEXT NOT NULL,
                        query TEXT NOT NULL,
                        posts_count INTEGER NOT NULL,
                        avg_score REAL NOT NULL,
                        collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                self.logger.info("Base de données initialisée avec succès")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
            raise
    
    def get_connection(self):
        """Obtient une connexion à la base de données."""
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Crée les tables de la base de données."""
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
    
    def insert_post(self, post_data: Dict[str, Any]) -> bool:
        """Insère un nouveau post dans la base de données."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO posts (id, title, author, category, overall_score, created_utc) VALUES (?, ?, ?, ?, ?, ?)",
                    (post_data["id"], post_data["title"], post_data["author"], post_data["category"], 
                     post_data["overall_score"], post_data["created_utc"])
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'insertion du post: {e}")
            return False
    
    def insert_user(self, user_data: Dict[str, Any]) -> bool:
        """Insère les données d'un utilisateur dans la base de données."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO gcc_users (post_id, country, city) VALUES (?, ?, ?)",
                    (user_data["post_id"], user_data["country"], user_data["city"])
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'insertion de l'utilisateur: {e}")
            return False
    
    def get_posts(self, subreddit: str = None, query: str = None, limit: int = None,
                  min_score: float = None, urgency: str = None) -> List[Dict]:
        """Récupère les posts de la base de données avec des filtres optionnels."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query_sql = "SELECT * FROM posts WHERE 1=1"
                params = []
                
                if subreddit:
                    query_sql += " AND subreddit = ?"
                    params.append(subreddit)
                    
                if query:
                    query_sql += " AND query = ?"
                    params.append(query)
                
                if min_score is not None:
                    query_sql += " AND relevance_score >= ?"
                    params.append(min_score)
                
                if urgency:
                    query_sql += " AND urgency = ?"
                    params.append(urgency)
                
                query_sql += " ORDER BY relevance_score DESC, created_utc DESC"
                    
                if limit:
                    query_sql += " LIMIT ?"
                    params.append(limit)
                
                cursor.execute(query_sql, params)
                
                posts = []
                for row in cursor.fetchall():
                    posts.append({
                        'id': row[0],
                        'title': row[1],
                        'text': row[2],
                        'created_utc': row[3],
                        'score': row[4],
                        'num_comments': row[5],
                        'url': row[6],
                        'subreddit': row[7],
                        'query': row[8],
                        'urgency': row[9],
                        'relevance_score': row[10],
                        'collected_at': row[11]
                    })
                
                return posts
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des posts: {str(e)}")
            return []

    def save_posts(self, posts: List[Dict], subreddit: str, query: str):
        """Sauvegarde une liste de posts dans la base de données."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Préparation des données pour insertion en masse
                posts_data = []
                total_score = 0
                
                for post in posts:
                    posts_data.append((
                        post['id'],
                        post['title'],
                        post['text'],
                        post['created_utc'],
                        post['score'],
                        post['num_comments'],
                        post['url'],
                        subreddit,
                        query,
                        post.get('urgency', 'Normal'),
                        post.get('relevance_score', 0.0)
                    ))
                    total_score += post.get('relevance_score', 0.0)
                
                # Insertion des posts
                cursor.executemany('''
                    INSERT OR REPLACE INTO posts 
                    (id, title, text, created_utc, score, num_comments, url, 
                     subreddit, query, urgency, relevance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', posts_data)
                
                # Mise à jour des statistiques
                avg_score = total_score / len(posts) if posts else 0
                cursor.execute('''
                    INSERT INTO collection_stats 
                    (subreddit, query, posts_count, avg_score)
                    VALUES (?, ?, ?, ?)
                ''', (subreddit, query, len(posts), avg_score))
                
                conn.commit()
                self.logger.info(f"Sauvegardé {len(posts)} posts de r/{subreddit}")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des posts: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques de collecte."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {
                    'total_posts': 0,
                    'by_subreddit': {},
                    'by_urgency': {},
                    'avg_score': 0.0,
                    'recent_collections': []
                }
                
                # Total des posts et moyenne des scores
                cursor.execute('''
                    SELECT COUNT(*), AVG(relevance_score)
                    FROM posts
                ''')
                total, avg_score = cursor.fetchone()
                stats['total_posts'] = total
                stats['avg_score'] = avg_score or 0.0
                
                # Stats par subreddit
                cursor.execute('''
                    SELECT subreddit, COUNT(*), AVG(relevance_score)
                    FROM posts
                    GROUP BY subreddit
                ''')
                for row in cursor.fetchall():
                    stats['by_subreddit'][row[0]] = {
                        'count': row[1],
                        'avg_score': row[2]
                    }
                
                # Stats par niveau d'urgence
                cursor.execute('''
                    SELECT urgency, COUNT(*)
                    FROM posts
                    GROUP BY urgency
                ''')
                for row in cursor.fetchall():
                    stats['by_urgency'][row[0]] = row[1]
                
                # Collections récentes
                cursor.execute('''
                    SELECT *
                    FROM collection_stats
                    ORDER BY collection_date DESC
                    LIMIT 10
                ''')
                for row in cursor.fetchall():
                    stats['recent_collections'].append({
                        'subreddit': row[1],
                        'query': row[2],
                        'posts_count': row[3],
                        'avg_score': row[4],
                        'date': row[5]
                    })
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
            return {} 