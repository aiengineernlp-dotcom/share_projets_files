"""
Implémentation du stockage avec PostgreSQL.
"""

import psycopg2
from psycopg2.extras import execute_batch, DictCursor
from datetime import datetime
from typing import List, Dict, Any
from .base_storage import BaseStorage

class PostgresStorage(BaseStorage):
    """Stockage des données dans PostgreSQL."""
    
    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost", port: str = "5432"):
        """
        Initialise le stockage PostgreSQL.
        
        Args:
            dbname: Nom de la base de données
            user: Nom d'utilisateur
            password: Mot de passe
            host: Hôte (défaut: localhost)
            port: Port (défaut: 5432)
        """
        self.conn_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self._init_database()
    
    def _get_connection(self):
        """Crée une nouvelle connexion."""
        return psycopg2.connect(**self.conn_params)
    
    def _init_database(self) -> None:
        """Crée les tables et index nécessaires."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Table principale pour les posts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            
            # Table pour les métadonnées (structure JSONB pour plus de flexibilité)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                post_id TEXT REFERENCES posts(id) ON DELETE CASCADE,
                data JSONB,
                PRIMARY KEY (post_id)
            )""")
            
            # Index pour la recherche full-text
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_title_content ON posts 
            USING gin(to_tsvector('english', title || ' ' || content))
            """)
            
            # Index sur le score
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_score ON posts(score)
            """)
            
            # Trigger pour mettre à jour updated_at
            cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'""")
            
            cursor.execute("""
            DROP TRIGGER IF EXISTS update_posts_updated_at ON posts;
            CREATE TRIGGER update_posts_updated_at
                BEFORE UPDATE ON posts
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
            """)
            
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
    
    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Sauvegarde les données dans PostgreSQL."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Préparation des données pour l'insertion en batch
            posts_data = [
                (item["id"], item["title"], item["content"], item.get("score", 0))
                for item in data
            ]
            
            # Insertion des posts en batch
            execute_batch(cursor, """
                INSERT INTO posts (id, title, content, score)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    score = EXCLUDED.score,
                    updated_at = CURRENT_TIMESTAMP
            """, posts_data)
            
            # Insertion des métadonnées
            metadata_data = [
                (item["id"], psycopg2.extras.Json(item.get("metadata", {})))
                for item in data if "metadata" in item
            ]
            
            if metadata_data:
                execute_batch(cursor, """
                    INSERT INTO metadata (post_id, data)
                    VALUES (%s, %s)
                    ON CONFLICT (post_id) DO UPDATE SET
                        data = EXCLUDED.data
                """, metadata_data)
            
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
    
    def get_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Récupère les données avec les filtres spécifiés."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        try:
            query = """
                SELECT p.*, m.data as metadata
                FROM posts p
                LEFT JOIN metadata m ON p.id = m.post_id
            """
            params = []
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(f"p.{key} = %s")
                    params.append(value)
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, params)
            results = []
            
            for row in cursor:
                post = dict(row)
                # Conversion des timestamps en str pour la sérialisation JSON
                post["created_at"] = post["created_at"].isoformat()
                post["updated_at"] = post["updated_at"].isoformat()
                results.append(post)
            
            return results
            
        finally:
            cursor.close()
            conn.close()
    
    def update_data(self, id: str, data: Dict[str, Any]) -> None:
        """Met à jour les données existantes."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Séparation des données de base et des métadonnées
            base_data = {k: v for k, v in data.items() if k != "metadata"}
            metadata = data.get("metadata")
            
            if base_data:
                # Construction de la requête de mise à jour
                set_parts = [f"{key} = %s" for key in base_data.keys()]
                query = f"""
                    UPDATE posts SET {", ".join(set_parts)}
                    WHERE id = %s
                """
                values = list(base_data.values()) + [id]
                cursor.execute(query, values)
            
            if metadata is not None:
                cursor.execute("""
                    INSERT INTO metadata (post_id, data)
                    VALUES (%s, %s)
                    ON CONFLICT (post_id) DO UPDATE SET
                        data = EXCLUDED.data
                """, (id, psycopg2.extras.Json(metadata)))
            
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, id: str) -> None:
        """Supprime une entrée et ses métadonnées."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # La suppression des métadonnées est automatique grâce à ON DELETE CASCADE
            cursor.execute("DELETE FROM posts WHERE id = %s", (id,))
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
    
    def close(self) -> None:
        """Pas de connexion persistante à fermer."""
        pass
    
    # Méthodes spécifiques à PostgreSQL
    
    def full_text_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Effectue une recherche full-text.
        
        Args:
            query: Texte à rechercher
            
        Returns:
            Liste des posts correspondants
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        try:
            cursor.execute("""
                SELECT p.*, m.data as metadata,
                       ts_rank(to_tsvector('english', p.title || ' ' || p.content),
                              plainto_tsquery('english', %s)) as rank
                FROM posts p
                LEFT JOIN metadata m ON p.id = m.post_id
                WHERE to_tsvector('english', p.title || ' ' || p.content) @@ 
                      plainto_tsquery('english', %s)
                ORDER BY rank DESC
            """, (query, query))
            
            results = []
            for row in cursor:
                post = dict(row)
                post["created_at"] = post["created_at"].isoformat()
                post["updated_at"] = post["updated_at"].isoformat()
                results.append(post)
            
            return results
            
        finally:
            cursor.close()
            conn.close() 