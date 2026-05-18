"""
Scraper Twitter pour collecter des posts médicaux.

RÔLE PRINCIPAL :
---------------
Ce module implémente un scraper Twitter spécialisé dans la collecte et l'analyse de tweets médicaux.
Il utilise l'API Twitter (tweepy) pour récupérer les tweets, analyse leur contenu avec des modèles NLP,
et stocke les résultats dans une base de données SQLite avec gestion des métriques et des relations.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Dépend de :
  * config/twitter_config.py (configuration du scraper)
  * config/settings.py (variables d'environnement)
  * processors/medical_analysis/medical_analyzer.py (analyseur médical)
  * processors/medical_analysis/urgency_analyzer.py (analyseur d'urgence)
  * nlp/language_detector.py (détecteur de langue)

STRUCTURE DU CONTENU :
--------------------
1. Imports et configuration
2. Classe TwitterScraper :
   - Initialisation de l'API Twitter
   - Gestion de la base de données
   - Analyse des tweets
   - Recherche et collecte
   - Sauvegarde des données

FONCTIONS PRINCIPALES :
---------------------
- __init__() : Initialise le scraper et les analyseurs
- _init_database() : Configure la base de données SQLite
- _save_tweets() : Sauvegarde les tweets dans la base
- _analyze_tweet() : Analyse le contenu d'un tweet
- _search_tweets() : Recherche des tweets avec gestion des limites
- scrape_medical_tweets() : Collecte les tweets médicaux

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il est le composant principal de collecte de données Twitter
- Il implémente l'analyse des tweets médicaux
- Il gère les métriques et les relations entre tweets
- Il assure la persistance des données collectées
"""

import os
import json
import sqlite3
import time
from datetime import datetime
import tweepy
from typing import List, Dict, Any, Optional
import spacy
from tqdm import tqdm

from config.twitter_config import (
    TWITTER_CONFIG,
    MEDICAL_HASHTAGS,
    MEDICAL_KEYWORDS,
    SEARCH_PARAMS,
    DB_CONFIG
)
from config.settings import logger
from phase1_data_collection.processors.medical_analysis.medical_analyzer import MedicalAnalyzer
from phase1_data_collection.processors.medical_analysis.urgency_analyzer import UrgencyAnalyzer
from nlp.language_detector import detect_language

