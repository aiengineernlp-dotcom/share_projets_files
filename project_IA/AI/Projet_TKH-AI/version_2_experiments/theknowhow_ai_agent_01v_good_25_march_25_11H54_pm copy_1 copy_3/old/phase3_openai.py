"""Version OpenAI de l'agent conversationnel médical."""

from phase3_conversationnel import ConversationManager, Response
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

class OpenAIConversationManager(ConversationManager):
    """Version du ConversationManager utilisant OpenAI."""
    
    def __init__(self):
        super().__init__()
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def _generate_gpt_response(self, message: str, context: Dict, language: str) -> str:
        """Génère une réponse avec OpenAI GPT."""
        try:
            prompt = self._build_prompt(message, context, language)
            response = await self.openai_client.chat.completions.create(
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
            print(f"Erreur OpenAI : {e}")
            return self._get_fallback_response(context, language) 