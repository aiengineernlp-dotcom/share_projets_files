import os
import logging
import praw
import sqlite3
import spacy

from fastapi import FastAPI, HTTPException
from typing import List, Dict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Configuration de Reddit API ---

'''Utilisez un fichier .env pour stocker
 les identifiants, comme vous l'avez fait dans la deuxième
 partie du code. Assurez-vous que le 
 fichier .env est ajouté à .gitignore pour éviter de le versionner.'''

REDDIT_CLIENT_ID = "8VNEuay-bprtWEDAxkSwFg"
REDDIT_CLIENT_SECRET = "a9Se9O_fX7yZai5uUfRIBKqCRV-2vw"
REDDIT_USER_AGENT = "MyRedditBot/0.1 by @-Tony"

# Initialisation de l'API Reddit
try:
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    logger.info("Connexion à l'API Reddit établie")
except Exception as e:
    logger.error(f"Erreur lors de la connexion à l'API Reddit: {e}")
    raise

# --- Initialisation de NLP ---
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Modèle NLP chargé avec succès")
except Exception as e:
    logger.warning(f"Impossible de charger le modèle NLP: {e}")
    nlp = None


# --- Initialisation de la base de données ---
def init_db():
    try:
        with sqlite3.connect("reddit_posts.db") as conn:
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
            logger.info("Base de données initialisée avec succès")
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise


# --- Fonction de Scraping ---
def scrape_reddit(subreddit: str, query: str, limit: int = 100):
    try:
        subreddit_obj = reddit.subreddit(subreddit)
        posts_scraped = 0

        logger.info(f"Recherche de '{query}' dans r/{subreddit}, limite: {limit}")

        with sqlite3.connect("reddit_posts.db") as conn:
            cursor = conn.cursor()

            for submission in subreddit_obj.search(query, limit=limit):
                try:
                    cursor.execute("INSERT OR IGNORE INTO posts VALUES (?, ?, ?, ?)",
                                   (submission.id, submission.title, submission.url, submission.created_utc))

                    if cursor.rowcount > 0:
                        posts_scraped += 1
                        logger.info(f"Post enregistré: {submission.title[:50]}...")
                except sqlite3.Error as e:
                    logger.error(f"Erreur lors de l'insertion du post {submission.id}: {e}")

            conn.commit()
            logger.info(f"Scraping terminé: {posts_scraped} nouveaux posts enregistrés")
            return posts_scraped
    except Exception as e:
        logger.error(f"Erreur lors du scraping: {e}")
        return 0


# --- API FastAPI ---
app = FastAPI(title="Reddit Scraper API")


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Reddit Scraper!"}


@app.get("/posts", response_model=List[Dict])
def get_posts(limit: int = 100):
    try:
        with sqlite3.connect("reddit_posts.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, url, created_utc FROM posts ORDER BY created_utc DESC LIMIT ?", (limit,))
            posts = cursor.fetchall()

        if not posts:
            logger.warning("Aucun post trouvé dans la base de données")
            return []

        return [{"id": p[0], "title": p[1], "url": p[2], "created_utc": p[3]} for p in posts]
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération des posts: {e}")
        raise HTTPException(status_code=500, detail="Erreur de base de données")


@app.post("/scrape")
def scrape_endpoint(subreddit: str, query: str, limit: int = 100):
    try:
        posts_count = scrape_reddit(subreddit, query, limit)
        return {"message": f"{posts_count} nouveaux posts ont été récupérés"}
    except Exception as e:
        logger.error(f"Erreur lors du scraping via l'API: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Initialisation de la base de données
    init_db()

    # Scraping initial
    try:
        scrape_reddit("AskDocs", "second opinion", 100)
    except Exception as e:
        logger.error(f"Erreur lors du scraping initial: {e}")

    # Lancement du serveur
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)















