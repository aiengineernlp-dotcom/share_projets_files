"""Script pour une conversation interactive avec l'agent médical."""

import asyncio
import websockets
import json

async def chat():
    """Fonction pour la conversation interactive."""
    uri = "ws://localhost:8001/ws/chat"
    
    print("Connexion à l'assistant médical...")
    async with websockets.connect(uri) as websocket:
        print("\nAssistant médical connecté !")
        print("Écrivez 'quit' pour quitter la conversation.")
        
        while True:
            # Demander le message à l'utilisateur
            message = input("\nVous : ")
            
            # Vérifier si l'utilisateur veut quitter
            if message.lower() == 'quit':
                break
            
            # Envoyer le message
            await websocket.send(message)
            
            # Recevoir la réponse
            response = await websocket.recv()
            response_data = json.loads(response)
            
            # Afficher la réponse
            print("\nAssistant :", response_data["response"])

def main():
    """Fonction principale."""
    try:
        asyncio.run(chat())
    except KeyboardInterrupt:
        print("\nAu revoir !")
    except Exception as e:
        print(f"\nErreur : {e}")

if __name__ == "__main__":
    main() 