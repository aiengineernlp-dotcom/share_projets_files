import praw
import logging
from typing import Dict, List
import time
import random
from nlp.private_response_manager import PrivateResponseManager

class RedditManager:
    """Gère les interactions avec Reddit."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.reddit = praw.Reddit(
            client_id=config['reddit']['client_id'],
            client_secret=config['reddit']['client_secret'],
            username=config['reddit']['username'],
            password=config['reddit']['password'],
            user_agent=config['reddit']['user_agent']
        )
        self.private_response_manager = PrivateResponseManager(self.reddit)
        self.conversation_tracker = {}  # Pour suivre les conversations en cours
        
    def monitor_subreddits(self):
        """Surveille les subreddits configurés"""
        relevant_posts = []
        
        for subreddit_name in self.config['reddit']['subreddits']:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                self.logger.info(f"\nAnalyse des posts dans r/{subreddit_name}:")
                
                total_posts = 0
                relevant_in_subreddit = 0
                
                for post in subreddit.new(limit=50):
                    total_posts += 1
                    relevance = self._is_relevant_post(post)
                    if relevance['is_relevant']:
                        relevant_posts.append(post)
                        relevant_in_subreddit += 1
                        
                        self.logger.info(f"\nPost ID: {post.id}")
                        self.logger.info(f"Titre: {post.title}")
                        self.logger.info(f"Score: {post.score} | Commentaires: {post.num_comments}")
                        self.logger.info(f"Mots-clés de second avis trouvés: {', '.join(relevance['second_opinion_keywords']) if relevance['second_opinion_keywords'] else 'Aucun'}")
                        self.logger.info(f"URL: {post.url}")
                
                self.logger.info(f"\nRésumé pour r/{subreddit_name}:")
                self.logger.info(f"Posts pertinents trouvés: {relevant_in_subreddit}/{total_posts}")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'analyse de r/{subreddit_name}: {str(e)}")
                
        return relevant_posts
        
    def _is_relevant_post(self, post):
        """Détermine si un post est pertinent pour un second avis"""
        # Vérifie si le post contient des mots-clés de second avis
        text = f"{post.title} {post.selftext}".lower()
        second_opinion_keywords = [
            'second opinion', 'not sure', 'confused', 'wondering',
            'question', 'check', 'skeptical', 'need advice'
        ]
        
        found_keywords = [keyword for keyword in second_opinion_keywords if keyword in text]
        return {
            'is_relevant': len(found_keywords) > 0,
            'second_opinion_keywords': found_keywords
        }
        
    def engage_with_post(self, post, response=None):
        """Engage avec un post pertinent en envoyant UNIQUEMENT un message privé"""
        try:
            relevance = self._is_relevant_post(post)
            if relevance['is_relevant']:
                self.logger.info(f"Envoi d'un message privé pour le post : {post.title}")
                
                # Vérifier si nous avons déjà engagé une conversation
                if post.author.name in self.conversation_tracker:
                    stage = self.conversation_tracker[post.author.name]
                    if stage < 3:  # Si la conversation n'est pas terminée
                        success = self.private_response_manager.handle_conversation(post, response)
                        if success:
                            self.conversation_tracker[post.author.name] += 1
                            self.logger.info(f"Message privé envoyé à {post.author.name} (étape {stage + 1})")
                else:
                    # Démarrer une nouvelle conversation
                    success = self.private_response_manager.handle_conversation(post, response)
                    if success:
                        self.conversation_tracker[post.author.name] = 1
                        self.logger.info(f"Nouvelle conversation démarrée avec {post.author.name}")
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message privé pour le post {post.id}: {str(e)}")
            return False 