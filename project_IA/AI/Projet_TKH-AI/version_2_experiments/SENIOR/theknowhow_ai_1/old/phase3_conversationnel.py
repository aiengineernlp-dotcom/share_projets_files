"""Module de gestion des conversations médicales pour TheKnowHow.ae.

Ce module implémente un agent conversationnel spécialisé dans le domaine médical,
capable de gérer des conversations multilingues et de fournir des réponses contextuelles
adaptées aux besoins des utilisateurs.

Classes principales:
    - DatabaseManager: Gestion de la persistance des données
    - TranslationManager: Gestion des traductions multilingues
    - MedicalAgent: Agent conversationnel médical
    - Message: Modèle de données pour les messages
    - Conversation: Modèle de données pour les conversations
    - Response: Modèle de données pour les réponses

Fonctionnalités principales:
    - Analyse de sentiment des messages
    - Support multilingue (FR, EN, AR)
    - Gestion du contexte des conversations
    - Intégration avec GPT pour la génération de réponses
    - Persistance des données dans SQLite
    - API REST et WebSocket pour l'interaction

Dépendances:
    - fastapi: Framework web
    - openai: Client OpenAI pour GPT
    - spacy: Traitement du langage naturel
    - deep_translator: Traduction de texte
    - textblob: Analyse de sentiment
    - langdetect: Détection de langue
"""

import os
import logging
import sqlite3
import uuid
import spacy
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any, Literal
from deep_translator import GoogleTranslator
from openai import AsyncOpenAI
from langdetect import detect, detect_langs
from dotenv import load_dotenv
from textblob import TextBlob
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration OpenAI et Traduction
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("La clé API OpenAI n'est pas configurée dans le fichier .env")

# --- Modèles de données ---
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=4000)

class Conversation(BaseModel):
    messages: List[Message]
    user_id: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None

    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v: List[Message]) -> List[Message]:
        if not v:
            raise ValueError("La conversation doit contenir au moins un message")
        return v

class Response(BaseModel):
    message: str
    action: Optional[Literal["Contacter immédiatement", "Proposer nos services", "Informer sur nos services"]] = None
    priority: Optional[Literal["Haute", "Moyenne", "Basse"]] = None
    sentiment_score: Optional[float] = None