"""# CETTE PARTIE DU CODE EXIGE QUE:  Création d'un fichier .env d'exemple si non existant"""
# import os
# import logging
# import praw
# import sqlite3
# import spacy
# from fastapi import FastAPI, HTTPException, Depends
# from typing import List, Dict, Any
# from pydantic import BaseModel
# from dotenv import load_dotenv
#
# # Configuration du logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)
#
# # Chargement des variables d'environnement
# load_dotenv()
#
# # --- Configuration de Reddit API ---
# REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
# REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
# REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MyRedditBot/0.1")
#
#
# # Modèle de données pour les posts
# class Post(BaseModel):
#     id: str
#     title: str
#     url: str
#     created_utc: float = None
#
#
# class Database:
#     def __init__(self, db_path="reddit_posts.db"):
#         self.db_path = db_path
#         self._create_tables()
#
#     def get_connection(self):
#         return sqlite3.connect(self.db_path)
#
#     def _create_tables(self):
#         try:
#             with self.get_connection() as conn:
#                 cursor = conn.cursor()
#                 cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS posts (
#                     id TEXT PRIMARY KEY,
#                     title TEXT,
#                     url TEXT,
#                     created_utc REAL
#                 )
#                 """)
#                 conn.commit()
#                 logger.info("Tables de base de données initialisées avec succès")
#         except sqlite3.Error as e:
#             logger.error(f"Erreur lors de la création des tables: {e}")
#             raise
#
#     def insert_post(self, post: Post):
#         try:
#             with self.get_connection() as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     "INSERT OR IGNORE INTO posts VALUES (?, ?, ?, ?)",
#                     (post.id, post.title, post.url, post.created_utc)
#                 )
#                 conn.commit()
#                 return cursor.rowcount > 0
#         except sqlite3.Error as e:
#             logger.error(f"Erreur lors de l'insertion dans la base de données: {e}")
#             return False
#
#     def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
#         try:
#             with self.get_connection() as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     "SELECT id, title, url, created_utc FROM posts ORDER BY created_utc DESC LIMIT ?",
#                     (limit,)
#                 )
#                 posts = cursor.fetchall()
#                 return [
#                     {"id": p[0], "title": p[1], "url": p[2], "created_utc": p[3]}
#                     for p in posts
#                 ]
#         except sqlite3.Error as e:
#             logger.error(f"Erreur lors de la récupération des posts: {e}")
#             return []
#
#
# class RedditScraper:
#     def __init__(self):
#         # Vérification des identifiants
#         if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]):
#             logger.error("Les identifiants Reddit sont manquants")
#             raise ValueError("Les identifiants Reddit doivent être définis dans le fichier .env")
#
#         try:
#             self.reddit = praw.Reddit(
#                 client_id=REDDIT_CLIENT_ID,
#                 client_secret=REDDIT_CLIENT_SECRET,
#                 user_agent=REDDIT_USER_AGENT
#             )
#             logger.info("Connexion à l'API Reddit établie")
#         except Exception as e:
#             logger.error(f"Erreur lors de la connexion à l'API Reddit: {e}")
#             raise
#
#         # Initialisation de NLP si nécessaire
#         try:
#             self.nlp = spacy.load("en_core_web_sm")
#             logger.info("Modèle NLP chargé avec succès")
#         except Exception as e:
#             logger.warning(f"Impossible de charger le modèle NLP: {e}")
#             self.nlp = None
#
#     def scrape_subreddit(self, subreddit: str, query: str, limit: int = 10, db: Database = None):
#         if not db:
#             logger.error("Base de données non fournie")
#             return []
#
#         try:
#             subreddit_obj = self.reddit.subreddit(subreddit)
#             posts_scraped = 0
#
#             logger.info(f"Recherche de '{query}' dans r/{subreddit}, limite: {limit}")
#
#             for submission in subreddit_obj.search(query, limit=limit):
#                 post = Post(
#                     id=submission.id,
#                     title=submission.title,
#                     url=submission.url,
#                     created_utc=submission.created_utc
#                 )
#
#                 if db.insert_post(post):
#                     posts_scraped += 1
#                     logger.info(f"Post enregistré: {submission.title[:50]}...")
#
#             logger.info(f"Scraping terminé: {posts_scraped} nouveaux posts enregistrés")
#             return posts_scraped
#         except Exception as e:
#             logger.error(f"Erreur lors du scraping: {e}")
#             return 0
#
#
# # --- API FastAPI ---
# app = FastAPI(title="Reddit Scraper API")
# db = Database()
# scraper = RedditScraper()
#
#
# def get_db():
#     return db
#
#
# @app.get("/", tags=["Général"])
# def read_root():
#     return {"message": "Bienvenue sur l'API Reddit Scraper!"}
#
#
# @app.get("/posts", response_model=List[Dict[str, Any]], tags=["Posts"])
# def get_posts(db: Database = Depends(get_db), limit: int = 10):
#     posts = db.get_recent_posts(limit)
#     if not posts:
#         logger.warning("Aucun post trouvé dans la base de données")
#         return []
#     return posts
#
#
# @app.post("/scrape", tags=["Scraping"])
# def scrape_endpoint(subreddit: str, query: str, limit: int = 10, db: Database = Depends(get_db)):
#     try:
#         posts_count = scraper.scrape_subreddit(subreddit, query, limit, db)
#         return {"message": f"{posts_count} nouveaux posts ont été récupérés"}
#     except Exception as e:
#         logger.error(f"Erreur lors du scraping via l'API: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# if __name__ == "__main__":
#     # Création d'un fichier .env d'exemple si non existant
#     if not os.path.exists(".env"):
#         with open(".env", "w") as f:
#             f.write("""# Remplacez ces valeurs par vos identifiants Reddit
# REDDIT_CLIENT_ID=votre_client_id
# REDDIT_CLIENT_SECRET=votre_client_secret
# REDDIT_USER_AGENT=MyRedditBot/0.1 by @YourUsername
# """)
#         logger.info("Fichier .env d'exemple créé. Veuillez le remplir avec vos identifiants.")
#
#     # Scraping initial si les identifiants sont configurés
#     if all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET]) and REDDIT_CLIENT_ID != "votre_client_id":
#         try:
#             scraper.scrape_subreddit("AskDocs", "second opinion", 10, db)
#         except Exception as e:
#             logger.error(f"Erreur lors du scraping initial: {e}")
#
#     # Lancement du serveur
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)



