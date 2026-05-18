"""Version hybride de l'agent conversationnel médical combinant base de données et OpenAI."""

from phase3_conversationnel import ConversationManager, Response
from typing import Dict, Optional
import asyncio
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
import uvicorn
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import sqlite3
import json

class HybridConversationManager(ConversationManager):
    """Version hybride du ConversationManager utilisant la base de données et OpenAI."""
    
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db_path = "medical_agent.db"
        self._init_db()
    
    def _init_db(self):
        """Initialise la base de données avec les réponses prédéfinies."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Création de la table des réponses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                language TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertion des réponses prédéfinies
        predefined_responses = [
            # Français - Symptômes courants
            ("mal à la tête", "Je comprends que vous souffrez de maux de tête. Voici quelques conseils :\n1. Reposez-vous dans un endroit calme\n2. Buvez beaucoup d'eau\n3. Évitez les écrans\nSi les symptômes persistent, consultez un médecin.", "fr", "céphalée"),
            ("fièvre", "La fièvre peut être le signe d'une infection. Je vous conseille de :\n1. Prendre votre température\n2. Buvez beaucoup d'eau\n3. Reposer\nSi la fièvre dépasse 39°C, consultez un médecin.", "fr", "fièvre"),
            ("douleur", "Je comprends que vous avez des douleurs. Pourriez-vous me préciser :\n1. La localisation exacte\n2. L'intensité\n3. La durée\nCela m'aidera à mieux vous conseiller.", "fr", "douleur"),
            ("toux", "La toux peut être le signe d'une infection respiratoire. Je vous conseille de :\n1. Boire beaucoup d'eau\n2. Utiliser un humidificateur\n3. Éviter les irritants (tabac, parfums)\nSi la toux persiste plus de 3 semaines, consultez un médecin.", "fr", "toux"),
            ("mal de gorge", "Pour le mal de gorge, voici quelques conseils :\n1. Gargariser avec de l'eau salée\n2. Boire des boissons chaudes\n3. Reposer la voix\nSi les symptômes persistent plus de 3 jours, consultez un médecin.", "fr", "mal de gorge"),
            ("nausée", "En cas de nausée, je vous conseille de :\n1. Boire de l'eau par petites gorgées\n2. Manger des aliments légers\n3. Éviter les aliments gras\nSi les nausées persistent, consultez un médecin.", "fr", "nausée"),
            ("fatigue", "La fatigue peut avoir plusieurs causes. Je vous conseille de :\n1. Dormir suffisamment\n2. Faire de l'exercice régulièrement\n3. Avoir une alimentation équilibrée\nSi la fatigue persiste, consultez un médecin.", "fr", "fatigue"),
            ("allergie", "Pour les allergies, voici quelques conseils :\n1. Éviter les allergènes connus\n2. Prendre des antihistaminiques\n3. Aérer votre maison\nSi les symptômes sont graves, consultez un médecin.", "fr", "allergie"),
            
            # Anglais - Common Symptoms
            ("headache", "I understand you're suffering from a headache. Here are some tips:\n1. Rest in a quiet place\n2. Drink plenty of water\n3. Avoid screens\nIf symptoms persist, consult a doctor.", "en", "headache"),
            ("fever", "Fever can be a sign of infection. I recommend:\n1. Taking your temperature\n2. Drinking plenty of water\n3. Resting\nIf fever exceeds 39°C, consult a doctor.", "en", "fever"),
            ("pain", "I understand you're experiencing pain. Could you please specify:\n1. The exact location\n2. The intensity\n3. The duration\nThis will help me provide better advice.", "en", "pain"),
            ("cough", "For cough, here are some recommendations:\n1. Drink plenty of water\n2. Use a humidifier\n3. Avoid irritants (smoke, perfumes)\nIf cough persists for more than 3 weeks, consult a doctor.", "en", "cough"),
            ("sore throat", "For sore throat, try these tips:\n1. Gargle with salt water\n2. Drink warm beverages\n3. Rest your voice\nIf symptoms persist for more than 3 days, consult a doctor.", "en", "sore throat"),
            ("nausea", "For nausea, I recommend:\n1. Drinking water in small sips\n2. Eating light foods\n3. Avoiding fatty foods\nIf nausea persists, consult a doctor.", "en", "nausea"),
            ("fatigue", "Fatigue can have multiple causes. Try these tips:\n1. Get enough sleep\n2. Exercise regularly\n3. Maintain a balanced diet\nIf fatigue persists, consult a doctor.", "en", "fatigue"),
            ("allergy", "For allergies, here are some tips:\n1. Avoid known allergens\n2. Take antihistamines\n3. Ventilate your home\nIf symptoms are severe, consult a doctor.", "en", "allergy"),
            
            # Français - Questions générales
            ("bonjour", "Bonjour ! Je suis votre assistant médical. Comment puis-je vous aider aujourd'hui ?", "fr", "salutation"),
            ("merci", "Je vous en prie ! N'hésitez pas si vous avez d'autres questions.", "fr", "politesse"),
            ("au revoir", "Au revoir ! Prenez soin de vous. N'hésitez pas à revenir si vous avez d'autres questions.", "fr", "politesse"),
            
            # Anglais - General Questions
            ("hello", "Hello! I'm your medical assistant. How can I help you today?", "en", "greeting"),
            ("hi", "Hi! I'm here to answer your medical questions.", "en", "greeting"),
            ("thanks", "You're welcome! Don't hesitate if you have any other questions.", "en", "politeness"),
            ("goodbye", "Goodbye! Take care. Feel free to come back if you have any other questions.", "en", "politeness")
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO saved_responses (message, response, language, category)
            VALUES (?, ?, ?, ?)
        """, predefined_responses)
        
        conn.commit()
        conn.close()
    
    async def _get_db_response(self, message: str, language: str) -> Optional[str]:
        """Récupère une réponse de la base de données si elle existe."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Recherche de correspondances partielles dans le message
        cursor.execute("""
            SELECT response FROM saved_responses 
            WHERE language = ? AND ? LIKE '%' || message || '%'
            LIMIT 1
        """, (language, message.lower()))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    async def _generate_gpt_response(self, message: str, context: Dict, language: str) -> str:
        """Génère une réponse en utilisant la base de données ou OpenAI."""
        message = message.lower().strip()
        
        # Vérifier si le message est vide
        if not message:
            return "Je ne peux pas traiter un message vide. Veuillez écrire votre question."
        
        # Vérifier si le message est trop court
        if len(message) < 2:
            return "Votre message est trop court. Veuillez formuler une question complète."
        
        # Vérifier si le message est inapproprié
        inappropriate_words = [
            # Mots inappropriés en français
            "penis", "sex", "xxx", "porn", "merde", "putain", "connard", "connasse",
            "bâtard", "bâtarde", "bordel", "cul", "bite", "couille", "merdique",
            "conneries", "connerie", "con", "conne", "connard", "connasse",
            "pute", "putain", "merdique", "merdique", "merdique", "merdique",
            "bâtard", "bâtarde", "bordel", "cul", "bite", "couille", "merdique",
            "baise", "baiser", "nique", "niquer", "couille", "couilles", "couillon",
            "couillonne", "couillonnade", "couillonnades", "couillonnage",
            "couillonnages", "couillonner", "couillonnerie", "couillonneries",
            "couillonnes"
        ]
        
        # Vérifier si le message contient un mot inapproprié
        message_words = message.split()
        for word in message_words:
            if word in inappropriate_words:
                return "Je suis un assistant médical professionnel. Je ne peux pas répondre à ce type de message. Veuillez reformuler votre question de manière appropriée."
        
        # Vérifier si c'est une salutation
        greetings = {
            "fr": ["bonjour", "salut", "bonsoir", "coucou"],
            "en": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        }
        
        if any(word in message for word in greetings[language]):
            return "Bonjour ! Je suis votre assistant médical. Comment puis-je vous aider aujourd'hui ?" if language == "fr" else "Hello! I'm your medical assistant. How can I help you today?"
        
        # Vérifier si c'est une question non médicale
        non_medical_keywords = ["temps", "météo", "football", "cinéma", "musique", "sport", "jeu", "jeux", "film", "chanson"]
        if any(word in message for word in non_medical_keywords):
            return "Je suis un assistant médical. Je ne peux répondre qu'aux questions concernant la santé. Comment puis-je vous aider avec vos questions médicales ?"
        
        # D'abord, essayer de trouver une réponse dans la base de données
        db_response = await self._get_db_response(message, language)
        if db_response:
            return db_response
        
        # Si pas de réponse dans la base de données, utiliser OpenAI
        try:
            prompt = f"""Tu es un assistant médical professionnel. Réponds à la question suivante en {language} :
            {message}
            
            Réponds de manière professionnelle et rassurante, en donnant des conseils appropriés.
            Si les symptômes semblent graves, conseille de consulter un médecin.
            Si la question n'est pas d'ordre médical, réponds poliment que tu ne peux répondre qu'aux questions médicales."""
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erreur OpenAI : {e}")
            # En cas d'erreur OpenAI, retourner une réponse par défaut
            return "Je comprends votre préoccupation. Pourriez-vous me donner plus de détails sur vos symptômes ?"

