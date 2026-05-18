"""
Module de stockage SQLite pour les données collectées.
"""

import os
import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLiteStorage:
    """Gestion du stockage des données dans SQLite."""
    
    def __init__(self, db_path: str):
        """
        Initialise la connexion à la base de données.
        
        Args:
            db_path: Chemin vers le fichier de base de données SQLite
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
        
    async def initialize(self):
        """
        Méthode d'initialisation asynchrone pour compatibilité avec l'interface BaseScraper.
        Cette méthode est appelée au démarrage du scraper.
        """
        logger.info(f"Initialisation du stockage SQLite: {self.db_path}")
        # L'initialisation est déjà faite dans __init__, donc cette méthode est juste pour la compatibilité
        return True
        
    async def close(self) -> None:
        """Ferme proprement les connexions à la base de données."""
        logger.info("Fermeture du stockage SQLite")
        # Pas de connexion persistante à fermer dans cette implémentation
        return
        
    def _ensure_db_directory(self):
        """Crée le répertoire de la base de données s'il n'existe pas."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_connection(self):
        """
        Obtient une connexion à la base de données.
        
        Returns:
            sqlite3.Connection: Connexion à la base de données
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _dict_factory(self, cursor, row):
        """
        Convertit une ligne de résultat en dictionnaire.
        
        Args:
            cursor: Curseur SQLite
            row: Ligne de résultat
            
        Returns:
            Dict: Dictionnaire contenant les données de la ligne
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
        
    def _init_database(self):
        """Initialise la structure de la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des posts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    author TEXT,
                    subreddit TEXT,
                    score INTEGER,
                    created_utc INTEGER,
                    num_comments INTEGER,
                    url TEXT,
                    collected_at INTEGER,
                    processed BOOLEAN DEFAULT FALSE,
                    relevance_score REAL DEFAULT 0.0
                )
            """)
            
            # Table des commentaires
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY,
                    post_id TEXT,
                    content TEXT,
                    author TEXT,
                    score INTEGER,
                    created_utc INTEGER,
                    collected_at INTEGER,
                    processed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (post_id) REFERENCES posts (id)
                )
            """)
            
            # Index pour optimiser les recherches
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_utc)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_score ON posts(score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)")
            
            conn.commit()
            
    def save_post(self, post_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde un post dans la base de données.
        
        Args:
            post_data: Dictionnaire contenant les données du post
            
        Returns:
            bool: True si sauvegarde réussie, False sinon
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO posts (
                        id, title, content, author, subreddit,
                        score, created_utc, num_comments, url, collected_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post_data['id'],
                    post_data['title'],
                    post_data['content'],
                    post_data['author'],
                    post_data['subreddit'],
                    post_data['score'],
                    post_data['created_utc'],
                    post_data['num_comments'],
                    post_data['url'],
                    post_data['collected_at']
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du post {post_data['id']}: {str(e)}")
            return False
            
    def save_comment(self, comment_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde un commentaire dans la base de données.
        
        Args:
            comment_data: Dictionnaire contenant les données du commentaire
            
        Returns:
            bool: True si sauvegarde réussie, False sinon
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO comments (
                        id, post_id, content, author,
                        score, created_utc, collected_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    comment_data['id'],
                    comment_data['post_id'],
                    comment_data['content'],
                    comment_data['author'],
                    comment_data['score'],
                    comment_data['created_utc'],
                    comment_data['collected_at']
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du commentaire {comment_data['id']}: {str(e)}")
            return False
            
    def get_unprocessed_posts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les posts non traités.
        
        Args:
            limit: Nombre maximum de posts à récupérer
            
        Returns:
            Liste de posts non traités
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM posts
                    WHERE processed = FALSE
                    ORDER BY created_utc DESC
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des posts non traités: {str(e)}")
            return []
            
    def mark_post_as_processed(self, post_id: str, relevance_score: float = 0.0) -> bool:
        """
        Marque un post comme traité.
        
        Args:
            post_id: ID du post
            relevance_score: Score de pertinence calculé
            
        Returns:
            bool: True si mise à jour réussie, False sinon
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE posts
                    SET processed = TRUE, relevance_score = ?
                    WHERE id = ?
                """, (relevance_score, post_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erreur lors du marquage du post {post_id}: {str(e)}")
            return False
            
    def get_post_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """
        Récupère tous les commentaires d'un post.
        
        Args:
            post_id: ID du post
            
        Returns:
            Liste des commentaires du post
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM comments
                    WHERE post_id = ?
                    ORDER BY score DESC
                """, (post_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des commentaires du post {post_id}: {str(e)}")
            return []
    
    def get_data(self, id: str) -> Optional[Dict]:
        """Récupère un post par son ID."""
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM posts WHERE id = ?", (id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "title": row[1],
                        "content": row[2],
                        "url": row[3],
                        "score": row[4],
                        "created_at": datetime.fromisoformat(row[5]),
                        "updated_at": datetime.fromisoformat(row[6]),
                        "metadata": json.loads(row[7])
                    }
                return None
        except Exception as e:
            print(f"Erreur lors de la récupération SQLite: {str(e)}")
            return None
    
    def update_data(self, id: str, data: Dict) -> bool:
        """Met à jour un post existant."""
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                
                # Mise à jour des champs spécifiés
                set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
                values = list(data.values())
                values.append(id)
                
                cursor.execute(f"""
                    UPDATE posts 
                    SET {set_clause}
                    WHERE id = ?
                """, values)
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur lors de la mise à jour SQLite: {str(e)}")
            return False
    
    def delete_data(self, id: str) -> bool:
        """Supprime un post par son ID."""
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM posts WHERE id = ?", (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur lors de la suppression SQLite: {str(e)}")
            return False
    
    async def save_medical_article(self, article_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde un article médical dans la base de données.
        
        Args:
            article_data: Dictionnaire contenant les données de l'article
            
        Returns:
            bool: True si sauvegarde réussie, False sinon
        """
        try:
            # Conversion en format JSON pour stockage
            article_json = json.dumps(article_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Vérifier si la table existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS medical_articles (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        url TEXT UNIQUE,
                        content TEXT,
                        source TEXT,
                        category TEXT,
                        date TEXT,
                        author TEXT,
                        collected_at TEXT,
                        data_json TEXT
                    )
                """)
                
                # Insertion des données
                cursor.execute("""
                    INSERT OR REPLACE INTO medical_articles (
                        id, title, url, content, source, category, date, author, collected_at, data_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_data.get('id', article_data.get('url', '')),
                    article_data.get('title', ''),
                    article_data.get('url', ''),
                    article_data.get('content', ''),
                    article_data.get('source', ''),
                    article_data.get('category', ''),
                    article_data.get('date', ''),
                    article_data.get('author', ''),
                    article_data.get('collected_at', datetime.now().isoformat()),
                    article_json
                ))
                conn.commit()
                logger.info(f"Article médical sauvegardé: {article_data.get('title')}")
                return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'article médical: {str(e)}")
            return False
            
    async def save_reddit_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Sauvegarde les données Reddit dans la base de données.
        
        Args:
            data: Liste de dictionnaires contenant les données Reddit
            
        Returns:
            bool: True si sauvegarde réussie, False sinon
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Vérifier si la table existe, sinon la créer
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reddit_data (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        title TEXT,
                        content TEXT,
                        author TEXT,
                        subreddit TEXT,
                        url TEXT,
                        permalink TEXT,
                        score INTEGER,
                        created_utc TEXT,
                        num_comments INTEGER,
                        post_id TEXT,
                        parent_id TEXT,
                        is_submitter BOOLEAN,
                        collected_at TEXT,
                        data_json TEXT
                    )
                """)
                
                # Créer des index pour optimiser les recherches
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_type ON reddit_data(type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_subreddit ON reddit_data(subreddit)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_post_id ON reddit_data(post_id)")
                
                # Insertion des données
                for item in data:
                    # Conversion en format JSON pour stockage complet
                    item_json = json.dumps(item)
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO reddit_data (
                            id, type, title, content, author, subreddit, url, permalink, 
                            score, created_utc, num_comments, post_id, parent_id, 
                            is_submitter, collected_at, data_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item.get('id', ''),
                        item.get('type', ''),
                        item.get('title', ''),
                        item.get('content', ''),
                        item.get('author', ''),
                        item.get('subreddit', ''),
                        item.get('url', ''),
                        item.get('permalink', ''),
                        item.get('score', 0),
                        item.get('created_utc', ''),
                        item.get('num_comments', 0),
                        item.get('post_id', ''),
                        item.get('parent_id', ''),
                        item.get('is_submitter', False),
                        item.get('collected_at', datetime.now().isoformat()),
                        item_json
                    ))
                
                conn.commit()
                logger.info(f"Données Reddit sauvegardées: {len(data)} éléments")
                return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données Reddit: {str(e)}")
            return False
    
    def get_all_posts(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les posts Reddit de la base de données.
        
        Returns:
            Liste de dictionnaires contenant les données des posts
        """
        try:
            conn = self._get_connection()
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM reddit_data
                ORDER BY created_utc DESC
            """)
            
            posts = cursor.fetchall()
            conn.close()
            
            # Convertir les champs JSON
            for post in posts:
                if 'metadata' in post and post['metadata']:
                    try:
                        post['metadata'] = json.loads(post['metadata'])
                    except json.JSONDecodeError:
                        post['metadata'] = {}
            
            return posts
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des posts Reddit: {e}")
            return []
            
    def get_all_articles(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les articles médicaux de la base de données.
        
        Returns:
            Liste de dictionnaires contenant les données des articles
        """
        try:
            conn = self._get_connection()
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            
            # Vérifier les colonnes disponibles dans la table
            cursor.execute("PRAGMA table_info(medical_articles)")
            columns = [col['name'] for col in cursor.fetchall()]
            
            # Adapter la requête en fonction des colonnes disponibles
            if 'published_date' in columns:
                order_by = "published_date"
            elif 'date' in columns:
                order_by = "date"
            elif 'created_at' in columns:
                order_by = "created_at"
            else:
                order_by = "id"  # Fallback sur l'ID
            
            cursor.execute(f"""
                SELECT * FROM medical_articles
                ORDER BY {order_by} DESC
            """)
            
            articles = cursor.fetchall()
            conn.close()
            
            # Convertir les champs JSON
            for article in articles:
                if 'metadata' in article and article['metadata']:
                    try:
                        article['metadata'] = json.loads(article['metadata'])
                    except json.JSONDecodeError:
                        article['metadata'] = {}
                        
                if 'tags' in article and article['tags']:
                    try:
                        article['tags'] = json.loads(article['tags'])
                    except json.JSONDecodeError:
                        article['tags'] = []
            
            return articles
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des articles médicaux: {e}")
            return [] 