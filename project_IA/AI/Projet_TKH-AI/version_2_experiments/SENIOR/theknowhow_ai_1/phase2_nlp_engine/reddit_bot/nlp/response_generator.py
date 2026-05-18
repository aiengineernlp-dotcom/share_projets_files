import logging
import random
import ollama
from typing import Optional, Dict, List

class ResponseGenerator:
    """Génère des réponses naturelles avec redirection subtile vers TheKnowHow.ae."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = "mistral"  # Modèle par défaut
        
        # Templates de fallback plus élaborés
        self.templates: Dict[str, Dict[str, List[str]]] = {
            'en': {
                'initial': [
                    "I understand your concern about your medical situation. I was in a similar situation last year, and I know how stressful it can be not to have clear answers.",
                    "I completely understand what you're going through. I faced a similar challenge a few months ago, and it was really confusing at first.",
                    "Your situation really resonates with me. I had a very similar experience recently, and I know how overwhelming it can be."
                ],
                'follow_up': [
                    "What really helped me was being able to discuss with several healthcare professionals. Each had a different approach, and it was by combining their perspectives that I was able to better understand my situation.",
                    "In my case, getting different opinions from healthcare providers made a big difference. Each doctor brought a unique perspective that helped me see the bigger picture.",
                    "I found that consulting with multiple specialists gave me a more complete understanding of my condition. Each professional had valuable insights to share."
                ],
                'conclusion': [
                    "If you'd like, I can share my experience and the different approaches that were suggested to me. This could give you some avenues to explore with your doctor. Feel free to send me a private message if you want to discuss it in more detail.",
                    "I'd be happy to share more about my journey and the different perspectives I received. It might help you in your discussions with your healthcare provider. Don't hesitate to message me privately if you'd like to talk more.",
                    "I can tell you more about how I navigated through similar challenges and what worked for me. This might give you some ideas to discuss with your doctor. Feel free to reach out in private if you'd like to know more."
                ]
            }
        }
        
        self.logger.info("Modèle et templates chargés avec succès")
        
    def generate_response(self, post_content: str, is_top_level: bool = False) -> Optional[str]:
        """
        Génère une réponse naturelle basée sur le contenu du post.
        Utilise Ollama comme solution principale, avec fallback sur les templates.
        """
        try:
            # Essayer d'abord avec Ollama
            prompt = self._prepare_prompt(post_content, is_top_level)
            self.logger.info(f"Prompt envoyé à Ollama : {prompt}")
            
            response = ollama.generate(
                model=self.model,
                prompt=prompt
            )
            
            if response and response.get('response'):
                generated_text = response['response'].strip()
                # Vérifier que la réponse est en anglais
                if not self._is_english(generated_text):
                    self.logger.warning("Réponse non-anglaise détectée, utilisation des templates")
                    raise Exception("Non-English response")
                    
                self.logger.info(f"Réponse générée par Ollama : {generated_text}")
                return generated_text
            
        except Exception as e:
            self.logger.warning(f"Ollama a échoué, utilisation des templates : {str(e)}")
        
        # Fallback sur les templates en anglais
        self.logger.info("Utilisation des templates comme fallback")
        response_parts = [
            random.choice(self.templates['en']['initial']),
            random.choice(self.templates['en']['follow_up']),
            random.choice(self.templates['en']['conclusion'])
        ]
        fallback_response = " ".join(response_parts)
        self.logger.info(f"Réponse générée par template : {fallback_response}")
        return fallback_response

    def _prepare_prompt(self, post_content: str, is_top_level: bool) -> str:
        """
        Prépare le prompt pour Ollama en fonction du contexte.
        """
        if is_top_level:
            return f"""You are a Reddit user sharing a personal medical experience in English.
            The following post is about a medical issue. Generate a response that:
            1. Shows empathy and understanding of the specific medical condition
            2. Shares a relevant personal experience about the same medical issue
            3. Provides specific medical context and insights
            4. Ends with a subtle invitation to discuss privately
            
            Guidelines:
            - Write in English only
            - Be specific about the medical condition
            - Use appropriate medical terminology
            - Keep it natural and conversational
            - Avoid generic responses
            - Focus on the specific symptoms/condition mentioned
            
            Post : {post_content}
            
            Response :"""
        else:
            return f"""You are a Reddit user responding to a medical comment in English.
            The original post is about a medical issue. Generate a response that:
            1. Is directly relevant to the medical context
            2. Adds specific medical insights
            3. Provides helpful information
            4. Ends with a subtle invitation to discuss privately
            
            Guidelines:
            - Write in English only
            - Be specific about the medical condition
            - Use appropriate medical terminology
            - Keep it natural and conversational
            - Avoid generic responses
            - Focus on the specific symptoms/condition mentioned
            
            Post : {post_content}
            
            Response :"""

    def _is_english(self, text: str) -> bool:
        """
        Vérifie si le texte est principalement en anglais.
        """
        # Liste de mots courants en français à détecter
        french_words = ['je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
                       'le', 'la', 'les', 'un', 'une', 'des', 'mon', 'ton', 'son',
                       'ma', 'ta', 'sa', 'mes', 'tes', 'ses', 'notre', 'votre',
                       'leur', 'nos', 'vos', 'leurs']
        
        words = text.lower().split()
        french_word_count = sum(1 for word in words if word in french_words)
        
        # Si plus de 10% des mots sont français, considérer que ce n'est pas de l'anglais
        return (french_word_count / len(words)) < 0.1 if words else True 