# Configuration FastAPI
app = FastAPI(title="TheKnowHow Medical Conversational Agent (Hybrid Version)")
conversation_manager = HybridConversationManager()

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
        
        if not messages[-1].get("content"):
            raise HTTPException(status_code=400, detail="Le contenu du message ne peut pas être vide")
        
        user_profile = conversation_manager.get_or_create_user_profile(user_id)
        conversation_manager.update_user_profile(user_id)
        
        language = conversation_manager.translation_manager.detect_language(messages[-1]["content"])
        
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
        print(f"Erreur lors du traitement de la conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Une erreur est survenue lors du traitement de votre demande: {str(e)}"
        )

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket pour le chat en temps réel."""
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            language = conversation_manager.translation_manager.detect_language(message)
            
            response = await conversation_manager.generate_response(
                message,
                None,
                "anonymous",
                language
            )
            
            await websocket.send_json({"response": response.message})
            
    except WebSocketDisconnect:
        print("Client WebSocket déconnecté")
    except Exception as e:
        print(f"Erreur WebSocket : {e}")
        try:
            await websocket.send_json({
                "error": "Une erreur est survenue lors du traitement de votre demande."
            })
        except:
            pass

def main():
    """Fonction principale."""
    print("Démarrage du serveur hybride...")
    print("Pour tester l'API, utilisez :")
    print("1. curl -X POST http://localhost:8001/chat -H 'Content-Type: application/json' -d '{\"messages\":[{\"role\":\"user\",\"content\":\"Bonjour, j'ai mal à la tête\"}],\"user_id\":\"test_user\",\"context\":{}}'")
    print("2. Ou connectez-vous via WebSocket à ws://localhost:8001/ws/chat")
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main() 