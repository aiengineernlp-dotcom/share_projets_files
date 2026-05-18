import os
import logging
import praw
import sqlite3
import spacy
import numpy as np
from spacy.matcher import PhraseMatcher, Matcher
from textblob import TextBlob
from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import re
from conversational_agent import ConversationalAgent

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Initialisation de l'API Reddit ---
REDDIT_CLIENT_ID = "8VNEuay-bprtWEDAxkSwFg"
REDDIT_CLIENT_SECRET = "a9Se9O_fX7yZai5uUfRIBKqCRV-2vw"
REDDIT_USER_AGENT = "MyRedditBot/0.1 by @-Tony"

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


# --- Initialisation des Matchers SpaCy ---
def init_matchers():
    # Phrases clés pour la recherche d'un second avis médical
    second_opinion_phrases = [
        "second opinion", "another doctor", "other doctor", "see specialist",
        "different doctor", "consult another", "another physician",
        "get checked again", "additional medical opinion", "different diagnosis",
        "need confirmation", "verify diagnosis", "doubt diagnosis",
        "unsure about treatment", "alternative treatment"
    ]

    # Phrases exprimant de l'inquiétude/urgence
    concern_phrases = [
        "worried", "anxious", "scared", "terrified", "concerned",
        "frightened", "panicking", "alarmed", "distressed",
        "urgent", "immediately", "emergency", "asap", "serious",
        "life threatening", "critical", "deteriorating", "getting worse",
        "severe pain", "extreme pain", "unbearable pain"
    ]

    # Phrases médicales générales
    medical_phrases = [
        "symptoms", "diagnosis", "treatment", "medication", "doctor",
        "hospital", "clinic", "surgery", "medical", "health", "disease",
        "condition", "illness", "specialist", "prescription", "therapy",
        "pain", "chronic", "acute", "diagnosis"
    ]

    # Créer les matchers de phrases
    second_opinion_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    concern_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    medical_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    # Ajouter les patterns
    second_opinion_matcher.add("SECOND_OPINION", [nlp(text) for text in second_opinion_phrases])
    concern_matcher.add("CONCERN", [nlp(text) for text in concern_phrases])
    medical_matcher.add("MEDICAL", [nlp(text) for text in medical_phrases])

    # Matcher pour structures syntaxiques spécifiques
    syntax_matcher = Matcher(nlp.vocab)

    # Pattern pour "Should I + [verb]" questions
    syntax_matcher.add("SHOULD_I", [[{"LOWER": "should"}, {"LOWER": "i"}, {"POS": "VERB"}]])

    # Pattern pour "Is this + [adjective]" questions
    syntax_matcher.add("IS_THIS", [[{"LOWER": "is"}, {"LOWER": "this"}, {"POS": "ADJ"}]])

    # Pattern pour "Could this be + [noun]" questions
    syntax_matcher.add("COULD_THIS_BE", [
        [{"LOWER": "could"}, {"LOWER": "this"}, {"LOWER": "be"}, {"POS": "NOUN"}]
    ])

    # Pattern pour "What does + [noun] + mean" questions
    syntax_matcher.add("WHAT_DOES_MEAN", [
        [{"LOWER": "what"}, {"LOWER": "does"}, {"POS": "NOUN"}, {"LOWER": "mean"}]
    ])

    return {
        "second_opinion_matcher": second_opinion_matcher,
        "concern_matcher": concern_matcher,
        "medical_matcher": medical_matcher,
        "syntax_matcher": syntax_matcher
    }


# Initialiser les matchers
matchers = init_matchers()


# --- Initialisation de la base de données ---
def init_db():
    try:
        # Créer le dossier data s'il n'existe pas
        os.makedirs("data", exist_ok=True)

        with sqlite3.connect("data/phase2_data.db") as conn:
            cursor = conn.cursor()
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

            # Table pour les réponses (pour suivi des interactions)
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


