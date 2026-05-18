import logging
import json
from pathlib import Path
from typing import Dict
import time
import random

from reddit_manager import RedditManager
from nlp.analyzer import PostAnalyzer
from nlp.response_generator import ResponseGenerator

class RedditBot:
    """Bot Reddit pour l'engagement médical."""
    
    def __init__(self, config_path: str):
        """
        Initialise le bot Reddit.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('reddit_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Chargement de la configuration
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info("Configuration chargée avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
            raise
            
        # Vérification des identifiants
        required_fields = ['client_id', 'client_secret', 'username', 'password', 'user_agent']
        for field in required_fields:
            if field not in self.config['reddit']:
                self.logger.error(f"Champ manquant dans la configuration: {field}")
                raise ValueError(f"Champ manquant: {field}")
            
        # Initialisation des composants
        self.reddit_manager = RedditManager(self.config)
        self.post_analyzer = PostAnalyzer()
        self.response_generator = ResponseGenerator()
        
    def run(self):
        """Exécute le bot en continu."""
        self.logger.info("Démarrage du bot Reddit")
        
        while True:
            try:
                # Surveillance des subreddits
                posts = self.reddit_manager.monitor_subreddits()
                self.logger.info(f"Trouvé {len(posts)} posts pertinents")
                
                # Traitement des posts
                for post in posts:
                    try:
                        # Analyse du post
                        analysis = self.post_analyzer.analyze_post(post)
                        
                        if analysis['needs_second_opinion']:
                            # Génération de la réponse
                            response = self.response_generator.generate_response(post, analysis)
                            
                            # Engagement avec le post
                            if response:
                                self.reddit_manager.engage_with_post(post, response)
                                
                            # Délai aléatoire entre les réponses
                            time.sleep(random.uniform(
                                self.config['reddit']['min_delay'],
                                self.config['reddit']['max_delay']
                            ))
                    except Exception as e:
                        self.logger.error(f"Erreur lors du traitement du post {post.id}: {str(e)}")
                        continue
                        
            except Exception as e:
                self.logger.error(f"Erreur lors de l'itération: {str(e)}")
                time.sleep(60)  # Attendre 1 minute en cas d'erreur
                
def main():
    """Fonction principale."""
    # Chemin vers le fichier de configuration
    config_path = Path(__file__).parent / 'config' / 'config.json'
    
    try:
        # Initialiser le bot
        bot = RedditBot(str(config_path))
        bot.run()
    except Exception as e:
        logging.error(f"Erreur lors de l'exécution du bot: {str(e)}")
        raise
    
if __name__ == '__main__':
    main() 