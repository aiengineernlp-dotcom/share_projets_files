import sqlite3
import logging
import os
from contextlib import contextmanager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "test.db"):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        try:
            logger.info(f"Initialisation de la base de données à {self.db_path}")
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Table pour les conversations
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    created_at REAL,
                    last_message_at REAL,
                    context TEXT,
                    status TEXT
                )
                """)
                
                # Table pour les messages
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    role TEXT,
                    content TEXT,
                    created_at REAL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
                """)
                
                # Table pour les utilisateurs GCC
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS gcc_users (
                    post_id INTEGER PRIMARY KEY,
                    country TEXT,
                    city TEXT
                )
                """)
                
                # Table pour les posts
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY,
                    author TEXT,
                    category TEXT,
                    overall_score REAL,
                    created_utc REAL
                )
                """)
                
                conn.commit()
                logger.info("Base de données initialisée avec succès")
                
                # Vérifier que les tables ont été créées
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                logger.info(f"Tables créées : {[table[0] for table in tables]}")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            raise

def test_database_initialization():
    """Test l'initialisation de la base de données"""
    # Utiliser une base de données temporaire
    db_path = "test_temp.db"
    
    # Supprimer la base de données si elle existe déjà
    if os.path.exists(db_path):
        os.remove(db_path)
    
    manager = DatabaseManager(db_path)
    
    with manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        assert "conversations" in table_names, "La table conversations n'a pas été créée"
        assert "chat_messages" in table_names, "La table chat_messages n'a pas été créée"
        assert "gcc_users" in table_names, "La table gcc_users n'a pas été créée"
        assert "posts" in table_names, "La table posts n'a pas été créée"
    
    # Nettoyer la base de données temporaire
    os.remove(db_path)

if __name__ == "__main__":
    test_database_initialization() 