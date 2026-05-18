"""
Module pour la gestion de l'intégration avec Reddit.
"""
import praw
import logging
from typing import List, Dict, Optional
import time
import random
from datetime import datetime, timedelta
import json
from pathlib import Path
import os

from utils.logger import setup_logger

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_bot.log'),
        logging.StreamHandler()
    ]
)

class RedditManager:
    """Gère les interactions avec l'API Reddit."""
    
    def __init__(self, config: dict):
        """
        Initialise le gestionnaire Reddit.
        
        Args:
            config: Configuration du bot
        """
        self.config = config
        self.logger = setup_logger(__name__)
        self.reddit = praw.Reddit(
            client_id=config['reddit']['client_id'],
            client_secret=config['reddit']['client_secret'],
            username=config['reddit']['username'],
            password=config['reddit']['password'],
            user_agent=config['reddit']['user_agent']
        )
        
    def get_relevant_posts(self) -> List[dict]:
        """
        Récupère les posts pertinents des subreddits configurés.
        
        Returns:
            List[dict]: Liste des posts pertinents
        """
        relevant_posts = []
        for subreddit_name in self.config['reddit']['subreddits']:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                for post in subreddit.new(limit=50):
                    post_data = {
                        'id': post.id,
                        'title': post.title,
                        'content': post.selftext,
                        'subreddit': subreddit_name,
                        'created_utc': post.created_utc,
                        'score': post.score,
                        'num_comments': post.num_comments
                    }
                    relevant_posts.append(post_data)
            except Exception as e:
                self.logger.error(f"Erreur lors de la récupération des posts de r/{subreddit_name}: {str(e)}")
        return relevant_posts
        
    def get_relevant_replies(self) -> List[dict]:
        """
        Récupère les réponses pertinentes aux commentaires du bot.
        
        Returns:
            List[dict]: Liste des réponses pertinentes
        """
        relevant_replies = []
        try:
            for comment in self.reddit.user.me().comments.new(limit=50):
                for reply in comment.replies:
                    reply_data = {
                        'id': reply.id,
                        'content': reply.body,
                        'parent_id': comment.id,
                        'created_utc': reply.created_utc,
                        'is_first_reply': len(comment.replies) == 1,
                        'is_reply_to_bot': True
                    }
                    relevant_replies.append(reply_data)
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des réponses: {str(e)}")
        return relevant_replies
        
    def engage_with_post(self, post: dict, response: str) -> bool:
        """
        Engage une conversation avec un post.
        
        Args:
            post: Données du post
            response: Réponse à poster
            
        Returns:
            bool: True si l'engagement a réussi, False sinon
        """
        try:
            submission = self.reddit.submission(id=post['id'])
            submission.reply(response)
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'engagement avec le post {post['id']}: {str(e)}")
            return False
            
    def engage_with_reply(self, reply: dict, response: str) -> bool:
        """
        Engage une conversation avec une réponse.
        
        Args:
            reply: Données de la réponse
            response: Réponse à poster
            
        Returns:
            bool: True si l'engagement a réussi, False sinon
        """
        try:
            comment = self.reddit.comment(id=reply['id'])
            comment.reply(response)
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'engagement avec la réponse {reply['id']}: {str(e)}")
            return False
        
    def monitor_subreddits(self) -> List[Dict]:
        """
        Surveille les subreddits pour détecter les opportunités d'engagement.
        
        Returns:
            List[Dict]: Liste des posts et commentaires pertinents
        """
        relevant_posts = []
        
        for subreddit_name in self.config['reddit']['subreddits']:
            try:
                self.logger.info(f"Surveillance du subreddit r/{subreddit_name}")
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Récupération des nouveaux posts
                posts = list(subreddit.new(limit=50))
                self.logger.info(f"Récupéré {len(posts)} posts de r/{subreddit_name}")
                
                for post in posts:
                    if self._is_relevant_post(post):
                        relevant_posts.append({
                            'id': post.id,
                            'type': 'post',
                            'title': post.title,
                            'content': post.selftext,
                            'author': post.author.name if post.author else 'Unknown',
                            'subreddit': subreddit_name,
                            'score': post.score,
                            'created_utc': post.created_utc,
                            'url': f"https://reddit.com{post.permalink}"
                        })
                        self.logger.info(f"Post pertinent trouvé: {post.title[:50]}...")
                        
                # Délai aléatoire entre les subreddits
                delay = random.uniform(self.config['reddit']['min_delay'], self.config['reddit']['max_delay'])
                self.logger.debug(f"Attente de {delay:.2f} secondes avant le prochain subreddit")
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la surveillance de r/{subreddit_name}: {str(e)}")
                continue
                
        self.logger.info(f"Trouvé {len(relevant_posts)} posts pertinents au total")
        return relevant_posts
        
    def _is_relevant_post(self, post) -> bool:
        """
        Vérifie si un post est pertinent pour notre intervention.
        
        Args:
            post: Post Reddit
            
        Returns:
            bool: True si le post est pertinent
        """
        try:
            # Vérification des critères de base
            if post.stickied:  # Ignore les posts épinglés
                self.logger.debug(f"Post {post.id} ignoré car épinglé")
                return False
                
            if post.author is None:  # Ignore les posts supprimés
                self.logger.debug(f"Post {post.id} ignoré car supprimé")
                return False
                
            if post.score < 1:  # Ignore les posts avec score négatif
                self.logger.debug(f"Post {post.id} ignoré car score négatif: {post.score}")
                return False
                
            # Vérification du contenu
            content = f"{post.title} {post.selftext}".lower()
            self.logger.debug(f"Analyse du post {post.id}: {content[:100]}...")
            
            # Vérification de la longueur du contenu
            if len(content.split()) < 20:  # Ignore les posts trop courts
                self.logger.debug(f"Post {post.id} ignoré car trop court")
                return False
                
            # Vérification des indicateurs de second avis
            second_opinion_indicators = self.config['second_opinion_indicators']
            has_second_opinion_need = any(indicator in content for indicator in second_opinion_indicators)
            
            if has_second_opinion_need:
                self.logger.info(f"Post {post.id} pertinent: besoin de second avis détecté")
                return True
                
            # Vérification des mots-clés médicaux
            medical_keywords = self.config['medical_keywords']
            has_medical_keywords = any(keyword in content for keyword in medical_keywords)
            
            # Vérification de la présence de questions
            has_questions = '?' in content or any(q in content for q in ['que faire', 'que penser', 'comment'])
            
            # Vérification de l'engagement (longueur et détails)
            is_engaged = len(content.split()) > 50 or 'détail' in content or 'explication' in content
            
            if has_medical_keywords and (has_questions or is_engaged):
                self.logger.info(f"Post {post.id} pertinent: mots-clés médicaux et engagement détectés")
                return True
                
            self.logger.debug(f"Post {post.id} ignoré: aucun critère de pertinence détecté")
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse du post {post.id}: {str(e)}")
            return False
        
    def _has_recent_interaction(self, post_id: str) -> bool:
        """
        Vérifie si nous avons déjà interagi avec ce post récemment.
        
        Args:
            post_id: ID du post
            
        Returns:
            bool: True si interaction récente
        """
        for interaction in self.interaction_history:
            if interaction['post_id'] == post_id:
                interaction_time = datetime.fromtimestamp(interaction['timestamp'])
                if datetime.now() - interaction_time < timedelta(hours=24):
                    return True
        return False
        
    def _record_interaction(self, post_id: str, comment_id: str):
        """
        Enregistre une interaction dans l'historique.
        
        Args:
            post_id: ID du post
            comment_id: ID du commentaire
        """
        self.interaction_history.append({
            'post_id': post_id,
            'comment_id': comment_id,
            'timestamp': datetime.now().timestamp(),
            'account': self.reddit.user.me().name
        })
        
        # Limite la taille de l'historique
        if len(self.interaction_history) > 1000:
            self.interaction_history = self.interaction_history[-1000:]
            
    def transition_to_private(self, comment_id: str, message: str) -> bool:
        """
        Transition vers une conversation privée.
        
        Args:
            comment_id: ID du commentaire
            message: Message à envoyer
            
        Returns:
            bool: True si la transition a réussi
        """
        try:
            comment = self.reddit.comment(id=comment_id)
            author = comment.author
            
            # Envoi du message privé
            author.message("Re: Discussion médicale", message)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la transition privée: {str(e)}")
            return False
        
    def monitor_replies(self) -> List[Dict]:
        """
        Surveille les réponses aux commentaires du bot.
        
        Returns:
            List[Dict]: Liste des réponses pertinentes
        """
        relevant_replies = []
        
        for interaction in self.interaction_history:
            try:
                comment = self.reddit.comment(id=interaction['comment_id'])
                comment.refresh()  # Rafraîchir pour obtenir les nouvelles réponses
                
                for reply in comment.replies:
                    if self._is_relevant_reply(reply):
                        relevant_replies.append({
                            'id': reply.id,
                            'type': 'reply',
                            'content': reply.body,
                            'author': reply.author.name if reply.author else 'Unknown',
                            'parent_id': interaction['comment_id'],
                            'created_utc': reply.created_utc
                        })
                        
            except Exception as e:
                self.logger.error(f"Erreur lors de la surveillance des réponses: {str(e)}")
                continue
                
        return relevant_replies
        
    def _is_relevant_reply(self, reply) -> bool:
        """
        Vérifie si une réponse est pertinente.
        
        Args:
            reply: Réponse Reddit
            
        Returns:
            bool: True si la réponse est pertinente
        """
        if reply.author is None:  # Ignore les réponses supprimées
            return False
            
        if reply.author.name == self.reddit.user.me().name:  # Ignore nos propres réponses
            return False
            
        # Vérification du contenu
        content = reply.body.lower()
        
        # Vérification des indicateurs d'intérêt
        interest_indicators = [
            'merci', 'intéressant', 'utile', 'aide', 'plus d\'infos',
            'en savoir plus', 'détails', 'mp', 'message privé', 'dm'
        ]
        
        return any(indicator in content for indicator in interest_indicators) 