# --- Classification avancée des posts ---
def is_gcc_country(country: str) -> bool:
    """
    Vérifie si le pays fait partie du GCC
    """
    gcc_countries = {
        # Arabie Saoudite
        'Saudi Arabia', 'Saudi', 'Arabie Saoudite', 'Arabie', 'KSA',
        # Émirats Arabes Unis
        'UAE', 'United Arab Emirates', 'Emirates', 'Dubai', 'Dubai UAE',
        'Abu Dhabi', 'Sharjah', 'Émirats Arabes Unis', 'EAU',
        # Qatar
        'Qatar', 'Doha', 'Qatar UAE',
        # Koweït
        'Kuwait', 'Koweït', 'Kuwait City',
        # Bahreïn
        'Bahrain', 'Bahreïn', 'Manama',
        # Oman
        'Oman', 'Muscat', 'Sultanate of Oman'
    }
    return country in gcc_countries if country else False


def extract_location(text: str) -> Dict[str, Any]:
    """
    Extrait les informations de localisation à partir du texte
    """
    doc = nlp(text)
    location_info = {
        'country': None,
        'city': None,
        'region': None,
        'latitude': None,
        'longitude': None
    }

    # Recherche des entités de type GPE (lieux)
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            text = ent.text.strip()
            # Si c'est une ville du GCC
            if text in ['Dubai', 'Abu Dhabi', 'Sharjah', 'Doha', 'Kuwait City', 'Manama', 'Muscat']:
                location_info['city'] = text
                # Déduire le pays
                if text == 'Dubai' or text == 'Abu Dhabi' or text == 'Sharjah':
                    location_info['country'] = 'UAE'
                elif text == 'Doha':
                    location_info['country'] = 'Qatar'
                elif text == 'Kuwait City':
                    location_info['country'] = 'Kuwait'
                elif text == 'Manama':
                    location_info['country'] = 'Bahrain'
                elif text == 'Muscat':
                    location_info['country'] = 'Oman'
            # Si c'est un pays du GCC
            elif is_gcc_country(text):
                location_info['country'] = text
                location_info['region'] = 'GCC'
            # Si c'est un pays africain
            elif is_african_country(text):
                location_info['country'] = text
                location_info['region'] = get_african_region(text)
            # Si c'est une région
            elif text in ['Gulf', 'Gulf Region', 'Middle East', 'Moyen-Orient',
                          'Afrique Centrale', 'Central Africa',
                          'Afrique de l\'Est', 'East Africa',
                          'Afrique de l\'Ouest', 'West Africa',
                          'Afrique du Sud', 'Southern Africa']:
                location_info['region'] = text

    return location_info


def analyze_post(title: str, body: str = "") -> Dict[str, Any]:
    """Analyse complète d'un post pour déterminer s'il s'agit d'une demande de second avis."""
    full_text = f"{title} {body}"

    # Analyser le texte avec SpaCy
    doc = nlp(full_text.lower())

    # Initialiser les scores
    scores = {
        "second_opinion_score": 0.0,
        "urgency_score": 0.0,
        "medical_relevance_score": 0.0,
        "sentiment_score": 0.0,
        "overall_score": 0.0,
        "category": "General"
    }

    # Analyse des correspondances de phrases
    second_opinion_matches = matchers["second_opinion_matcher"](doc)
    concern_matches = matchers["concern_matcher"](doc)
    medical_matches = matchers["medical_matcher"](doc)
    syntax_matches = matchers["syntax_matcher"](doc)

    # Calculer les scores basés sur les correspondances
    scores["second_opinion_score"] = min(1.0, len(second_opinion_matches) * 0.3)
    scores["urgency_score"] = min(1.0, len(concern_matches) * 0.2)
    scores["medical_relevance_score"] = min(1.0, len(medical_matches) * 0.1)

    # Bonus pour les structures syntaxiques spécifiques
    scores["second_opinion_score"] += min(0.5, len(syntax_matches) * 0.1)

    # Analyse de sentiment pour évaluer l'anxiété/urgence
    sentiment = TextBlob(full_text).sentiment
    # Inverser la polarité car un sentiment négatif indique souvent de l'inquiétude
    # dans un contexte médical
    scores["sentiment_score"] = max(0, -sentiment.polarity)

    # Calculer le score global
    weights = {
        "second_opinion": 0.4,
        "urgency": 0.3,
        "medical_relevance": 0.2,
        "sentiment": 0.1
    }

    scores["overall_score"] = (
            scores["second_opinion_score"] * weights["second_opinion"] +
            scores["urgency_score"] * weights["urgency"] +
            scores["medical_relevance_score"] * weights["medical_relevance"] +
            scores["sentiment_score"] * weights["sentiment"]
    )

    # Attribuer une catégorie basée sur le score global
    if scores["overall_score"] >= 0.7:
        scores["category"] = "High Priority - Second Opinion"
    elif scores["overall_score"] >= 0.5:
        scores["category"] = "Medium Priority - Second Opinion"
    elif scores["overall_score"] >= 0.3:
        scores["category"] = "Low Priority - Second Opinion"
    else:
        scores["category"] = "General Medical Question"

    # Extraction de la localisation
    location_info = extract_location(full_text)
    scores.update(location_info)

    return scores