'''tu comprend ce que fait ce code ?
Oui, je comprends parfaitement ce que fait ce code. Il s'agit d'une application qui combine web scraping (extraction de données) de Reddit, stockage des données dans une base de données SQLite, et exposition de ces données via une API REST construite avec FastAPI. Voici une explication détaillée de ce que fait chaque partie du code :

1. Connexion à l'API Reddit
Le code utilise la bibliothèque praw pour interagir avec l'API Reddit. Il se connecte à Reddit en utilisant des identifiants (client ID, client secret, et user agent) pour accéder aux données des subreddits.

python
Copy
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)
Objectif : Récupérer des posts Reddit en fonction d'une requête de recherche.

2. Initialisation de la base de données SQLite
Le code crée une base de données SQLite nommée reddit_posts.db avec une table posts pour stocker les informations des posts Reddit (ID, titre, URL, et date de création).

python
Copy
with sqlite3.connect("reddit_posts.db") as conn:
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
Objectif : Stocker les posts Reddit pour une utilisation ultérieure.

3. Scraping des posts Reddit
La fonction scrape_reddit recherche des posts dans un subreddit spécifique en fonction d'une requête (par exemple, "second opinion" dans le subreddit "AskDocs"). Les posts trouvés sont ensuite enregistrés dans la base de données.

python
Copy
def scrape_reddit(subreddit: str, query: str, limit: int = 100):
    subreddit_obj = reddit.subreddit(subreddit)
    for submission in subreddit_obj.search(query, limit=limit):
        cursor.execute("INSERT OR IGNORE INTO posts VALUES (?, ?, ?, ?)",
                       (submission.id, submission.title, submission.url, submission.created_utc))
Objectif : Extraire des posts Reddit et les stocker dans la base de données.

4. API FastAPI
Le code expose une API REST avec FastAPI pour permettre aux utilisateurs d'interagir avec les données scrapées. Il propose deux endpoints principaux :

a. Endpoint racine (/)
python
Copy
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Reddit Scraper!"}
Objectif : Afficher un message de bienvenue.

b. Endpoint /posts
python
Copy
@app.get("/posts", response_model=List[Dict])
def get_posts(limit: int = 100):
    with sqlite3.connect("reddit_posts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, url, created_utc FROM posts ORDER BY created_utc DESC LIMIT ?", (limit,))
        posts = cursor.fetchall()
    return [{"id": p[0], "title": p[1], "url": p[2], "created_utc": p[3]} for p in posts]
Objectif : Récupérer les posts stockés dans la base de données et les renvoyer au format JSON.

c. Endpoint /scrape
python
Copy
@app.post("/scrape")
def scrape_endpoint(subreddit: str, query: str, limit: int = 100):
    posts_count = scrape_reddit(subreddit, query, limit)
    return {"message": f"{posts_count} nouveaux posts ont été récupérés"}
Objectif : Lancer un scraping manuel en spécifiant un subreddit, une requête, et une limite.

5. Logging
Le code utilise le module logging pour enregistrer les événements importants (connexion à Reddit, insertion de posts, erreurs, etc.).

python
Copy
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
Objectif : Faciliter le débogage et le suivi de l'application.

6. Initialisation de NLP (spacy)
Le code charge un modèle de traitement du langage naturel (NLP) avec spacy, mais il n'est pas utilisé dans le code actuel.

python
Copy
nlp = spacy.load("en_core_web_sm")
Objectif : Si vous prévoyez d'analyser le texte des posts Reddit (par exemple, pour extraire des entités ou des mots-clés), ce modèle sera utile.

7. Lancement de l'application
Le code lance l'application FastAPI avec uvicorn et effectue un scraping initial au démarrage.

python
Copy
if __name__ == "__main__":
    init_db()  # Initialisation de la base de données
    scrape_reddit("AskDocs", "second opinion", 100)  # Scraping initial
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Lancement de l'API
Objectif : Démarrer l'API et préparer les données pour les utilisateurs.

Fonctionnement global
Scraping : Le code se connecte à Reddit, recherche des posts dans un subreddit spécifique, et les enregistre dans une base de données SQLite.

Stockage : Les posts sont stockés dans une table SQLite pour une récupération ultérieure.

API : FastAPI expose les données scrapées via des endpoints REST.

Logging : Toutes les actions importantes sont enregistrées pour le suivi et le débogage.

Cas d'utilisation
Scraping de données : Récupérer des posts Reddit sur un sujet spécifique (par exemple, "second opinion" dans "AskDocs").

Stockage des données : Enregistrer les posts dans une base de données pour une analyse ultérieure.

Exposition des données : Permettre à d'autres applications ou utilisateurs d'accéder aux données via une API REST.

Améliorations possibles
Sécurité : Utiliser un fichier .env pour stocker les identifiants Reddit.

Validation des entrées : Valider les paramètres des endpoints avec pydantic.

Tests unitaires : Ajouter des tests pour vérifier le bon fonctionnement du scraping et de l'API.

Scraping périodique : Utiliser un scheduler pour exécuter le scraping à intervalles réguliers.

En résumé, ce code est une application complète qui combine web scraping, stockage de données, et exposition via une API. Il est bien structuré et prêt à être amélioré pour une utilisation en production.'''

