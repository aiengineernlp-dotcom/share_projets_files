"""Exemple d'utilisation de la phase 3 de l'agent conversationnel médical."""

import asyncio
import requests
import websockets
from phase3_conversationnel import ConversationManager

async def test_rest_api():
    """Test de l'API REST."""
    print("\n=== Test de l'API REST ===")
    
    try:
        # Exemple de requête en français
        response = requests.post(
            "http://localhost:8000/chat",
            json={
                "messages": [{"role": "user", "content": "Bonjour, j'ai mal à la tête"}],
                "user_id": "test_user_1",
                "context": {
                    "post_id": "1",
                    "country": "France",
                    "city": "Paris"
                }
            }
        )
        print("Réponse en français:", response.json())
    except Exception as e:
        print(f"Erreur lors du test REST en français: {e}")
    
    try:
        # Exemple de requête en anglais
        response = requests.post(
            "http://localhost:8000/chat",
            json={
                "messages": [{"role": "user", "content": "Hello, I have a headache"}],
                "user_id": "test_user_2",
                "context": {
                    "post_id": "2",
                    "country": "UAE",
                    "city": "Dubai"
                }
            }
        )
        print("Réponse en anglais:", response.json())
    except Exception as e:
        print(f"Erreur lors du test REST en anglais: {e}")

async def test_websocket():
    """Test de l'API WebSocket."""
    print("\n=== Test de l'API WebSocket ===")
    
    try:
        async with websockets.connect("ws://localhost:8000/ws/chat") as websocket:
            # Envoyer un message en français
            await websocket.send("Bonjour, j'ai mal à la tête")
            response = await websocket.recv()
            print("Réponse WebSocket en français:", response)
            
            # Envoyer un message en anglais
            await websocket.send("Hello, I have a headache")
            response = await websocket.recv()
            print("Réponse WebSocket en anglais:", response)
    except Exception as e:
        print(f"Erreur lors du test WebSocket: {e}")

async def test_direct_usage():
    """Test d'utilisation directe du ConversationManager."""
    print("\n=== Test d'utilisation directe ===")
    
    try:
        manager = ConversationManager()
        
        # Test en français
        response = await manager.generate_response(
            "Bonjour, j'ai mal à la tête",
            "1",
            "test_user_3",
            "fr"
        )
        print("Réponse directe en français:", response.message)
        
        # Test en anglais
        response = await manager.generate_response(
            "Hello, I have a headache",
            "2",
            "test_user_4",
            "en"
        )
        print("Réponse directe en anglais:", response.message)
    except Exception as e:
        print(f"Erreur lors du test direct: {e}")

async def main():
    """Fonction principale pour exécuter tous les tests."""
    try:
        # Démarrer le serveur FastAPI (dans un autre terminal)
        print("Assurez-vous que le serveur FastAPI est en cours d'exécution avec:")
        print("uvicorn phase3_conversationnel:app --reload")
        
        # Exécuter les tests
        await test_rest_api()
        await test_websocket()
        await test_direct_usage()
        
    except Exception as e:
        print(f"Erreur lors des tests: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 