# --- Scraping de Reddit avec analyse NLP avancée ---
def scrape_reddit(subreddit: str, query: str, limit: int = 100):
    try:
        subreddit_obj = reddit.subreddit(subreddit)
        posts_scraped = 0
        posts_analyzed = 0
        gcc_users_found = 0

        logger.info(f"Recherche de '{query}' dans r/{subreddit}, limite: {limit}")

        with sqlite3.connect("data/phase2_data.db") as conn:
            cursor = conn.cursor()

            for submission in subreddit_obj.search(query, limit=limit):
                # Récupérer le contenu du post (body)
                body = submission.selftext if hasattr(submission, 'selftext') else ""

                # Analyser le post avec SpaCy
                analysis = analyze_post(submission.title, body)

                # Insérer dans la table posts
                cursor.execute("""
                INSERT OR IGNORE INTO posts 
                (id, title, body, url, created_utc, subreddit, author, category, 
                second_opinion_score, urgency_score, medical_relevance_score, 
                sentiment_score, overall_score, country, city, region, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    submission.id,
                    submission.title,
                    body,
                    submission.url,
                    submission.created_utc,
                    str(submission.subreddit),
                    str(submission.author),
                    analysis["category"],
                    analysis["second_opinion_score"],
                    analysis["urgency_score"],
                    analysis["medical_relevance_score"],
                    analysis["sentiment_score"],
                    analysis["overall_score"],
                    analysis["country"],
                    analysis["city"],
                    analysis["region"],
                    analysis["latitude"],
                    analysis["longitude"]
                ))

                if cursor.rowcount > 0:
                    posts_scraped += 1

                    # Vérifier si l'utilisateur est du GCC
                    if is_gcc_country(analysis["country"]):
                        cursor.execute("""
                        INSERT INTO gcc_users 
                        (post_id, country, city, region, latitude, longitude, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            submission.id,
                            analysis["country"],
                            analysis["city"],
                            analysis["region"],
                            analysis["latitude"],
                            analysis["longitude"],
                            submission.created_utc
                        ))
                        gcc_users_found += 1
                        logger.info(
                            f"Utilisateur GCC détecté: {analysis['country']} - "
                            f"Ville: {analysis['city']} - "
                            f"Post: {submission.title[:50]}..."
                        )

                    logger.info(
                        f"Post enregistré: {submission.title[:50]}... "
                        f"Catégorie: {analysis['category']}, "
                        f"Score: {analysis['overall_score']:.2f}"
                    )
                posts_analyzed += 1

            conn.commit()
            logger.info(
                f"Scraping terminé: {posts_scraped} nouveaux posts sur {posts_analyzed} analysés, "
                f"{gcc_users_found} utilisateurs GCC détectés"
            )
            return posts_scraped
    except Exception as e:
        logger.error(f"Erreur lors du scraping: {e}")
        return 0


# --- Initialisation de l'agent conversationnel ---
conversational_agent = ConversationalAgent()


# --- Modèles Pydantic pour l'API ---
class PostResponse(BaseModel):
    id: str
    title: str
    url: str
    created_utc: float
    subreddit: str
    category: str
    second_opinion_score: float
    urgency_score: float
    medical_relevance_score: float
    sentiment_score: float
    overall_score: float
    body_excerpt: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ScrapingRequest(BaseModel):
    subreddit: str
    query: str
    limit: int = 100


