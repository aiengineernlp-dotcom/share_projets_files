"""
Module d'intégration avec GPT.
"""
import os
import logging
import openai
from typing import Dict, Any
from dotenv import load_dotenv

class GPTHandler:
    def __init__(self):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Génère une réponse en utilisant GPT.
        """
        try:
            # Préparation du prompt
            prompt = self._prepare_prompt(message, context)
            
            # Appel à l'API GPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Vous êtes un assistant médical IA."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de réponse GPT : {str(e)}")
            raise

    def _prepare_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """
        Prépare le prompt pour GPT.
        """
        prompt = f"Message utilisateur : {message}\n"
        prompt += f"Contexte : {context}\n"
        prompt += "Veuillez fournir une réponse appropriée."
        return prompt 