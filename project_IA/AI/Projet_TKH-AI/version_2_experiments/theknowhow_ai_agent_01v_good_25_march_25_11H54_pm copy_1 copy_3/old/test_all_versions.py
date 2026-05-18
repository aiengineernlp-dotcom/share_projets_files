"""Test des différentes versions de l'agent conversationnel médical."""

import asyncio
from phase3_openai import OpenAIConversationManager
from phase3_mock import MockConversationManager
from phase3_conversationnel import ConversationManager
from responses_db import SavedResponses

async def test_openai_version():
    """Test de la version OpenAI."""
    print("\n=== Test de la version OpenAI ===")
    try:
        manager = OpenAIConversationManager()
        
        # Test en français
        response = await manager.generate_response(
            "Bonjour, j'ai mal à la tête",
            "1",
            "test_user_1",
            "fr"
        )
        print("Réponse OpenAI en français:", response.message)
        
        # Test en anglais
        response = await manager.generate_response(
            "Hello, I have a headache",
            "2",
            "test_user_2",
            "en"
        )
        print("Réponse OpenAI en anglais:", response.message)
    except Exception as e:
        print(f"Erreur lors du test OpenAI: {e}")

async def test_mock_version():
    """Test de la version avec mocks."""
    print("\n=== Test de la version avec mocks ===")
    try:
        manager = MockConversationManager()
        
        # Test en français
        response = await manager.generate_response(
            "Bonjour, j'ai mal à la tête",
            "1",
            "test_user_3",
            "fr"
        )
        print("Réponse Mock en français:", response.message)
        
        # Test en anglais
        response = await manager.generate_response(
            "Hello, I have a headache",
            "2",
            "test_user_4",
            "en"
        )
        print("Réponse Mock en anglais:", response.message)
    except Exception as e:
        print(f"Erreur lors du test Mock: {e}")

async def test_saved_responses():
    """Test de la version avec réponses sauvegardées."""
    print("\n=== Test de la version avec réponses sauvegardées ===")
    try:
        saved_responses = SavedResponses()
        
        # Test en français
        response = saved_responses.get_response("mal à la tête", "fr")
        print("Réponse sauvegardée en français:", response)
        
        # Test en anglais
        response = saved_responses.get_response("headache", "en")
        print("Réponse sauvegardée en anglais:", response)
    except Exception as e:
        print(f"Erreur lors du test des réponses sauvegardées: {e}")

async def main():
    """Fonction principale pour exécuter tous les tests."""
    try:
        # Exécuter les tests
        await test_openai_version()
        await test_mock_version()
        await test_saved_responses()
        
    except Exception as e:
        print(f"Erreur lors des tests: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 