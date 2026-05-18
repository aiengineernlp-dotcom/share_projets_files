"""
Scraper Reddit multilingue pour collecter les posts médicaux
"""
import sys
import os
from pathlib import Path

# Ajout du répertoire racine au PYTHONPATH
project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
sys.path.append(project_root)

import logging
import praw
import sqlite3
import spacy
from spacy.matcher import PhraseMatcher, Matcher
from textblob import TextBlob
from typing import List, Dict, Optional, Any
from config.settings import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, REDDIT_DB_PATH
from config.reddit_config import (
    MEDICAL_SUBREDDITS, SEARCH_TERMS, POSTS_PER_SEARCH,
    CATEGORIZATION_THRESHOLDS, SCORE_WEIGHTS,
    NLP_CONFIG, POST_CATEGORIES, LOG_CONFIG
)
from storage.models.post import Post, PostCreate
from phase1_data_collection.processors.medical_analysis.medical_analyzer import MedicalAnalyzer
from nlp.analysis import TextAnalyzer
from datetime import datetime
from tqdm import tqdm

# Configuration du logging
logger = logging.getLogger("theknowhow_ai")

class RedditScraper:
    def __init__(self):
        # Initialisation de l'API Reddit
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        
        # Subreddits médicaux à scraper
        self.medical_subreddits = MEDICAL_SUBREDDITS

        # Termes de recherche pour différentes catégories
        self.search_terms = SEARCH_TERMS
        
        # Initialisation des modèles NLP pour chaque langue
        self.nlp_models = {}
        try:
            for lang, model in NLP_CONFIG['models'].items():
                self.nlp_models[lang] = spacy.load(model)
                logger.info(f"Modèle NLP pour {lang} chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des modèles spaCy: {e}")
            raise
            
        # Initialisation des analyseurs pour chaque langue
        self.medical_analyzers = {
            lang: MedicalAnalyzer(model) for lang, model in self.nlp_models.items()
        }
        
        # Initialisation de la base de données
        self.init_db()
        logger.info("Scraper Reddit multilingue initialisé")

    def init_db(self):
        """Initialise la base de données SQLite"""
        # Utilisation du chemin défini dans les variables d'environnement
        self.db_path = os.path.join(project_root, REDDIT_DB_PATH)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        logger.info(f"Connexion à la base de données établie: {self.db_path}")
        
        cursor = self.conn.cursor()
        
        # Création de la table des posts avec support multilingue
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            subreddit TEXT,
            title TEXT,
            body TEXT,
            author TEXT,
            url TEXT, 
            created_utc INTEGER,
            score INTEGER,
            num_comments INTEGER,
            category TEXT,
            search_category TEXT,
            search_term TEXT,
            language TEXT,
            medical_relevance_score REAL,
            urgency_score REAL,
            second_opinion_score REAL,
            overall_score REAL,
            keywords TEXT,
            is_medical_related BOOLEAN,
            has_symptoms BOOLEAN,
            has_diagnosis BOOLEAN,
            has_treatment BOOLEAN
        )
        ''')
        logger.info("Table posts créée ou déjà existante")
        
        self.conn.commit()
        logger.info("Initialisation de la base de données terminée")

    def detect_language(self, text: str) -> str:
        """
        Détecte la langue du texte
        """
        try:
            blob = TextBlob(text)
            detected_lang = blob.detect_language()
            return detected_lang if detected_lang in self.nlp_models else NLP_CONFIG['default']
        except:
            return NLP_CONFIG['default']

    def is_medical_related(self, text: str, lang: str) -> bool:
        """
        Vérifie si le texte est lié à un problème médical
        """
        # Mots-clés médicaux par langue
        medical_keywords = {
            'en': ['symptom', 'diagnosis', 'treatment', 'doctor', 'hospital', 'pain', 'illness', 'disease', 'condition'],
            'fr': ['symptôme', 'diagnostic', 'traitement', 'médecin', 'hôpital', 'douleur', 'maladie', 'état'],
            'ar': ['عَرَض', 'تَشخِيص', 'عِلاج', 'طَبيب', 'مُستَشفى', 'أَلَم', 'مَرَض', 'حَالَة']
        }
        
        # Vérification des mots-clés
        if lang in medical_keywords:
            return any(keyword in text.lower() for keyword in medical_keywords[lang])
        return False

    def has_medical_elements(self, analysis: dict) -> dict:
        """
        Vérifie la présence d'éléments médicaux dans l'analyse
        """
        return {
            'has_symptoms': any(ent['label'] == 'SYMPTOM' for ent in analysis['medical_entities']),
            'has_diagnosis': any(ent['label'] == 'DIAGNOSIS' for ent in analysis['medical_entities']),
            'has_treatment': any(ent['label'] == 'TREATMENT' for ent in analysis['medical_entities'])
        }

    def categorize_post(self, scores: dict, search_category: str) -> str:
        """
        Catégorise un post en fonction des scores
        """
        if scores['urgency_score'] > CATEGORIZATION_THRESHOLDS['urgent_help']:
            return POST_CATEGORIES['emergency']
        elif scores['second_opinion_score'] > CATEGORIZATION_THRESHOLDS['urgent_second_opinion']:
            return POST_CATEGORIES['urgent']
        elif scores['second_opinion_score'] > CATEGORIZATION_THRESHOLDS['priority_second_opinion']:
            return POST_CATEGORIES['priority']
        elif scores['second_opinion_score'] > CATEGORIZATION_THRESHOLDS['standard_second_opinion']:
            return POST_CATEGORIES['standard']
        else:
            return POST_CATEGORIES['quick']

    def search_and_analyze(self):
        """
        Recherche et analyse les posts selon les différentes catégories et langues
        """
        total_posts = 0
        categorized_posts = {category: {lang: 0 for lang in NLP_CONFIG['models'].keys()} 
                           for category in SEARCH_TERMS.keys()}
        
        for subreddit_name in self.medical_subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                logger.info(f"Analyse du subreddit: {subreddit_name}")
                
                # Recherche pour chaque catégorie et langue
                for category, lang_terms in self.search_terms.items():
                    for lang, terms in lang_terms.items():
                        for search_term in terms:
                            try:
                                logger.info(f"Recherche de '{search_term}' ({lang}) dans r/{subreddit_name}")
                                # cette ligne dessous est la recherche classique.
                                # posts = subreddit.search(search_term, limit=POSTS_PER_SEARCH) 
                                # je peux utiliser time_filter pour limiter la recherche à un mois (month) ou une semaine (week) ou un jour (day) ou une heure (hour)  ou une minute (minute) ou une seconde (second) ou une année (year) ou un décennie (decade) ou un siècle (century) ou un millénaire (millennium) ou simplement (all)  
                                posts = subreddit.search(search_term, sort='new', time_filter='month', limit=POSTS_PER_SEARCH)
                                
                                for post in posts:
                                    # Détection de la langue du post
                                    post_text = f"{post.title} {post.selftext}"
                                    detected_lang = self.detect_language(post_text)
                                    
                                    # Vérification de la pertinence médicale
                                    if not self.is_medical_related(post_text, detected_lang):
                                        continue
                                    
                                    # Utilisation des analyseurs appropriés
                                    analysis = self.medical_analyzers[detected_lang].analyze_medical_text(post_text)
                                    
                                    # Vérification des éléments médicaux
                                    medical_elements = self.has_medical_elements(analysis)
                                    
                                    # Calcul des scores
                                    scores = {
                                        'medical_relevance_score': analysis['medical_score'],
                                        'urgency_score': analysis['urgency_score'],
                                        'second_opinion_score': analysis['second_opinion_score']
                                    }
                                    
                                    # Calcul du score global avec pondération des éléments médicaux
                                    overall_score = (
                                        scores['medical_relevance_score'] * SCORE_WEIGHTS['medical_relevance'] +
                                        scores['urgency_score'] * SCORE_WEIGHTS['urgency'] +
                                        scores['second_opinion_score'] * SCORE_WEIGHTS['second_opinion']
                                    )
                                    
                                    # Ajustement du score en fonction des éléments médicaux présents
                                    if medical_elements['has_symptoms']:
                                        overall_score *= 1.2
                                    if medical_elements['has_diagnosis']:
                                        overall_score *= 1.1
                                    if medical_elements['has_treatment']:
                                        overall_score *= 1.1
                                    
                                    # Catégorisation
                                    post_category = self.categorize_post(scores, category)
                                    
                                    # Sauvegarde dans la base de données
                                    cursor = self.conn.cursor()
                                    cursor.execute('''
                                    INSERT OR REPLACE INTO posts (
                                        id, subreddit, title, body, author,url, created_utc,
                                        score, num_comments, category, search_category,
                                        search_term, language, medical_relevance_score,
                                        urgency_score, second_opinion_score, overall_score,
                                        keywords, is_medical_related, has_symptoms,
                                        has_diagnosis, has_treatment
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (
                                        post.id, subreddit_name, post.title, post.selftext,
                                        str(post.author), post.url, post.created_utc, post.score,
                                        post.num_comments, post_category, category,
                                        search_term, detected_lang, scores['medical_relevance_score'],
                                        scores['urgency_score'], scores['second_opinion_score'],
                                        overall_score, ','.join(ent['text'] for ent in analysis['medical_entities']),
                                        True, medical_elements['has_symptoms'],
                                        medical_elements['has_diagnosis'], medical_elements['has_treatment']
                                    ))
                                    
                                    self.conn.commit()
                                    total_posts += 1
                                    categorized_posts[category][detected_lang] += 1
                                    
                                    logger.info(f"Post enregistré: {post.title[:50]}... "
                                              f"Langue: {detected_lang}, "
                                              f"Catégorie: {post_category}, Score: {overall_score:.2f}")
                            except Exception as e:
                                logger.error(f"Erreur lors du traitement du terme de recherche '{search_term}': {str(e)}")
                                continue
            except Exception as e:
                logger.error(f"Erreur lors du scraping du subreddit {subreddit_name}: {str(e)}")
                continue
        
        # Affichage des statistiques par langue
        logger.info(f"Total des posts analysés : {total_posts}")
        for category, lang_counts in categorized_posts.items():
            for lang, count in lang_counts.items():
                logger.info(f"Posts de type {category} en {lang}: {count}")

def main():
    """
    Fonction principale
    """
    try:
        # Initialisation du scraper
        scraper = RedditScraper()
        logger.info("Scraper Reddit multilingue initialisé")
        
        # Lancement de la recherche et analyse
        scraper.search_and_analyze()
        
        return {
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    main()