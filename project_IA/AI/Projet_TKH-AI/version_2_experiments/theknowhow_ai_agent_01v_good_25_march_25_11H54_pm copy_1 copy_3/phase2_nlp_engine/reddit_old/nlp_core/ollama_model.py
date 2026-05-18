"""
Module pour l'interaction avec le modèle Ollama.
"""
import requests
import json
from typing import Dict, Any

class OllamaMedicalModel:
    """Classe pour gérer les interactions avec le modèle Ollama."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le modèle Ollama.
        
        Args:
            config: Configuration du modèle
        """
        self.config = config
        self.base_url = "http://localhost:11434/api/generate"
        
    def generate_response(self, prompt: str) -> str:
        """
        Génère une réponse à partir d'un prompt.
        
        Args:
            prompt: Le prompt à envoyer au modèle
            
        Returns:
            str: La réponse générée
        """
        try:
            response = requests.post(
                self.base_url,
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "temperature": self.config["model_parameters"]["temperature"],
                    "max_tokens": self.config["model_parameters"]["max_tokens"],
                    "top_p": self.config["model_parameters"]["top_p"],
                    "frequency_penalty": self.config["model_parameters"]["frequency_penalty"],
                    "presence_penalty": self.config["model_parameters"]["presence_penalty"]
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Erreur lors de la génération de la réponse : {str(e)}")
            return "Je suis désolé, je ne peux pas répondre pour le moment." 