class DatabaseManager:
    """Gestionnaire de base de données pour la persistance des conversations.
    
    Cette classe gère toutes les opérations de base de données pour le stockage
    et la récupération des conversations, messages et contextes utilisateur.
    
    Attributes:
        db_path (str): Chemin vers le fichier de base de données SQLite.
    """
    
    def __init__(self, db_path="medical_agent.db"):
        """Initialise le gestionnaire de base de données.
        
        Args:
            db_path (str): Chemin vers le fichier de base de données.
        """
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Crée les tables nécessaires dans la base de données si elles n'existent pas.
        
        Tables créées:
            - posts: Stockage des posts et leurs métadonnées
            - conversations: Gestion des conversations utilisateur
            - chat_messages: Stockage des messages individuels
            - gcc_users: Informations sur les utilisateurs GCC
            - users: Profils utilisateurs
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Supprimer les tables existantes pour éviter les conflits
            cursor.execute("DROP TABLE IF EXISTS chat_messages")
            cursor.execute("DROP TABLE IF EXISTS conversations")
            cursor.execute("DROP TABLE IF EXISTS gcc_users")
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS posts")
            
            # Table des posts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    author TEXT NOT NULL,
                    category TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    created_utc DATETIME NOT NULL,
                    title TEXT,
                    body TEXT,
                    country TEXT,
                    city TEXT
                )
            """)
            
            # Table des conversations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    last_message_at DATETIME NOT NULL,
                    status TEXT NOT NULL,
                    sentiment_score REAL,
                    post_id INTEGER,
                    FOREIGN KEY (post_id) REFERENCES posts(id)
                )
            """)
            
            # Table des messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    sentiment_score REAL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            
            # Table des utilisateurs GCC
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gcc_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER NOT NULL,
                    country TEXT NOT NULL,
                    city TEXT NOT NULL,
                    FOREIGN KEY (post_id) REFERENCES posts(id)
                )
            """)
            
            # Table des utilisateurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    created_at DATETIME NOT NULL,
                    last_active DATETIME NOT NULL
                )
            """)
            
            # Insérer des données de test
            cursor.execute("""
                INSERT OR IGNORE INTO posts (id, author, category, overall_score, created_utc, title, body, country, city)
                VALUES 
                (1, 'test_user', 'High Priority', 0.8, datetime('now'), 'Urgent medical question', 'I need a second opinion', 'UAE', 'Dubai'),
                (2, 'test_user2', 'General', 0.3, datetime('now'), 'General question', 'Just asking about symptoms', 'France', 'Paris')
            """)
            
            conn.commit()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def save_message(self, conversation_id: str, role: str, content: str, sentiment_score: float = 0.0):
        """Sauvegarde un message dans la base de données.
        
        Args:
            conversation_id (str): ID de la conversation
            role (str): Rôle du message ('user' ou 'assistant')
            content (str): Contenu du message
            sentiment_score (float): Score de sentiment du message (-1 à 1)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO chat_messages (conversation_id, role, content, created_at, sentiment_score) VALUES (?, ?, ?, datetime('now'), ?)",
                    (conversation_id, role, content, sentiment_score)
                )
                cursor.execute(
                    "UPDATE conversations SET last_message_at = datetime('now') WHERE id = ?",
                    (conversation_id,)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la sauvegarde du message : {e}")

    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Récupérer le contexte d'un utilisateur"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT g.country, g.city, p.category, p.overall_score, p.title, p.body
                FROM gcc_users g
                JOIN posts p ON g.post_id = p.id
                WHERE p.author = ?
                ORDER BY p.created_utc DESC
                LIMIT 1
                """, (user_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        "country": result[0],
                        "city": result[1],
                        "category": result[2],
                        "score": result[3],
                        "title": result[4],
                        "body": result[5]
                    }
                return {}
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération du contexte : {e}")
            return {}

    def get_conversation_history(self, conversation_id):
        """Récupère l'historique des messages d'une conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT created_at, role, content, sentiment_score
                FROM chat_messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
            """, (conversation_id,))
            return cursor.fetchall()

    def get_post_context(self, post_id: str) -> Dict:
        """Récupère le contexte du post depuis la base de données."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT title, body, category, overall_score, country, city
                FROM posts
                WHERE id = ?
                """, (post_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        "title": result[0],
                        "body": result[1],
                        "category": result[2],
                        "overall_score": result[3],
                        "country": result[4],
                        "city": result[5]
                    }
                return {}
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération du contexte: {e}")
            return {}

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Récupère un utilisateur par son ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                return {
                    "id": user[0],
                    "created_at": user[1],
                    "last_active": user[2]
                }
            return None

    def create_user(self, user_id: str):
        """Crée un nouvel utilisateur."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO users (id, created_at, last_active) VALUES (?, ?, ?)",
                (user_id, now, now)
            )
            conn.commit()

    def update_user_last_active(self, user_id: str):
        """Met à jour le dernier temps d'activité d'un utilisateur."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute(
                    "UPDATE users SET last_active = ? WHERE id = ?",
                    (now, user_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la mise à jour du dernier temps d'activité : {e}")

class TranslationManager:
    """Gestionnaire de traductions multilingues.
    
    Cette classe gère la détection de langue et la traduction des messages
    entre différentes langues supportées (FR, EN, AR).
    
    Attributes:
        language_detector (LanguageDetector): Instance pour la détection de langue
        translators (dict): Cache des traducteurs par langue
    """
    
    def __init__(self):
        """Initialise le gestionnaire de traductions."""
        self.language_detector = LanguageDetector()
        self.translators = {}

    def detect_language(self, text: str) -> str:
        """Détecte la langue du texte.
        
        Args:
            text (str): Texte à analyser
            
        Returns:
            str: Code de langue détecté ('fr', 'en', ou 'ar')
        """
        """Détecte la langue du texte."""
        return self.language_detector.detect(text)

    def translate_text(self, text: str, target_lang: str) -> str:
        """Traduit le texte dans la langue cible."""
        try:
            if target_lang not in self.translators:
                self.translators[target_lang] = GoogleTranslator(source='auto', target=target_lang)
            return self.translators[target_lang].translate(text)
        except Exception as e:
            logger.error(f"Erreur de traduction : {e}")
            return text

class UserProfile:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.language = "en"
        self.medical_interests = []
        self.conversation_history = []
        self.engagement_score = 0

class LanguageDetector:
    """Détecteur de langue utilisant langdetect."""
    
    def __init__(self):
        self.detector = detect_langs
    
    def detect(self, text: str) -> str:
        """Détecte la langue du texte."""
        try:
            # Détecter la langue
            lang = detect(text)
            
            # Mapping des codes de langue
            lang_mapping = {
                'fr': 'fr',
                'en': 'en',
                'ar': 'ar'
            }
            
            # Si la langue détectée est le français, on la garde
            if lang == 'fr':
                return 'fr'
            
            # Sinon, on retourne l'anglais
            return 'en'
        except Exception as e:
            logger.error(f"Erreur de détection de langue : {e}")
            return 'en'  # Par défaut en anglais

class MockOpenAI:
    """Classe pour simuler les réponses d'OpenAI."""
    async def chat(self, completions):
        class MockResponse:
            def __init__(self, content):
                self.choices = [type('obj', (object,), {'message': type('obj', (object,), {'content': content})})]
        return MockResponse(self._get_mock_response(completions['messages'][1]['content']))

    def _get_mock_response(self, message: str) -> str:
        """Génère une réponse simulée basée sur le message."""
        message = message.lower()
        
        # Réponses en français
        if "bonjour" in message or "salut" in message:
            return "Bonjour ! Je suis votre assistant médical. Comment puis-je vous aider aujourd'hui ?"
        elif "mal à la tête" in message or "céphalée" in message:
            return "Je comprends que vous souffrez de maux de tête. Voici quelques conseils :\n1. Reposez-vous dans un endroit calme\n2. Buvez beaucoup d'eau\n3. Évitez les écrans\nSi les symptômes persistent, consultez un médecin."
        elif "fièvre" in message:
            return "La fièvre peut être le signe d'une infection. Je vous conseille de :\n1. Prendre votre température\n2. Boire beaucoup d'eau\n3. Reposer\nSi la fièvre dépasse 39°C, consultez un médecin."
        
        # Réponses en anglais
        elif "hello" in message or "hi" in message:
            return "Hello! I'm your medical assistant. How can I help you today?"
        elif "headache" in message:
            return "I understand you're suffering from a headache. Here are some tips:\n1. Rest in a quiet place\n2. Drink plenty of water\n3. Avoid screens\nIf symptoms persist, consult a doctor."
        elif "fever" in message:
            return "Fever can be a sign of infection. I recommend:\n1. Taking your temperature\n2. Drinking plenty of water\n3. Resting\nIf fever exceeds 39°C, consult a doctor."
        
        # Réponse par défaut
        return "Je comprends votre préoccupation. Pourriez-vous me donner plus de détails sur vos symptômes ?"

class ConversationManager:
    # openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)  # Commenté pour utiliser le mock
    openai_client = MockOpenAI()  # Utilisation du mock
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.translation_manager = TranslationManager()
        self.language_detector = LanguageDetector()
        self.user_profiles = {}
        self.conversation_db = {}
        self.max_conversation_history = 10
        
        # Charger les modèles SpaCy
        try:
            self.nlp_en = spacy.load("en_core_web_sm")
            self.nlp_fr = spacy.load("fr_core_news_sm")
            logger.info("Modèles SpaCy anglais et français chargés avec succès")
            
            # Tentative de chargement du modèle arabe
            try:
                self.nlp_ar = spacy.load("ar_core_web_sm")
                logger.info("Modèle SpaCy arabe chargé avec succès")
            except OSError:
                logger.warning("Modèle SpaCy arabe non disponible, utilisation du modèle anglais")
                self.nlp_ar = self.nlp_en
        except Exception as e:
            logger.error(f"Erreur lors du chargement des modèles SpaCy: {e}")
            raise

    def analyze_sentiment(self, text: str) -> float:
        """Analyse le sentiment du texte."""
        try:
            # Créer un objet TextBlob
            blob = TextBlob(text)
            
            # Obtenir le score de sentiment (-1 à 1)
            score = blob.sentiment.polarity
            
            # Ajuster le score pour les messages en français
            text_lower = text.lower()
            
            # Mots positifs
            if any(word in text_lower for word in ["merci", "bien", "mieux", "bon", "bonne"]):
                score = max(score, 0.1)
            
            # Mots négatifs
            if any(word in text_lower for word in ["inquiet", "inquiète", "inquiétude", "mal", "douleur", "souffre"]):
                score = min(score, -0.1)
            
            return score
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de sentiment : {e}")
            return 0.0

    async def generate_response(self, message: str, post_id: str, user_id: str, language: str = "fr") -> Response:
        """Génère une réponse appropriée au message."""
        # Analyser le sentiment du message
        sentiment_score = self.analyze_sentiment(message)
        
        # Récupérer le contexte du post
        post_context = self.db_manager.get_post_context(post_id)
        
        # Déterminer la priorité
        priority = self._determine_priority(post_context, sentiment_score)
        
        # Générer la réponse avec GPT
        response_text = await self._generate_gpt_response(message, post_context, language)
        
        # Sauvegarder la conversation
        self._save_conversation(post_id, user_id, message, response_text, sentiment_score)
        
        return Response(
            message=response_text,
            priority=priority,
            sentiment_score=sentiment_score
        )

    def _determine_priority(self, context: Dict, sentiment_score: float) -> str:
        """Détermine la priorité de la réponse."""
        overall_score = context.get("overall_score", 0)
        
        if overall_score >= 0.7 or sentiment_score <= -0.5:
            return "Haute"
        elif overall_score >= 0.5 or sentiment_score <= -0.2:
            return "Moyenne"
        return "Basse"

    async def _generate_gpt_response(self, message: str, context: Dict, language: str) -> str:
        """Génère une réponse avec GPT."""
        try:
            prompt = self._build_prompt(message, context, language)
            response = await self.openai_client.chat(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(language)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la réponse GPT: {e}")
            if "OpenAI" in str(e):
                raise Exception("OpenAI Error")
            return self._get_fallback_response(context, language)

    def _save_conversation(self, post_id: str, user_id: str, message: str, 
                          response: str, sentiment_score: float):
        """Sauvegarde la conversation dans la base de données."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                # Créer une nouvelle conversation si nécessaire
                cursor.execute("""
                INSERT OR IGNORE INTO conversations 
                (user_id, created_at, last_message_at, status, sentiment_score)
                VALUES (?, datetime('now'), datetime('now'), 'active', ?)
                """, (user_id, sentiment_score))
                
                conversation_id = cursor.lastrowid
                
                # Sauvegarder le message de l'utilisateur
                cursor.execute("""
                INSERT INTO chat_messages 
                (conversation_id, role, content, created_at, sentiment_score)
                VALUES (?, 'user', ?, datetime('now'), ?)
                """, (conversation_id, message, sentiment_score))
                
                # Sauvegarder la réponse
                cursor.execute("""
                INSERT INTO chat_messages 
                (conversation_id, role, content, created_at, sentiment_score)
                VALUES (?, 'assistant', ?, datetime('now'), 0.0)
                """, (conversation_id, response))
                
                conn.commit()
                logger.info(f"Conversation sauvegardée pour le post {post_id}")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la sauvegarde de la conversation: {e}")

    def _build_prompt(self, message: str, context: Dict, language: str) -> str:
        """Construit le prompt pour GPT."""
        prompt = f"Contexte du post :\n"
        prompt += f"Catégorie : {context.get('category', 'Non spécifiée')}\n"
        prompt += f"Pays : {context.get('country', 'Non spécifié')}\n"
        prompt += f"Ville : {context.get('city', 'Non spécifiée')}\n"
        prompt += f"Contenu : {context.get('body', 'Non spécifié')}\n\n"
        prompt += f"Message de l'utilisateur : {message}\n\n"
        prompt += "Veuillez fournir une réponse appropriée en tenant compte du contexte."
        return prompt

    def _get_fallback_response(self, context: Dict, language: str) -> str:
        """Retourne une réponse par défaut en cas d'erreur."""
        if language == "fr":
            return "Je m'excuse, mais je rencontre des difficultés techniques. Veuillez réessayer dans quelques instants."
        elif language == "en":
            return "I apologize, but I'm experiencing technical difficulties. Please try again in a few moments."
        else:  # ar
            return "عذراً، لكنني أواجه صعوبات تقنية. يرجى المحاولة مرة أخرى بعد قليل."

    def get_or_create_user_profile(self, user_id: str) -> Dict:
        """Récupère ou crée un profil utilisateur."""
        try:
            # Vérifier si l'utilisateur existe
            user = self.db_manager.get_user(user_id)
            if user:
                return user
            
            # Créer un nouveau profil
            self.db_manager.create_user(user_id)
            return self.db_manager.get_user(user_id)
        except Exception as e:
            logger.error(f"Erreur lors de la gestion du profil utilisateur : {e}")
            return {"id": user_id, "created_at": datetime.now()}

    def update_user_profile(self, user_id: str):
        """Met à jour le profil utilisateur avec la dernière activité."""
        try:
            self.db_manager.update_user_last_active(user_id)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du profil utilisateur : {e}")

    def _get_system_prompt(self, language: str) -> str:
        """Retourne le prompt système selon la langue."""
        prompts = {
            "fr": """Vous êtes un assistant médical professionnel de TheKnowHow.ae.
            Votre rôle est de fournir des informations médicales précises et utiles,
            tout en restant dans les limites de votre expertise.
            Soyez empathique et rassurant dans vos réponses.""",
            
            "en": """You are a professional medical assistant for TheKnowHow.ae.
            Your role is to provide accurate and useful medical information,
            while staying within the limits of your expertise.
            Be empathetic and reassuring in your responses.""",
            
            "ar": """أنت مساعد طبي محترف في TheKnowHow.ae.
            دورك هو تقديم معلومات طبية دقيقة ومفيدة،
            مع البقاء ضمن حدود خبرتك.
            كن متعاطفاً ومطمئناً في ردودك."""
        }
        return prompts.get(language, prompts["en"])

# Configuration FastAPI
app = FastAPI(title="TheKnowHow Medical Conversational Agent")
conversation_manager = ConversationManager()

@app.post("/chat")
async def chat(request: Request):
    """Endpoint pour le chat."""
    try:
        data = await request.json()
        messages = data.get("messages", [])
        user_id = data.get("user_id")
        context = data.get("context", {})
        
        if not messages:
            raise HTTPException(status_code=400, detail="La liste des messages ne peut pas être vide")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="L'ID utilisateur est requis")
        
        # Vérifier le contenu du message
        if not messages[-1].get("content"):
            raise HTTPException(status_code=400, detail="Le contenu du message ne peut pas être vide")
        
        # Obtenir ou créer le profil utilisateur
        user_profile = conversation_manager.get_or_create_user_profile(user_id)
        
        # Mettre à jour le profil
        conversation_manager.update_user_profile(user_id)
        
        # Détecter la langue
        language = conversation_manager.translation_manager.detect_language(messages[-1]["content"])
        
        # Générer la réponse
        response = await conversation_manager.generate_response(
            messages[-1]["content"],
            context.get("post_id"),
            user_id,
            language
        )
        
        return {"response": response.message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la conversation: {e}")
        error_message = str(e)
        if "OpenAI" in error_message:
            raise HTTPException(
                status_code=500,
                detail="Une erreur est survenue lors de la communication avec OpenAI. Veuillez réessayer plus tard."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Une erreur est survenue lors du traitement de votre demande: {error_message}"
        )

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket pour le chat en temps réel."""
    await websocket.accept()
    try:
        while True:
            # Recevoir le message
            message = await websocket.receive_text()
            
            # Créer un contexte de message
            message_data = {
                "messages": [{"role": "user", "content": message}],
                "user_id": "anonymous",
                "context": {}
            }
            
            # Détecter la langue
            language = conversation_manager.translation_manager.detect_language(message)
            
            # Générer la réponse
            response = await conversation_manager.generate_response(
                message,
                None,  # Pas de post_id pour les messages simples
                "anonymous",
                language
            )
            
            # Envoyer la réponse en JSON
            await websocket.send_json({"response": response.message})
            
    except WebSocketDisconnect:
        logger.info("Client WebSocket déconnecté")
    except Exception as e:
        logger.error(f"Erreur WebSocket : {e}")
        try:
            await websocket.send_json({
                "error": "Une erreur est survenue lors du traitement de votre demande."
            })
        except:
            pass



