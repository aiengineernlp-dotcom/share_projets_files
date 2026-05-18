import time
from typing import List, Dict, Any
from textblob import TextBlob

class ConversationalAgent:
    def __init__(self):
        """Initialise l'agent conversationnel."""
        self.conversations = {}  # stockage des conversations par post_id
        
    def generate_response(self, message: str, post_id: str, user_id: str) -> str:
        """Génère une réponse basée sur le message de l'utilisateur."""
        # Analyse simple du sentiment
        sentiment = TextBlob(message).sentiment.polarity
        
        # Stockage de l'interaction
        if post_id not in self.conversations:
            self.conversations[post_id] = []
            
        # Création d'une réponse simple
        response = self._get_basic_response(message, sentiment)
        
        # Enregistrement de l'interaction
        self.conversations[post_id].append({
            "message": message,
            "response": response,
            "user_id": user_id,
            "timestamp": time.time(),
            "sentiment_score": sentiment
        })
        
        return response
        
    def get_conversation_history(self, post_id: str) -> List[Dict[str, Any]]:
        """Récupère l'historique des conversations pour un post donné."""
        return self.conversations.get(post_id, [])
        
    def _get_basic_response(self, message: str, sentiment: float) -> str:
        """Génère une réponse basique basée sur le message et le sentiment."""
        message = message.lower()
        
        # Réponses pour les salutations
        if any(word in message for word in ["bonjour", "salut", "hello", "hi"]):
            return "Bonjour ! Je suis l'assistant médical de TheKnowHow. Comment puis-je vous aider ?"
            
        # Réponses pour les symptômes
        if any(word in message for word in ["mal", "douleur", "symptôme", "souffre"]):
            return "Je comprends votre inquiétude. Pouvez-vous me donner plus de détails sur vos symptômes ?"
            
        # Réponses pour les questions sur les services
        if any(word in message for word in ["service", "consultation", "rendez-vous", "prix"]):
            return "Nous offrons des consultations médicales avec des spécialistes qualifiés. Souhaitez-vous plus d'informations sur nos services ?"
            
        # Réponse par défaut
        if sentiment < -0.2:
            return "Je comprends votre préoccupation. Comment puis-je vous aider plus spécifiquement ?"
        elif sentiment > 0.2:
            return "Je suis ravi de pouvoir vous aider. Que souhaitez-vous savoir d'autre ?"
        else:
            return "Pouvez-vous me donner plus de détails pour mieux vous aider ?" 