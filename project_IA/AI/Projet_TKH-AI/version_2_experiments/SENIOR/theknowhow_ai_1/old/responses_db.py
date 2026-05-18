"""Module de gestion des réponses sauvegardées dans la base de données."""

import sqlite3
from typing import Dict, Optional

class SavedResponses:
    def __init__(self, db_path="medical_agent.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """Crée la table des réponses sauvegardées."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    language TEXT NOT NULL,
                    category TEXT,
                    created_at DATETIME NOT NULL
                )
            """)
            
            # Insérer quelques réponses de base
            cursor.execute("""
                INSERT OR IGNORE INTO saved_responses 
                (message, response, language, category, created_at)
                VALUES 
                ('mal à la tête', 'Je comprends que vous souffrez de maux de tête. Voici quelques conseils :\n1. Reposez-vous dans un endroit calme\n2. Buvez beaucoup d''eau\n3. Évitez les écrans\nSi les symptômes persistent, consultez un médecin.', 'fr', 'headache', datetime('now')),
                ('headache', 'I understand you''re suffering from a headache. Here are some tips:\n1. Rest in a quiet place\n2. Drink plenty of water\n3. Avoid screens\nIf symptoms persist, consult a doctor.', 'en', 'headache', datetime('now')),
                ('fièvre', 'La fièvre peut être le signe d''une infection. Je vous conseille de :\n1. Prendre votre température\n2. Boire beaucoup d''eau\n3. Reposer\nSi la fièvre dépasse 39°C, consultez un médecin.', 'fr', 'fever', datetime('now')),
                ('fever', 'Fever can be a sign of infection. I recommend:\n1. Taking your temperature\n2. Drinking plenty of water\n3. Resting\nIf fever exceeds 39°C, consult a doctor.', 'en', 'fever', datetime('now'))
            """)
            conn.commit()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_response(self, message: str, language: str) -> Optional[str]:
        """Récupère une réponse sauvegardée pour un message donné."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT response FROM saved_responses 
                    WHERE message LIKE ? AND language = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (f"%{message}%", language))
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de la réponse : {e}")
            return None

    def save_response(self, message: str, response: str, language: str, category: Optional[str] = None):
        """Sauvegarde une nouvelle réponse."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO saved_responses 
                    (message, response, language, category, created_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                """, (message, response, language, category))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la sauvegarde de la réponse : {e}") 