class TwitterScraper:
    def __init__(self):
        """Initialise le scraper Twitter avec l'API et les analyseurs."""
        # Initialisation de l'API Twitter
        self.client = tweepy.Client(
            bearer_token=TWITTER_CONFIG["bearer_token"],
            consumer_key=TWITTER_CONFIG["consumer_key"],
            consumer_secret=TWITTER_CONFIG["consumer_secret"],
            access_token=TWITTER_CONFIG["access_token"],
            access_token_secret=TWITTER_CONFIG["access_token_secret"],
            wait_on_rate_limit=True
        )

        # Initialisation des analyseurs
        self.nlp = spacy.load("en_core_web_sm")
        self.medical_analyzer = MedicalAnalyzer(self.nlp)
        self.urgency_analyzer = UrgencyAnalyzer(self.nlp)

        # Initialisation de la base de données
        self.db_path = DB_CONFIG["db_path"]
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()

        logger.info("TwitterScraper initialisé avec succès")

    def _init_database(self):
        """Initialise la base de données SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Création de la table principale
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS twitter_posts (
                    id TEXT PRIMARY KEY,
                    tweet_id TEXT UNIQUE NOT NULL,
                    author_id TEXT NOT NULL,
                    author_username TEXT,
                    title TEXT,
                    body TEXT NOT NULL,
                    created_utc REAL NOT NULL,
                    score INTEGER DEFAULT 0,
                    retweet_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    quote_count INTEGER DEFAULT 0,
                    
                    medical_relevance_score REAL DEFAULT 0.0,
                    urgency_score REAL DEFAULT 0.0,
                    second_opinion_score REAL DEFAULT 0.0,
                    overall_score REAL DEFAULT 0.0,
                    
                    category TEXT,
                    language TEXT,
                    keywords TEXT,
                    search_term TEXT,
                    
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

                # Création des index
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_twitter_posts_category ON twitter_posts(category)
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_twitter_posts_language ON twitter_posts(language)
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_twitter_posts_created_utc ON twitter_posts(created_utc)
                """)

                # Trigger pour updated_at
                cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_twitter_posts_updated_at 
                    AFTER UPDATE ON twitter_posts
                BEGIN
                    UPDATE twitter_posts SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END
                """)

                conn.commit()
                logger.info("Base de données Twitter initialisée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            raise

    def _save_tweets(self, tweets: List[Dict[str, Any]]):
        """Sauvegarde un lot de tweets dans la base de données."""
        if not tweets:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for tweet in tweets:
                    cursor.execute("""
                    INSERT OR REPLACE INTO twitter_posts (
                        id, tweet_id, author_id, author_username, title, body,
                        created_utc, score, retweet_count, reply_count, quote_count,
                        medical_relevance_score, urgency_score, second_opinion_score,
                        overall_score, category, language, keywords, search_term
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tweet["id"],
                        tweet["tweet_id"],
                        tweet["author_id"],
                        tweet["author_username"],
                        tweet.get("title", ""),
                        tweet["body"],
                        tweet["created_utc"],
                        tweet.get("score", 0),
                        tweet.get("retweet_count", 0),
                        tweet.get("reply_count", 0),
                        tweet.get("quote_count", 0),
                        tweet.get("medical_relevance_score", 0.0),
                        tweet.get("urgency_score", 0.0),
                        tweet.get("second_opinion_score", 0.0),
                        tweet.get("overall_score", 0.0),
                        tweet.get("category", ""),
                        tweet.get("language", ""),
                        json.dumps(tweet.get("keywords", [])),
                        tweet.get("search_term", "")
                    ))
                conn.commit()
                logger.info(f"Sauvegarde de {len(tweets)} tweets effectuée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des tweets: {e}")
            raise

    def _analyze_tweet(self, tweet: Dict[str, Any], search_term: str) -> Optional[Dict[str, Any]]:
        """Analyse un tweet et retourne les résultats d'analyse."""
        try:
            text = tweet.text
            
            # Vérification de la longueur minimale
            if len(text) < SEARCH_PARAMS["min_tweet_length"]:
                return None

            # Détection de la langue
            language = detect_language(text)
            if language != SEARCH_PARAMS["language"]:
                return None

            # Analyse médicale
            medical_analysis = self.medical_analyzer.analyze_medical_text(text)
            urgency_analysis = self.urgency_analyzer.analyze_urgency(text)

            # Extraction des mots-clés à partir du texte
            doc = self.nlp(text)
            keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"] and token.text.lower() in MEDICAL_KEYWORDS]

            # Calcul du score global
            overall_score = (
                medical_analysis["medical_score"] * 0.4 +
                urgency_analysis["urgency_score"] * 0.4 +
                medical_analysis["second_opinion_score"] * 0.2
            )

            # Création du dictionnaire de résultats
            return {
                "id": f"tw_{tweet.id}",
                "tweet_id": str(tweet.id),
                "author_id": str(tweet.author_id),
                "author_username": tweet.author.username if hasattr(tweet, 'author') else None,
                "title": text.split('\n')[0][:100],
                "body": text,
                "created_utc": tweet.created_at.timestamp(),
                "score": tweet.public_metrics.get("like_count", 0) if hasattr(tweet, 'public_metrics') else 0,
                "retweet_count": tweet.public_metrics.get("retweet_count", 0) if hasattr(tweet, 'public_metrics') else 0,
                "reply_count": tweet.public_metrics.get("reply_count", 0) if hasattr(tweet, 'public_metrics') else 0,
                "quote_count": tweet.public_metrics.get("quote_count", 0) if hasattr(tweet, 'public_metrics') else 0,
                "medical_relevance_score": medical_analysis["medical_score"],
                "urgency_score": urgency_analysis["urgency_score"],
                "second_opinion_score": medical_analysis["second_opinion_score"],
                "overall_score": overall_score,
                "category": medical_analysis["category"],
                "language": language,
                "keywords": keywords,
                "search_term": search_term
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du tweet {tweet.id}: {e}")
            return None

    def _search_tweets(self, query: str, retries: int = 0) -> Optional[tweepy.Response]:
        """Effectue une recherche de tweets avec gestion des erreurs et des limites de taux."""
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=SEARCH_PARAMS["max_results_per_query"],
                tweet_fields=["created_at", "public_metrics", "author_id"],
                user_fields=["username"],
                expansions=["author_id"]
            )
            time.sleep(SEARCH_PARAMS["delay_between_queries"])  # Délai entre les requêtes
            return tweets
        except tweepy.TooManyRequests:
            if retries < SEARCH_PARAMS["max_retries"]:
                wait_time = 60 * (retries + 1)  # Attente exponentielle
                logger.warning(f"Limite de taux atteinte. Attente de {wait_time} secondes...")
                time.sleep(wait_time)
                return self._search_tweets(query, retries + 1)
            else:
                logger.error("Nombre maximum de tentatives atteint pour la limite de taux")
                return None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de tweets: {e}")
            return None

    def scrape_medical_tweets(self):
        """Collecte les tweets médicaux basés sur les hashtags configurés."""
        total_tweets = 0
        batch = []

        try:
            for hashtag in tqdm(MEDICAL_HASHTAGS, desc="Traitement des hashtags"):
                query = f"{hashtag} -is:retweet"
                
                for _ in range(SEARCH_PARAMS["max_queries_per_hashtag"]):
                    tweets = self._search_tweets(query)
                    if not tweets or not tweets.data:
                        continue

                    for tweet in tweets.data:
                        analyzed_tweet = self._analyze_tweet(tweet, hashtag)
                        if analyzed_tweet:
                            batch.append(analyzed_tweet)
                            total_tweets += 1

                        # Sauvegarde par lots
                        if len(batch) >= DB_CONFIG["batch_size"]:
                            self._save_tweets(batch)
                            batch = []

            # Sauvegarde des tweets restants
            if batch:
                self._save_tweets(batch)

            logger.info(f"Collecte terminée. Total des tweets collectés: {total_tweets}")
            return total_tweets
            
        except Exception as e:
            logger.error(f"Erreur lors du scraping: {e}")
            if batch:  # Sauvegarde des tweets en cas d'erreur
                self._save_tweets(batch)
            raise

def main():
    """Point d'entrée principal pour le scraper Twitter."""
    try:
        scraper = TwitterScraper()
        total_tweets = scraper.scrape_medical_tweets()
        
        logger.info(f"Scraping Twitter terminé avec succès. {total_tweets} tweets collectés.")
        return {
            "status": "success",
            "total_tweets": total_tweets
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du scraper Twitter: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    main() 