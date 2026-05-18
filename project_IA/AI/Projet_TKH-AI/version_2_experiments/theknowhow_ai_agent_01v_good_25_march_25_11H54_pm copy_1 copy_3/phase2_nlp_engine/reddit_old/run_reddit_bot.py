"""
Script principal pour l'exécution du bot Reddit.
"""
import logging
import time
import random
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# Ajout du répertoire parent au PYTHONPATH
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from bot.reddit_manager import RedditManager
from nlp_core.medical_model import MedicalNLPModel

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        # Initialisation des composants
        self.reddit_manager = RedditManager(config_path)
        self.post_analyzer = PostAnalyzer(self.config)
        self.response_generator = ResponseGenerator(self.config)
        
        # Configuration des limites
        self.max_posts_per_iteration = self.config['reddit']['max_posts_per_iteration']
        self.max_replies_per_iteration = self.config['reddit']['max_replies_per_iteration']
        
        # État du bot
        self.is_running = False
        self.last_iteration = datetime.now()
        
    def run(self):
        """Exécute le bot en continu."""
        self.is_running = True
        self.logger.info("Démarrage du bot Reddit")
        
        while self.is_running:
            try:
                self._run_iteration()
            except Exception as e:
                self.logger.error(f"Erreur lors de l'itération: {str(e)}")
                time.sleep(60)  # Attendre 1 minute en cas d'erreur
                
    def _run_iteration(self):
        """Exécute une itération du bot."""
        # Vérification du délai minimum entre les itérations
        if (datetime.now() - self.last_iteration) < timedelta(seconds=self.config['reddit']['min_delay']):
            time.sleep(1)
            return
            
        self.logger.info("Début d'une nouvelle itération")
        
        # Surveillance des subreddits
        posts = self.reddit_manager.monitor_subreddits()
        self.logger.info(f"Trouvé {len(posts)} posts pertinents")
        
        # Limitation du nombre de posts à traiter
        posts = posts[:self.max_posts_per_iteration]
        
        # Traitement des posts
        for post in posts:
            try:
                # Analyse du post
                analysis = self.post_analyzer.analyze_post(post)
                
                # Génération de la réponse
                response = self.response_generator.generate_response(post, analysis)
                
                # Engagement avec le post
                if response:
                    self.reddit_manager.engage_with_post(post, response)
                    
                # Délai aléatoire entre les réponses
                delay = random.uniform(self.config['reddit']['min_delay'], self.config['reddit']['max_delay'])
                self.logger.debug(f"Attente de {delay:.2f} secondes avant la prochaine réponse")
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Erreur lors du traitement du post {post.get('id')}: {str(e)}")
                continue
                
        # Surveillance des réponses
        replies = self.reddit_manager.monitor_replies()
        self.logger.info(f"Trouvé {len(replies)} réponses pertinentes")
        
        # Limitation du nombre de réponses à traiter
        replies = replies[:self.max_replies_per_iteration]
        
        # Traitement des réponses
        for reply in replies:
            try:
                # Analyse de la réponse
                analysis = self.post_analyzer.analyze_post(reply)
                
                # Génération de la réponse
                response = self.response_generator.generate_response(reply, analysis)
                
                # Engagement avec la réponse
                if response:
                    self.reddit_manager.engage_with_reply(reply, response)
                    
                # Délai aléatoire entre les réponses
                delay = random.uniform(self.config['reddit']['min_delay'], self.config['reddit']['max_delay'])
                self.logger.debug(f"Attente de {delay:.2f} secondes avant la prochaine réponse")
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Erreur lors du traitement de la réponse {reply.get('id')}: {str(e)}")
                continue
                
        self.last_iteration = datetime.now()
        self.logger.info("Fin de l'itération")
        
    def stop(self):
        """Arrête le bot."""
        self.is_running = False
        self.logger.info("Arrêt du bot Reddit")
        
    def _determine_conversation_stage(self, reply: Dict) -> int:
        """
        Détermine le stade de la conversation.
        
        Args:
            reply: Réponse à analyser
            
        Returns:
            int: Stade de la conversation (1: initial, 2: suivi, 3: conclusion)
        """
        # Si c'est la première réponse du bot
        if reply.get('is_first_reply', False):
            return 1
            
        # Si c'est une réponse à une réponse du bot
        elif reply.get('is_reply_to_bot', False):
            return 2
            
        # Sinon, on considère que c'est la conclusion
        else:
            return 3
            
def main():
    """Fonction principale."""
    # Chemin vers le fichier de configuration
    config_path = Path(__file__).parent / 'config' / 'config.json'
    
    try:
        # Initialiser le bot
        bot = RedditBot(str(config_path))
        bot.run()
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du bot: {str(e)}")
        raise
    
if __name__ == '__main__':
    main() 