"""Tests pour la phase 2 - Traitement du Langage Naturel."""

import pytest
from unittest.mock import patch, MagicMock
from phase_2_traitement_du_langage_naturel import (
    TextProcessor,
    SentimentAnalyzer,
    EntityExtractor,
    LanguageDetector
)

@pytest.fixture
def text_processor():
    """Fixture pour le processeur de texte"""
    return TextProcessor()

@pytest.fixture
def sentiment_analyzer():
    """Fixture pour l'analyseur de sentiment"""
    return SentimentAnalyzer()

@pytest.fixture
def entity_extractor():
    """Fixture pour l'extracteur d'entités"""
    return EntityExtractor()

@pytest.fixture
def language_detector():
    """Fixture pour le détecteur de langue"""
    return LanguageDetector()

def test_text_preprocessing(text_processor):
    """Test le prétraitement du texte"""
    text = "Bonjour! Comment allez-vous? Je suis malade depuis 3 jours."
    
    # Prétraiter le texte
    processed = text_processor.preprocess(text)
    
    # Vérifier les résultats
    assert isinstance(processed, str)
    assert "!" not in processed  # Ponctuation supprimée
    assert "?" not in processed
    assert processed.islower()  # Texte en minuscules
    assert len(processed.split()) > 0  # Texte non vide