class AnalysisRequest(BaseModel):
    title: str
    body: Optional[str] = ""


class ConversationRequest(BaseModel):
    post_id: str
    user_id: str
    message: str


class ConversationResponse(BaseModel):
    message: str
    response: str
    timestamp: float
    sentiment_score: float


# Création de l'application FastAPI
app = FastAPI(
    title="Medical Second Opinion API",
    description="API pour l'analyse des demandes de second avis médical",
    version="2.0.0"
)


@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur l'API TheKnowHow pour détection de besoins de second avis médical",
        "endpoints": [
            "/posts - Récupérer les posts analysés",
            "/analyze - Analyser un texte médical",
            "/scrape - Lancer une recherche sur Reddit",
            "/stats - Statistiques sur les données collectées",
            "/gcc_stats - Statistiques sur les utilisateurs GCC",
            "/conversation - Démarrer une nouvelle conversation",
            "/conversation/{post_id} - Récupérer l'historique d'une conversation"
        ]
    }


@app.get("/posts", response_model=List[PostResponse])
def get_posts(
        limit: int = Query(50, description="Nombre maximum de posts à récupérer"),
        min_score: float = Query(0.0, description="Score minimum pour filtrer les posts"),
        category: Optional[str] = Query(None, description="Filtrer par catégorie")
):
    try:
        with sqlite3.connect("data/phase2_data.db") as conn:
            cursor = conn.cursor()

            query = """
            SELECT id, title, body, url, created_utc, subreddit, author, category, 
                   second_opinion_score, urgency_score, medical_relevance_score, 
                   sentiment_score, overall_score, country, city, region, latitude, longitude
            FROM posts 
            WHERE overall_score >= ?
            """
            params = [min_score]

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " ORDER BY overall_score DESC, created_utc DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            posts = cursor.fetchall()

        if not posts:
            logger.warning(f"Aucun post trouvé avec les critères: score min={min_score}, catégorie={category}")
            return []

        result = []
        for p in posts:
            # Extraire un extrait du corps (si disponible)
            body_excerpt = p[2][:200] + "..." if p[2] and len(p[2]) > 200 else p[2]

            result.append({
                "id": p[0],
                "title": p[1],
                "url": p[3],
                "created_utc": p[4],
                "subreddit": p[5],
                "category": p[7],
                "second_opinion_score": p[8],
                "urgency_score": p[9],
                "medical_relevance_score": p[10],
                "sentiment_score": p[11],
                "overall_score": p[12],
                "body_excerpt": body_excerpt,
                "country": p[13],
                "city": p[14],
                "region": p[15],
                "latitude": p[16],
                "longitude": p[17]
            })

        return result
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération des posts: {e}")
        raise HTTPException(status_code=500, detail="Erreur de base de données")


