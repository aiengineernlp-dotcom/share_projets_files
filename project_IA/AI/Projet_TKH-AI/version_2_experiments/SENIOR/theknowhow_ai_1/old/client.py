import asyncio
import websockets
async def test_chat():
    uri = "ws://localhost:8001/chat"
    try:
        async with websockets.connect(uri) as websocket:
            # Liste de messages de test
            messages = [
                "Bonjour, j'ai besoin d'un deuxième avis médical",
                "Je ressens des douleurs étranges depuis quelques semaines",
                "Qu'est-ce que TheKnowHow peut faire pour moi ?",
                "Je suis vraiment inquiet de mon état de santé"
            ]

            for message in messages:
                print(f"\n🔹 Message envoyé : {message}")

                # Envoyer le message
                await websocket.send(message)

                # Recevoir la réponse
                response = await websocket.recv()
                print(f"🔸 Réponse reçue : {response}")

                # Petit délai entre les messages
                await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosed:
        print("❌ La connexion a été fermée")
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")


# Lancer le test
asyncio.run(test_chat())