"""
Implémentation du stockage avec MySQL.
"""

import json
from typing import List, Dict, Any
from datetime import datetime
import mysql.connector
from mysql.connector import pooling
from .base_storage import BaseStorage

class MySQLStorage(BaseStorage):
    """Stockage des données dans MySQL avec pool de connexions."""
    
    def __init__(self, database: str, user: str, password: str, host: str = "localhost",
                 port: int = 3306, pool_name: str = "mypool", pool_size: int = 5):
        """
        Initialise le stockage MySQL.
        
        Args:
            database: Nom de la base de données
            user: Nom d'utilisateur
            password: Mot de passe
            host: Hôte (défaut: localhost)
            port: Port (défaut: 3306)
            pool_name: Nom du pool de connexions
            pool_size: Taille du pool
        """
        self.dbconfig = {
            "database_o": database,
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "pool_name": pool_name,
            "pool_size": pool_size
        }
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**self.dbconfig)
        self._init_database()
    
    def _init_database(self) -> None:
        """Crée les tables et index nécessaires."""
        conn = self.connection_pool.get_connection()
        cursor = conn.cursor()
        
        try:
            # Table principale pour les posts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id VARCHAR(255) PRIMARY KEY,
                title TEXT,
                content TEXT,
                score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_score (score),
                FULLTEXT INDEX idx_content (title, content)
            ) ENGINE=InnoDB
            """)
            
            # Table pour les métadonnées
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                post_id VARCHAR(255),
                data JSON,
                PRIMARY KEY (post_id),
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            ) ENGINE=InnoDB
            """)
            
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
    
    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Sauvegarde les données dans MySQL."""
        conn = self.connection_pool.get_connection()
        cursor = conn.cursor()
        
        try:
            # Préparation des données pour l'insertion en batch
            posts_data = [
                (item["id"], item["title"], item["content"], item.get("score", 0))
                for item in data
            ]
            
            # Insertion des posts
            cursor.executemany("""
                INSERT INTO posts (id, title, content, score)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    content = VALUES(content),
                    score = VALUES(score)
            """, posts_data)
            
            # Insertion des métadonnées
            metadata_data = [
                (item["id"], json.dumps(item.get("metadata", {})))
                for item in data if "metadata" in item
            ]
            
            if metadata_data:
                cursor.executemany("""
                    INSERT INTO metadata (post_id, data)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                        data = VALUES(data)
                """, metadata_data)
            
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
    
    def get_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Récupère les données avec les filtres spécifiés."""
        conn = self.connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
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
                # Conversion des timestamps en str
                row["created_at"] = row["created_at"].isoformat()
                row["updated_at"] = row["updated_at"].isoformat()
                # Parse des métadonnées JSON
                if row["metadata"]:
                    row["metadata"] = json.loads(row["metadata"])
                else:
                    row["metadata"] = {}
                results.append(row)
            
            return results
            
        finally:
            cursor.close()
            conn.close()
    
    def update_data(self, id: str, data: Dict[str, Any]) -> None:
        """Met à jour les données existantes."""
        conn = self.connection_pool.get_connection()
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
                    ON DUPLICATE KEY UPDATE
                        data = VALUES(data)
                """, (id, json.dumps(metadata)))
            
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, id: str) -> None:
        """Supprime une entrée et ses métadonnées."""
        conn = self.connection_pool.get_connection()
        cursor = conn.cursor()
        
        try:
            # La suppression des métadonnées est automatique grâce à ON DELETE CASCADE
            cursor.execute("DELETE FROM posts WHERE id = %s", (id,))
            conn.commit()
            
        finally:
            cursor.close()
            conn.close()
    
    def close(self) -> None:
        """Ferme le pool de connexions."""
        # MySQL Connector gère automatiquement la fermeture du pool
        pass
    
    # Méthodes spécifiques à MySQL
    
    def full_text_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Effectue une recherche full-text.
        
        Args:
            query: Texte à rechercher
            
        Returns:
            Liste des posts correspondants avec score de pertinence
        """
        conn = self.connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Préparation de la requête pour la recherche full-text
            search_terms = ' '.join([f'+{term}' for term in query.split()])
            
            cursor.execute("""
                SELECT p.*, m.data as metadata,
                       MATCH(p.title, p.content) AGAINST (%s IN BOOLEAN MODE) as relevance
                FROM posts p
                LEFT JOIN metadata m ON p.id = m.post_id
                WHERE MATCH(p.title, p.content) AGAINST (%s IN BOOLEAN MODE)
                ORDER BY relevance DESC
            """, (search_terms, search_terms))
            
            results = []
            for row in cursor:
                row["created_at"] = row["created_at"].isoformat()
                row["updated_at"] = row["updated_at"].isoformat()
                if row["metadata"]:
                    row["metadata"] = json.loads(row["metadata"])
                else:
                    row["metadata"] = {}
                results.append(row)
            
            return results
            
        finally:
            cursor.close()
            conn.close()
    
    def get_connection(self):
        """
        Récupère une connexion du pool.
        Utile pour les transactions personnalisées.
        """
        return self.connection_pool.get_connection() 