@app.post("/scrape")
def scrape_endpoint(request: ScrapingRequest):
    try:
        posts_count = scrape_reddit(request.subreddit, request.query, request.limit)
        return {
            "message": f"{posts_count} nouveaux posts ont été récupérés et analysés",
            "subreddit": request.subreddit,
            "query": request.query
        }
    except Exception as e:
        logger.error(f"Erreur lors du scraping via l'API: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
def analyze_endpoint(request: AnalysisRequest):
    try:
        analysis = analyze_post(request.title, request.body)
        return {
            "title": request.title,
            "analysis": analysis,
            "recommendation": get_recommendation_based_on_score(analysis["overall_score"])
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de texte: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def get_stats():
    try:
        with sqlite3.connect("data/phase2_data.db") as conn:
            cursor = conn.cursor()

            # Nombre total de posts
            cursor.execute("SELECT COUNT(*) FROM posts")
            total_posts = cursor.fetchone()[0]

            # Répartition par catégories
            cursor.execute("SELECT category, COUNT(*) FROM posts GROUP BY category")
            categories = {cat: count for cat, count in cursor.fetchall()}

            # Score moyen
            cursor.execute("SELECT AVG(overall_score) FROM posts")
            avg_score = cursor.fetchone()[0]

            # Subreddits les plus intéressants
            cursor.execute("""
            SELECT subreddit, COUNT(*), AVG(overall_score) 
            FROM posts 
            GROUP BY subreddit 
            ORDER BY AVG(overall_score) DESC
            LIMIT 5
            """)
            top_subreddits = [
                {"subreddit": sr, "post_count": count, "avg_score": score}
                for sr, count, score in cursor.fetchall()
            ]

            return {
                "total_posts": total_posts,
                "categories": categories,
                "average_score": avg_score,
                "top_subreddits": top_subreddits
            }
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(status_code=500, detail="Erreur de base de données")


@app.get("/gcc_stats")
def get_gcc_stats():
    try:
        with sqlite3.connect("data/phase2_data.db") as conn:
            cursor = conn.cursor()

            # Nombre total d'utilisateurs GCC
            cursor.execute("SELECT COUNT(*) FROM gcc_users")
            total_gcc_users = cursor.fetchone()[0]

            # Répartition par pays
            cursor.execute("SELECT country, COUNT(*) FROM gcc_users GROUP BY country")
            countries = {country: count for country, count in cursor.fetchall()}

            # Répartition par ville
            cursor.execute("SELECT city, COUNT(*) FROM gcc_users WHERE city IS NOT NULL GROUP BY city")
            cities = {city: count for city, count in cursor.fetchall()}

            # Score moyen des posts des utilisateurs GCC
            cursor.execute("""
            SELECT AVG(p.overall_score) 
            FROM posts p 
            JOIN gcc_users g ON p.id = g.post_id
            """)
            avg_score = cursor.fetchone()[0]

            return {
                "total_gcc_users": total_gcc_users,
                "countries": countries,
                "cities": cities,
                "average_score": avg_score
            }
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération des statistiques GCC: {e}")
        raise HTTPException(status_code=500, detail="Erreur de base de données")


@app.post("/conversation", response_model=ConversationResponse)
def start_conversation(request: ConversationRequest):
    """Démarre une nouvelle conversation avec l'agent."""
    try:
        response = conversational_agent.generate_response(
            request.message,
            request.post_id,
            request.user_id
        )

        # Récupérer les détails de la conversation
        history = conversational_agent.get_conversation_history(request.post_id)
        if history:
            latest = history[-1]
            return ConversationResponse(
                message=latest["message"],
                response=latest["response"],
                timestamp=latest["timestamp"],
                sentiment_score=latest["sentiment_score"]
            )

        raise HTTPException(status_code=500, detail="Erreur lors de la génération de la réponse")
    except Exception as e:
        logger.error(f"Erreur lors de la conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{post_id}", response_model=List[ConversationResponse])
def get_conversation_history(post_id: str):
    """Récupère l'historique des conversations pour un post."""
    try:
        history = conversational_agent.get_conversation_history(post_id)
        return [
            ConversationResponse(
                message=h["message"],
                response=h["response"],
                timestamp=h["timestamp"],
                sentiment_score=h["sentiment_score"]
            )
            for h in history
        ]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Fonction auxiliaire pour les recommandations ---
def get_recommendation_based_on_score(score):
    if score >= 0.7:
        return {
            "action": "Contacter immédiatement",
            "priority": "Haute",
            "message": "Ce cas semble urgent et nécessite un deuxième avis médical rapidement. Nous recommandons de contacter TheKnowHow pour une consultation prioritaire."
        }
    elif score >= 0.5:
        return {
            "action": "Proposer nos services",
            "priority": "Moyenne",
            "message": "Cette personne pourrait bénéficier d'un deuxième avis médical. Nous recommandons de lui proposer les services de TheKnowHow."
        }
    elif score >= 0.3:
        return {
            "action": "Informer sur nos services",
            "priority": "Basse",
            "message": "Cette personne pourrait être intéressée par un deuxième avis médical. Nous recommandons de l'informer sur les services disponibles."
        }
    else:
        return {
            "action": "Aucune action requise",
            "priority": "Aucune",
            "message": "Ce cas ne semble pas nécessiter un deuxième avis médical pour le moment."
        }


class TextProcessor:
    """Classe pour le prétraitement des textes."""

    def __init__(self):
        """Initialise le processeur de texte avec le modèle SpaCy."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Erreur lors du chargement du modèle SpaCy: {e}")
            self.nlp = None

    def preprocess(self, text: str) -> str:
        """Prétraite le texte en entrée.

        Args:
            text (str): Texte à prétraiter

        Returns:
            str: Texte prétraité

        Raises:
            ValueError: Si le texte est vide ou None
            TypeError: Si le texte n'est pas une chaîne de caractères
        """
        if not text:
            raise ValueError("Le texte ne peut pas être vide")
        if not isinstance(text, str):
            raise TypeError("Le texte doit être une chaîne de caractères")

        # Conversion en minuscules
        text = text.lower()

        # Suppression de la ponctuation
        text = re.sub(r'[^\w\s]', ' ', text)

        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text)

        # Suppression des espaces au début et à la fin
        text = text.strip()

        return text


class SentimentAnalyzer:
    """Classe pour l'analyse de sentiment."""

    def analyze(self, text: str) -> Dict[str, float]:
        """Analyse le sentiment d'un texte.

        Args:
            text (str): Texte à analyser

        Returns:
            Dict[str, float]: Résultat de l'analyse avec polarité
        """
        # Implémentation simplifiée
        positive_words = {
            "bien", "bon", "excellent", "parfait", "merci", "mieux", "heureux",
            "content", "satisfait", "positif", "optimiste", "guéri", "sain"
        }
        negative_words = {
            "mal", "inquiet", "stressé", "problème", "douleur", "souffrance",
            "anxieux", "négatif", "pessimiste", "malade", "fatigué", "inquiétude"
        }

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        total = positive_count + negative_count
        if total == 0:
            return {"polarity": 0.0}

        polarity = (positive_count - negative_count) / total
        return {"polarity": polarity}


class EntityExtractor:
    def __init__(self):
        self.locations = [
            "Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain",
            "Émirats Arabes Unis", "UAE", "United Arab Emirates"
        ]
        self.dates = {
            "aujourd'hui", "demain", "hier", "semaine", "mois", "année",
            "matin", "soir", "midi", "nuit", "jour", "heure"
        }
        self.duration_pattern = re.compile(r'\d+\s+(semaine|mois|année|jour|heure|minute|seconde)s?')
        self.symptoms = [
            "symptoms", "diagnosis", "treatment", "medication", "doctor",
            "hospital", "clinic", "surgery", "medical", "health", "disease",
            "condition", "illness", "specialist", "prescription", "therapy",
            "pain", "chronic", "acute", "diagnosis"
        ]

    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extrait les entités du texte."""
        entities = {
            "locations": [],
            "dates": [],
            "symptoms": []
        }

        # Extraire les locations
        for location in self.locations:
            if location.lower() in text.lower():
                entities["locations"].append(location)

        # Extraire les dates
        for date in self.dates:
            if date.lower() in text.lower():
                entities["dates"].append(date)

        # Extraire les symptômes
        for symptom in self.symptoms:
            if symptom.lower() in text.lower():
                entities["symptoms"].append(symptom)

        return entities


class LanguageDetector:
    def __init__(self):
        self.french_words = {
            "bonjour", "merci", "s'il", "vous", "plait", "oui", "non", "je", "tu", "il", "elle",
            "nous", "vous", "ils", "elles", "être", "avoir", "faire", "aller", "venir", "pouvoir",
            "vouloir", "devoir", "savoir", "voir", "entendre", "parler", "manger", "boire", "dormir",
            "travailler", "étudier", "apprendre", "comprendre", "penser", "croire", "aimer", "détester",
            "grand", "petit", "beau", "laid", "bon", "mauvais", "nouveau", "vieux", "jeune", "vieux",
            "chaud", "froid", "heureux", "triste", "fatigué", "malade", "en", "dans", "sur", "sous",
            "devant", "derrière", "avec", "sans", "pour", "contre", "et", "ou", "mais", "donc", "car",
            "parce", "que", "si", "quand", "comment", "pourquoi", "où", "qui", "quoi", "combien"
        }
        self.english_words = {
            "hello", "thank", "you", "please", "yes", "no", "i", "you", "he", "she", "it", "we",
            "they", "am", "is", "are", "was", "were", "have", "has", "had", "do", "does", "did",
            "can", "could", "will", "would", "shall", "should", "may", "might", "must", "need",
            "want", "like", "love", "hate", "big", "small", "good", "bad", "new", "oldddddddddddddddddddddddddddddddddd", "young",
            "hot", "cold", "happy", "sad", "tired", "sick", "in", "on", "at", "under", "over",
            "before", "after", "with", "without", "for", "against", "and", "or", "but", "so",
            "because", "if", "when", "how", "why", "where", "who", "what", "how", "many"
        }
        self.arabic_pattern = re.compile(r'[\u0600-\u06FF]')

    def detect(self, text):
        """Détecte la langue du texte"""
        if not text or not isinstance(text, str):
            return "unknown"

        # Vérifier si le texte contient des caractères arabes
        if self.arabic_pattern.search(text):
            return "ar"

        text = text.lower()
        words = set(text.split())

        french_count = len(words.intersection(self.french_words))
        english_count = len(words.intersection(self.english_words))

        if french_count > english_count:
            return "fr"
        elif english_count > french_count:
            return "en"
        else:
            return "unknown"


@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'API."""
    return {"status": "healthy", "message": "Le serveur fonctionne correctement"}


def is_african_country(country: str) -> bool:
    """Vérifie si le pays fait partie de l'Afrique."""
    african_countries = {
        # Afrique Centrale
        'Cameroun', 'Cameroon', 'République centrafricaine', 'Central African Republic',
        'Tchad', 'Chad', 'Congo', 'République démocratique du Congo', 'DR Congo', 'DRC',
        'Guinée équatoriale', 'Equatorial Guinea', 'Gabon', 'São Tomé et Príncipe',
        'Sao Tome and Principe',

        # Afrique de l'Est
        'Burundi', 'Comores', 'Comoros', 'Djibouti', 'Érythrée', 'Eritrea', 'Éthiopie',
        'Ethiopia', 'Kenya', 'Madagascar', 'Malawi', 'Maurice', 'Mauritius', 'Mozambique',
        'Rwanda', 'Seychelles', 'Somalie', 'Somalia', 'Soudan du Sud', 'South Sudan',
        'Tanzanie', 'Tanzania', 'Ouganda', 'Uganda',

        # Afrique de l'Ouest
        'Bénin', 'Benin', 'Burkina Faso', 'Cap-Vert', 'Cape Verde', 'Côte d\'Ivoire',
        'Ivory Coast', 'Gambie', 'Gambia', 'Ghana', 'Guinée', 'Guinea', 'Guinée-Bissau',
        'Guinea-Bissau', 'Libéria', 'Liberia', 'Mali', 'Mauritanie', 'Mauritania',
        'Niger', 'Nigeria', 'Sénégal', 'Senegal', 'Sierra Leone', 'Togo',

        # Afrique du Sud
        'Afrique du Sud', 'South Africa', 'Angola', 'Botswana', 'Lesotho', 'Namibie',
        'Namibia', 'Eswatini', 'Swaziland', 'Zambie', 'Zambia', 'Zimbabwe'
    }
    return country in african_countries if country else False


def get_african_region(country: str) -> str:
    """Détermine la région africaine d'un pays."""
    central_africa = {
        'Cameroun', 'Cameroon', 'République centrafricaine', 'Central African Republic',
        'Tchad', 'Chad', 'Congo', 'République démocratique du Congo', 'DR Congo', 'DRC',
        'Guinée équatoriale', 'Equatorial Guinea', 'Gabon', 'São Tomé et Príncipe',
        'Sao Tome and Principe'
    }

    east_africa = {
        'Burundi', 'Comores', 'Comoros', 'Djibouti', 'Érythrée', 'Eritrea', 'Éthiopie',
        'Ethiopia', 'Kenya', 'Madagascar', 'Malawi', 'Maurice', 'Mauritius', 'Mozambique',
        'Rwanda', 'Seychelles', 'Somalie', 'Somalia', 'Soudan du Sud', 'South Sudan',
        'Tanzanie', 'Tanzania', 'Ouganda', 'Uganda'
    }

    west_africa = {
        'Bénin', 'Benin', 'Burkina Faso', 'Cap-Vert', 'Cape Verde', 'Côte d\'Ivoire',
        'Ivory Coast', 'Gambie', 'Gambia', 'Ghana', 'Guinée', 'Guinea', 'Guinée-Bissau',
        'Guinea-Bissau', 'Libéria', 'Liberia', 'Mali', 'Mauritanie', 'Mauritania',
        'Niger', 'Nigeria', 'Sénégal', 'Senegal', 'Sierra Leone', 'Togo'
    }

    south_africa = {
        'Afrique du Sud', 'South Africa', 'Angola', 'Botswana', 'Lesotho', 'Namibie',
        'Namibia', 'Eswatini', 'Swaziland', 'Zambie', 'Zambia', 'Zimbabwe'
    }

    if country in central_africa:
        return "Afrique Centrale"
    elif country in east_africa:
        return "Afrique de l'Est"
    elif country in west_africa:
        return "Afrique de l'Ouest"
    elif country in south_africa:
        return "Afrique du Sud"
    else:
        return "Autre"


@app.get("/african_stats")
def get_african_stats():
    """Récupère les statistiques pour les utilisateurs africains."""
    try:
        with sqlite3.connect("data/phase2_data.db") as conn:
            cursor = conn.cursor()

            # Sélectionner tous les posts avec un pays
            cursor.execute("SELECT DISTINCT country FROM posts WHERE country IS NOT NULL")
            all_countries = cursor.fetchall()

            # Filtrer les pays africains et compter par région
            stats = {
                "Afrique Centrale": {"count": 0, "countries": set(), "posts": []},
                "Afrique de l'Est": {"count": 0, "countries": set(), "posts": []},
                "Afrique de l'Ouest": {"count": 0, "countries": set(), "posts": []},
                "Afrique du Sud": {"count": 0, "countries": set(), "posts": []}
            }

            for (country,) in all_countries:
                if is_african_country(country):
                    region = get_african_region(country)
                    if region in stats:
                        # Récupérer les posts pour ce pays
                        cursor.execute("""
                        SELECT title, category, overall_score 
                        FROM posts 
                        WHERE country = ?
                        ORDER BY overall_score DESC
                        LIMIT 5
                        """, (country,))
                        posts = cursor.fetchall()

                        stats[region]["count"] += 1
                        stats[region]["countries"].add(country)
                        stats[region]["posts"].extend([{
                            "title": p[0],
                            "category": p[1],
                            "score": p[2]
                        } for p in posts])

            # Convertir les sets en listes pour la sérialisation JSON
            for region in stats:
                stats[region]["countries"] = list(stats[region]["countries"])

            # Ajouter des statistiques globales
            total_african_countries = sum(len(r["countries"]) for r in stats.values())
            total_african_posts = sum(len(r["posts"]) for r in stats.values())

            return {
                "total_african_countries": total_african_countries,
                "total_african_posts": total_african_posts,
                "regions": stats
            }

    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération des statistiques africaines: {e}")
        raise HTTPException(status_code=500, detail="Erreur de base de données")


if __name__ == "__main__":
    # Initialisation de la base de données
    init_db()

    # Scraping initial des subreddits médicaux populaires
    subreddits = ["AskDocs", "DiagnoseMe", "medical", "AskDoctorSmeeee", "Health"]
    queries = [
        "second opinion", "need doctor", "medical advice",
        "diagnosis help", "worried about health", "medical question"
    ]

    try:
        for subreddit in subreddits:
            for query in queries:
                scrape_reddit(subreddit, query, 50)
    except Exception as e:
        logger.error(f"Erreur lors du scraping initial: {e}")

    # Lancement du serveur
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8002)