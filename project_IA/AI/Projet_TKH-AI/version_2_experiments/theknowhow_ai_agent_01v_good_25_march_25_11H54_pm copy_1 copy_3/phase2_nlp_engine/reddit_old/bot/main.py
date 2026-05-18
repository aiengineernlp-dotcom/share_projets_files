"""
Script principal du bot Reddit.
"""
import logging
import time
import random
from datetime import datetime
import json
from pathlib import Path

from reddit_manager import RedditManager
from nlp.analyzer import PostAnalyzer
from nlp.generator import ResponseGenerator
from utils.logger import setup_logger
from utils.config import load_config

class RedditBot:
    """Classe principale du bot Reddit."""
    
    def __init__(self, config_path: str):
        """
        Initialise le bot Reddit.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        # Configuration
        self.config = load_config(config_path)
        self.logger = setup_logger(__name__)
        
        # Initialisation des composants
        self.reddit_manager = RedditManager(self.config)
        self.post_analyzer = PostAnalyzer(self.config)
        self.response_generator = ResponseGenerator(self.config)
        
        # Statistiques
        self.stats = {
            'posts_processed': 0,
            'replies_processed': 0,
            'successful_engagements': 0,
            'failed_engagements': 0,
            'last_reset': datetime.now()
        }
        
    def run(self):
        """Exécute le bot en continu."""
        self.logger.info("Démarrage du bot Reddit")
        
        while True:
            try:
                # Surveillance des subreddits
                self._monitor_subreddits()
                
                # Surveillance des réponses
                self._monitor_replies()
                
                # Pause entre les itérations
                delay = random.uniform(
                    self.config['reddit']['min_delay'],
                    self.config['reddit']['max_delay']
                )
                self.logger.info(f"Pause de {delay/60:.1f} minutes avant la prochaine itération")
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle principale: {str(e)}")
                time.sleep(60)  # Pause plus longue en cas d'erreur
                
    def _monitor_subreddits(self):
        """Surveille les subreddits pour détecter les opportunités d'engagement."""
        self.logger.info("Surveillance des subreddits")
        
        # Récupération des posts pertinents
        relevant_posts = self.reddit_manager.get_relevant_posts()
        self.logger.info(f"Trouvé {len(relevant_posts)} posts pertinents")
        
        # Limite du nombre de posts traités
        posts_to_process = relevant_posts[:self.config['reddit']['max_posts_per_iteration']]
        
        for post in posts_to_process:
            try:
                # Analyse du post
                analysis = self.post_analyzer.analyze(post)
                
                # Génération de la réponse
                response = self.response_generator.generate(
                    post=post,
                    analysis=analysis,
                    stage=1  # Stage initial
                )
                
                # Engagement avec le post
                if self.reddit_manager.engage_with_post(post, response):
                    self.stats['successful_engagements'] += 1
                    self.stats['posts_processed'] += 1
                    self.logger.info(f"Engagement réussi avec le post {post['id']}")
                else:
                    self.stats['failed_engagements'] += 1
                    
            except Exception as e:
                self.logger.error(f"Erreur lors du traitement du post {post['id']}: {str(e)}")
                self.stats['failed_engagements'] += 1
                continue
                
    def _monitor_replies(self):
        """Surveille les réponses aux commentaires du bot."""
        self.logger.info("Surveillance des réponses")
        
        # Récupération des réponses pertinentes
        relevant_replies = self.reddit_manager.get_relevant_replies()
        self.logger.info(f"Trouvé {len(relevant_replies)} réponses pertinentes")
        
        # Limite du nombre de réponses traitées
        replies_to_process = relevant_replies[:self.config['reddit']['max_replies_per_iteration']]
        
        for reply in replies_to_process:
            try:
                # Analyse de la réponse
                analysis = self.post_analyzer.analyze(reply)
                
                # Détermination du stade de la conversation
                conversation_stage = self._determine_conversation_stage(reply)
                
                # Génération de la réponse
                response = self.response_generator.generate(
                    post=reply,
                    analysis=analysis,
                    stage=conversation_stage
                )
                
                # Engagement avec la réponse
                if self.reddit_manager.engage_with_reply(reply, response):
                    self.stats['successful_engagements'] += 1
                    self.stats['replies_processed'] += 1
                    self.logger.info(f"Engagement réussi avec la réponse {reply['id']}")
                else:
                    self.stats['failed_engagements'] += 1
                    
            except Exception as e:
                self.logger.error(f"Erreur lors du traitement de la réponse {reply['id']}: {str(e)}")
                self.stats['failed_engagements'] += 1
                continue
                
    def _determine_conversation_stage(self, reply: dict) -> int:
        """
        Détermine le stade de la conversation.
        
        Args:
            reply: Réponse à analyser
            
        Returns:
            int: Stade de la conversation (1: initial, 2: suivi, 3: conclusion)
        """
        if reply.get('is_first_reply', False):
            return 1
        elif reply.get('is_reply_to_bot', False):
            return 2
        else:
            return 3

def main():
    """Fonction principale."""
    # Chemin vers le fichier de configuration
    config_path = Path(__file__).parent.parent / 'config.json'
    
    # Création et exécution du bot
    bot = RedditBot(str(config_path))
    bot.run()
    
if __name__ == '__main__':
    main() 