def test_sentiment_analysis(sentiment_analyzer):
    """Test l'analyse de sentiment"""
    # Test avec un texte positif
    positive_text = "Je me sens beaucoup mieux aujourd'hui, merci!"
    positive_sentiment = sentiment_analyzer.analyze(positive_text)
    assert positive_sentiment["polarity"] > 0
    
    # Test avec un texte négatif
    negative_text = "Je suis très inquiet et stressé par ma situation."
    negative_sentiment = sentiment_analyzer.analyze(negative_text)
    assert negative_sentiment["polarity"] < 0
    
    # Test avec un texte neutre
    neutral_text = "Le temps est nuageux aujourd'hui."
    neutral_sentiment = sentiment_analyzer.analyze(neutral_text)
    assert abs(neutral_sentiment["polarity"]) < 0.1

def test_entity_extraction(entity_extractor):
    """Test l'extraction d'entités"""
    text = "Je suis à Dubai aux Émirats Arabes Unis depuis 2 semaines."
    
    # Extraire les entités
    entities = entity_extractor.extract(text)
    
    # Vérifier les résultats
    assert isinstance(entities, dict)
    assert "locations" in entities
    assert "Dubai" in entities["locations"]
    assert "Émirats Arabes Unis" in entities["locations"]
    assert "dates" in entities
    assert "2 semaines" in entities["dates"]

def test_language_detection(language_detector):
    """Test la détection de langue"""
    # Test avec un texte en français
    french_text = "Bonjour, je vais bien."
    french_lang = language_detector.detect(french_text)
    assert french_lang == "fr"
    
    # Test avec un texte en anglais
    english_text = "Hello, I am fine."
    english_lang = language_detector.detect(english_text)
    assert english_lang == "en"
    
    # Test avec un texte en arabe
    arabic_text = "مرحبا، أنا بخير"
    arabic_lang = language_detector.detect(arabic_text)
    assert arabic_lang == "ar"

@patch('spacy.load')
def test_spacy_initialization(mock_spacy_load):
    """Test l'initialisation de SpaCy"""
    # Simuler le chargement de SpaCy
    mock_nlp = MagicMock()
    mock_spacy_load.return_value = mock_nlp
    
    # Créer une instance de TextProcessor
    processor = TextProcessor()
    
    # Vérifier que SpaCy a été chargé
    mock_spacy_load.assert_called_once()
    assert processor.nlp is not None

def test_error_handling(text_processor):
    """Test la gestion des erreurs"""
    # Test avec un texte vide
    with pytest.raises(ValueError):
        text_processor.preprocess("")
    
    # Test avec un texte None
    with pytest.raises(ValueError):
        text_processor.preprocess(None)
    
    # Test avec un texte non-string
    with pytest.raises(TypeError):
        text_processor.preprocess(123)

@pytest.fixture
def db_manager():
    """Fixture pour le gestionnaire de base de données"""
    db_path = "test_phase2_data.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    manager = DatabaseManager(db_path)
    yield manager
    if os.path.exists(db_path):
        os.remove(db_path)
