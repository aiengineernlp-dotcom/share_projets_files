"""Version avec mocks de l'agent conversationnel médical."""

from phase3_conversationnel import ConversationManager, Response
from typing import Dict
import asyncio
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
import uvicorn

class MockConversationManager(ConversationManager):
    """Version du ConversationManager utilisant des mocks."""
    
    def __init__(self):
        super().__init__()
        self.mock_responses = {
            "fr": {
                "salutations": ["Bonjour ! Je suis votre assistant médical. Comment puis-je vous aider aujourd'hui ?",
                               "Bonjour ! Je suis là pour répondre à vos questions médicales."],
                "mal à la tête": "Je comprends que vous souffrez de maux de tête. Voici quelques conseils :\n1. Reposez-vous dans un endroit calme\n2. Buvez beaucoup d'eau\n3. Évitez les écrans\nSi les symptômes persistent, consultez un médecin.",
                "fièvre": "La fièvre peut être le signe d'une infection. Je vous conseille de :\n1. Prendre votre température\n2. Buvez beaucoup d'eau\n3. Reposer\nSi la fièvre dépasse 39°C, consultez un médecin.",
                "douleur": "Je comprends que vous avez des douleurs. Pourriez-vous me préciser :\n1. La localisation exacte\n2. L'intensité\n3. La durée\nCela m'aidera à mieux vous conseiller."
            },
            "en": {
                "salutations": ["Hello! I'm your medical assistant. How can I help you today?",
                               "Hi! I'm here to answer your medical questions."],
                "headache": "I understand you're suffering from a headache. Here are some tips:\n1. Rest in a quiet place\n2. Drink plenty of water\n3. Avoid screens\nIf symptoms persist, consult a doctor.",
                "fever": "Fever can be a sign of infection. I recommend:\n1. Taking your temperature\n2. Drinking plenty of water\n3. Resting\nIf fever exceeds 39°C, consult a doctor.",
                "pain": "I understand you're experiencing pain. Could you please specify:\n1. The exact location\n2. The intensity\n3. The duration\nThis will help me provide better advice."
            }
        }

    async def _generate_gpt_response(self, message: str, context: Dict, language: str) -> str:
        """Génère une réponse mock basée sur le message."""
        message = message.lower()
        
        # Vérifier les salutations
        if any(word in message for word in ["bonjour", "salut", "hello", "hi"]):
            import random
            return random.choice(self.mock_responses[language]["salutations"])
        
        # Vérifier les maux de tête
        if any(word in message for word in ["mal à la tête", "céphalée", "headache"]):
            return self.mock_responses[language]["mal à la tête" if language == "fr" else "headache"]
        
        # Vérifier la fièvre
        if any(word in message for word in ["fièvre", "fever"]):
            return self.mock_responses[language]["fièvre" if language == "fr" else "fever"]
        
        # Vérifier les douleurs
        if any(word in message for word in ["douleur", "pain"]):
            return self.mock_responses[language]["douleur" if language == "fr" else "pain"]
        
        # Réponse par défaut
        return "Je comprends votre préoccupation. Pourriez-vous me donner plus de détails sur vos symptômes ?"

# Configuration FastAPI
app = FastAPI(title="TheKnowHow Medical Conversational Agent (Mock Version)")
conversation_manager = MockConversationManager()

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
            # Recevoir le message
            message = await websocket.receive_text()
            
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
        print("Client WebSocket déconnecté")
    except Exception as e:
        print(f"Erreur WebSocket : {e}")
        try:
            await websocket.send_json({
                "error": "Une erreur est survenue lors du traitement de votre demande."
            })
        except:
            pass

async def test_mock():
    """Test direct de la version mock."""
    print("\n=== Test direct de la version mock ===")
    try:
        # Test en français
        response = await conversation_manager.generate_response(
            "Bonjour, j'ai mal à la tête",
            "1",
            "test_user_1",
            "fr"
        )
        print("Réponse en français:", response.message)
        
        # Test en anglais
        response = await conversation_manager.generate_response(
            "Hello, I have a headache",
            "2",
            "test_user_2",
            "en"
        )
        print("Réponse en anglais:", response.message)
    except Exception as e:
        print(f"Erreur lors du test: {e}")

def main():
    """Fonction principale."""
    print("Démarrage du serveur mock...")
    print("Pour tester l'API, utilisez :")
    print("1. curl -X POST http://localhost:8001/chat -H 'Content-Type: application/json' -d '{\"messages\":[{\"role\":\"user\",\"content\":\"Bonjour, j''ai mal à la tête\"}],\"user_id\":\"test_user\",\"context\":{}}'")
    print("2. Ou connectez-vous via WebSocket à ws://localhost:8001/ws/chat")
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main() 