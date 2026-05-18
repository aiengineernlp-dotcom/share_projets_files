"""
Module pour l'implémentation du modèle médical avec Ollama.
"""
import logging
import requests
import json
from typing import Dict, Any, Optional, Iterator
import time

class OllamaMedicalModel:
    """Modèle médical utilisant Ollama."""
    
    def __init__(self, model_name: str = "mistral"):
        """
        Initialise le modèle Ollama.
        
        Args:
            model_name (str): Nom du modèle à utiliser
        """
        self.model_name = model_name
        self.base_url = "http://localhost:11434/api"
        self.timeout = 30  # Réduction du timeout à 30 secondes
        self.max_retries = 3
        self.retry_delay = 5
        
        # Configuration des logs
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:  # Évite la duplication des handlers
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)  # Réduction du niveau de log
        
        self.logger.info(f"Initialisation du modèle Ollama avec le modèle {model_name}")
        
        # Templates de réponses
        self.response_templates = {
            'urgence': [
                "Cette situation semble nécessiter une attention médicale immédiate. Je vous conseille de contacter les services d'urgence ou de vous rendre au plus proche centre médical.",
                "Votre situation semble préoccupante. Il est important de consulter un professionnel de santé rapidement pour une évaluation appropriée.",
                "Je comprends votre inquiétude. Dans ce cas, il est crucial de demander l'avis d'un médecin sans délai."
            ],
            'symptome': [
                "Je comprends que vous ressentez ces symptômes. Pouvez-vous me donner plus de détails sur leur intensité et leur durée ? Cela m'aidera à mieux comprendre votre situation.",
                "Ces symptômes peuvent avoir plusieurs causes. Pour vous aider au mieux, pourriez-vous préciser depuis combien de temps ils persistent ?",
                "Je note vos symptômes. Pour une meilleure compréhension, pourriez-vous me dire s'ils sont constants ou intermittents ?"
            ],
            'diagnostic': [
                "Je ne peux pas établir de diagnostic précis sans examen médical. Je vous conseille de consulter un professionnel de santé pour une évaluation complète.",
                "Un diagnostic précis nécessite une évaluation médicale approfondie. Je vous recommande de prendre rendez-vous avec votre médecin.",
                "Pour établir un diagnostic fiable, il est essentiel de consulter un professionnel de santé qui pourra vous examiner."
            ]
        }
        
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Effectue une requête à l'API Ollama avec gestion des erreurs et retry."""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Tentative {attempt + 1}/{self.max_retries} - Requête vers {url}")
                
                response = requests.post(
                    url,
                    json=data,
                    timeout=self.timeout,
                    stream=True
                )
                
                if response.status_code == 200:
                    return response
                
                self.logger.warning(f"Échec de la requête (code {response.status_code}): {response.text}")
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout lors de la tentative {attempt + 1}")
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"Erreur de connexion lors de la tentative {attempt + 1}")
            except Exception as e:
                self.logger.error(f"Erreur inattendue lors de la tentative {attempt + 1}: {str(e)}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        raise Exception("Impossible de se connecter au serveur Ollama après plusieurs tentatives")

    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Génère une réponse en utilisant le modèle Ollama."""
        try:
            # Construction du prompt complet
            full_prompt = self._construct_prompt(prompt, context)
            
            # Préparation des données pour la requête
            data = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": True
            }
            
            # Envoi de la requête
            response = self._make_request("generate", data)
            
            # Traitement de la réponse en streaming
            complete_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line)
                        if "response" in json_response:
                            complete_response += json_response["response"]
                    except json.JSONDecodeError:
                        continue
            
            return complete_response.strip()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de réponse: {str(e)}")
            return self._get_fallback_response(context)

    def _construct_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """Construit le prompt complet avec le contexte."""
        system_prompt = "Tu es un assistant médical professionnel et empathique. Ta mission est de fournir des informations médicales précises et de guider les utilisateurs vers des ressources appropriées. Réponds toujours en français et de manière professionnelle."
        
        if context:
            return f"{system_prompt}\n\nContexte: {context}\n\nQuestion: {prompt}\n\nRéponse:"
        return f"{system_prompt}\n\nQuestion: {prompt}\n\nRéponse:"
        
    def _get_fallback_response(self, context: Optional[str] = None) -> str:
        """Retourne une réponse de secours."""
        if context and context in self.response_templates:
            import random
            return random.choice(self.response_templates[context])
        return "Je comprends votre situation. Pour une assistance médicale appropriée, je vous recommande de consulter un professionnel de santé." 