"""
Scraper pour Reddit.
Ce module permet de collecter des posts et commentaires depuis Reddit liés aux avis médicaux.
"""

import os
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncpraw
from asyncpraw.models import Submission, Comment, Subreddit

class RedditScraper:
    """Scraper spécialisé pour Reddit."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le scraper Reddit.
        
        Args:
            config_path (str, optional): Chemin vers le fichier de configuration.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration par défaut
        self.config = {
            'client_id': os.environ.get('REDDIT_CLIENT_ID', ''),
            'client_secret': os.environ.get('REDDIT_CLIENT_SECRET', ''),
            'user_agent': os.environ.get('REDDIT_USER_AGENT', 'medical_data_collector:v1.0 (by /u/your_username)'),
            'subreddits': [
                'AskDocs', 'medical', 'AskMedical', 'DiagnoseMe', 'Health', 
                'medical_advice', 'MedicalAdvice', 'secondopinion', 'askdoctors'
            ],
            'search_queries': [
                # Requêtes originales
                'second opinion', 'diagnosis help', 'medical advice', 'doctor opinion',
                'need help diagnosis', 'medical question', 'health concern',
                'worried about symptoms', 'medical uncertainty', 'doctor second opinion',
                
                # Nouvelles requêtes spécifiques au second avis médical
                'need another doctor', 'different medical opinion', 'conflicting diagnosis',
                'alternative medical opinion', 'disagree with doctor', 'doctor was wrong',
                'seeking medical confirmation', 'validate diagnosis', 'unsure about diagnosis',
                'medical misdiagnosis', 'doctor disagreement', 'medical consultation',
                'specialist opinion', 'medical expert opinion', 'contradicting medical advice',
                'questioning treatment', 'medical error', 'wrong treatment',
                'medical consultation advice', 'trust doctor opinion'
            ],
            'max_posts_per_subreddit': 100,
            'max_posts_per_query': 50,
            'post_limit': 500,
            'comment_limit': 50,
            'storage_path': os.environ.get('REDDIT_DB_PATH', 'data/databases/social_media/reddit')
        }
        
        # Charger la configuration si fournie
        if config_path:
            self._load_config(config_path)
        
        # Initialiser le client Reddit
        self.reddit = None
        
        # Initialiser le stockage SQLite
        from medical_ai_agent.app.db.models import SQLiteStorage
        self.db_path = os.path.join(self.config['storage_path'], 'reddit_data.db')
        self.storage = SQLiteStorage(self.db_path)
        
        # Créer le dossier de stockage
        os.makedirs(self.config['storage_path'], exist_ok=True)
        
        self.logger.info("RedditScraper initialisé")
    
    def _load_config(self, config_path: str):
        """
        Charge la configuration depuis un fichier JSON.
        
        Args:
            config_path (str): Chemin vers le fichier de configuration.
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.config.update(config)
            self.logger.info(f"Configuration chargée depuis {config_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la configuration: {e}")
    
    async def initialize_reddit_client(self):
        """Initialise le client Reddit avec les identifiants de manière asynchrone."""
        try:
            # Afficher les informations d'authentification (masquées pour la sécurité)
            client_id = self.config['client_id']
            client_secret = self.config['client_secret']
            user_agent = self.config['user_agent']
            
            self.logger.info(f"Tentative d'initialisation du client Reddit avec:")
            self.logger.info(f"  - Client ID: {client_id[:4]}...{client_id[-4:] if len(client_id) > 8 else ''}")
            self.logger.info(f"  - User Agent: {user_agent}")
            
            # Initialiser le client Reddit avec les identifiants
            self.reddit = asyncpraw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            
            # Vérifier que le client est correctement authentifié
            # Cette ligne va lever une exception si l'authentification échoue
            try:
                me = await self.reddit.user.me()
                if me:
                    self.logger.info("Client Reddit initialisé avec succès en mode authentifié")
                else:
                    self.logger.info("Client Reddit initialisé en mode read-only")
            except Exception as e:
                self.logger.warning(f"Authentification échouée: {e}, utilisation en mode read-only")
                # Réinitialiser le client en mode read-only
                await self.reddit.close()
                self.reddit = asyncpraw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                    check_for_updates=False,
                    read_only=True
                )
                self.logger.info("Client Reddit initialisé en mode read-only")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation du client Reddit: {e}")
            self.reddit = None
    
    async def fetch_posts_from_subreddit(self, subreddit_name: str) -> List[Dict[str, Any]]:
        """
        Récupère les posts d'un subreddit.
        
        Args:
            subreddit_name (str): Nom du subreddit.
            
        Returns:
            List[Dict[str, Any]]: Liste des posts récupérés.
        """
        if not self.reddit:
            self.logger.error("Client Reddit non initialisé")
            return []
        
        posts = []
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            
            # Récupérer les posts récents
            submissions = []
            async for submission in subreddit.new(limit=self.config['max_posts_per_subreddit']):
                submissions.append(submission)
            
            for submission in submissions:
                post_data = await self._extract_post_data(submission)
                posts.append(post_data)
                
                # Récupérer les commentaires
                try:
                    # Utiliser une approche différente pour les commentaires
                    submission = await self.reddit.submission(id=submission.id)
                    await submission.load()  # Charger complètement la soumission
                    
                    # Récupérer les commentaires de premier niveau uniquement
                    if hasattr(submission, 'comments') and submission.comments:
                        comment_list = []
                        async for comment in submission.comments:
                            if len(comment_list) >= self.config['comment_limit']:
                                break
                            comment_list.append(comment)
                        
                        for comment in comment_list:
                            comment_data = await self._extract_comment_data(comment, submission.id)
                            posts.append(comment_data)
                except Exception as e:
                    self.logger.error(f"Erreur lors de la récupération des commentaires pour {submission.id}: {e}")
            
            self.logger.info(f"Récupéré {len(posts)} posts/commentaires depuis r/{subreddit_name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des posts de r/{subreddit_name}: {e}")
        
        return posts
    
    async def search_posts_by_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Recherche des posts par requête.
        
        Args:
            query (str): Requête de recherche.
            
        Returns:
            List[Dict[str, Any]]: Liste des posts récupérés.
        """
        if not self.reddit:
            self.logger.error("Client Reddit non initialisé")
            return []
        
        posts = []
        try:
            # Rechercher dans tous les subreddits
            subreddit = await self.reddit.subreddit('all')
            
            # Collecter d'abord les soumissions
            submissions = []
            async for submission in subreddit.search(query, limit=self.config['max_posts_per_query']):
                submissions.append(submission)
            
            # Traiter les soumissions collectées
            for submission in submissions:
                post_data = await self._extract_post_data(submission)
                posts.append(post_data)
                
                # Récupérer les commentaires
                try:
                    # Utiliser une approche différente pour les commentaires
                    submission = await self.reddit.submission(id=submission.id)
                    await submission.load()  # Charger complètement la soumission
                    
                    # Récupérer les commentaires de premier niveau uniquement
                    if hasattr(submission, 'comments') and submission.comments:
                        comment_list = []
                        async for comment in submission.comments:
                            if len(comment_list) >= self.config['comment_limit']:
                                break
                            comment_list.append(comment)
                        
                        for comment in comment_list:
                            comment_data = await self._extract_comment_data(comment, submission.id)
                            posts.append(comment_data)
                except Exception as e:
                    self.logger.error(f"Erreur lors de la récupération des commentaires pour {submission.id}: {e}")
            
            self.logger.info(f"Récupéré {len(posts)} posts/commentaires pour la requête '{query}'")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de posts pour '{query}': {e}")
        
        return posts
    
    async def _extract_post_data(self, submission: Submission) -> Dict[str, Any]:
        """
        Extrait les données d'un post Reddit.
        
        Args:
            submission (Submission): Post Reddit.
            
        Returns:
            Dict[str, Any]: Données du post.
        """
        try:
            author = str(submission.author) if submission.author else '[deleted]'
        except Exception:
            author = '[deleted]'
            
        try:
            return {
                'id': submission.id,
                'type': 'post',
                'title': submission.title,
                'content': submission.selftext,
                'author': author,
                'subreddit': submission.subreddit.display_name,
                'url': submission.url,
                'permalink': f"https://www.reddit.com{submission.permalink}",
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(),
                'num_comments': submission.num_comments,
                'is_original_content': submission.is_original_content,
                'is_self': submission.is_self,
                'collected_at': datetime.now().isoformat(),
                'source': 'Reddit'
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des données du post {submission.id}: {e}")
            # Retourner un dictionnaire minimal en cas d'erreur
            return {
                'id': submission.id,
                'type': 'post',
                'title': getattr(submission, 'title', '[error]'),
                'content': '[error extracting content]',
                'author': author,
                'subreddit': getattr(submission.subreddit, 'display_name', '[error]'),
                'collected_at': datetime.now().isoformat(),
                'source': 'Reddit'
            }
    
    async def _extract_comment_data(self, comment: Comment, post_id: str) -> Dict[str, Any]:
        """
        Extrait les données d'un commentaire Reddit.
        
        Args:
            comment (Comment): Commentaire Reddit.
            post_id (str): ID du post parent.
            
        Returns:
            Dict[str, Any]: Données du commentaire.
        """
        try:
            author = str(comment.author) if comment.author else '[deleted]'
        except Exception:
            author = '[deleted]'
            
        try:
            return {
                'id': comment.id,
                'type': 'comment',
                'post_id': post_id,
                'content': comment.body,
                'author': author,
                'subreddit': comment.subreddit.display_name,
                'permalink': f"https://www.reddit.com{comment.permalink}",
                'score': comment.score,
                'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                'is_submitter': comment.is_submitter,
                'parent_id': comment.parent_id,
                'collected_at': datetime.now().isoformat(),
                'source': 'Reddit'
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des données du commentaire {comment.id}: {e}")
            # Retourner un dictionnaire minimal en cas d'erreur
            return {
                'id': comment.id,
                'type': 'comment',
                'post_id': post_id,
                'content': '[error extracting content]',
                'author': author,
                'collected_at': datetime.now().isoformat(),
                'source': 'Reddit'
            }
    
    async def save_data(self, data: List[Dict[str, Any]], name: str = ""):
        """
        Sauvegarde les données dans la base de données.
        
        Args:
            data (List[Dict[str, Any]]): Données à sauvegarder.
            name (str, optional): Nom du fichier de sauvegarde.
        """
        if not data:
            self.logger.warning("Aucune donnée à sauvegarder")
            return
        
        try:
            # Sauvegarder dans la base de données SQLite
            await self.storage.save_reddit_data(data)
            self.logger.info(f"Données de {name} sauvegardées dans la base de données ({len(data)} éléments)")
            
            # Sauvegarder également en JSON pour la sauvegarde
            if name:
                json_path = os.path.join(self.config['storage_path'], f"{name}.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.logger.info(f"Données de {name} sauvegardées dans {json_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des données: {e}")
    
    async def run(self):
        """Exécute le processus de scraping pour Reddit."""
        await self.initialize_reddit_client()
        self.logger.info("Début du scraping de Reddit")
        
        if not self.reddit:
            self.logger.error("Impossible d'initialiser le client Reddit, abandon du scraping")
            return
        
        # Collecter les données
        all_posts = []
        
        # Scraping des subreddits
        for subreddit in self.config['subreddits']:
            try:
                self.logger.info(f"Scraping du subreddit: {subreddit}")
                posts = await self.fetch_posts_from_subreddit(subreddit)
                if posts:
                    all_posts.extend(posts)
                    self.logger.info(f"Posts collectés depuis r/{subreddit}: {len(posts)}")
                    
                    # Sauvegarder les données immédiatement après chaque subreddit
                    await self.save_data(posts, subreddit)
                    
                await asyncio.sleep(2)  # Pause pour éviter de surcharger l'API
            except Exception as e:
                self.logger.error(f"Erreur lors de la récupération des posts de r/{subreddit}: {e}")
        
        # Recherche par mots-clés
        for query in self.config['search_queries']:
            try:
                self.logger.info(f"Recherche de posts pour '{query}'")
                posts = await self.search_posts_by_query(query)
                if posts:
                    all_posts.extend(posts)
                    self.logger.info(f"Posts collectés pour la recherche '{query}': {len(posts)}")
                    
                    # Sauvegarder les données immédiatement après chaque requête
                    await self.save_data(posts, f"query_{query.replace(' ', '_')}")
                    
                await asyncio.sleep(2)  # Pause pour éviter de surcharger l'API
            except Exception as e:
                self.logger.error(f"Erreur lors de la recherche de posts pour '{query}': {e}")
        
        # Fermer la session Reddit
        await self.reddit.close()
        
        # Sauvegarder toutes les données à la fin
        if all_posts:
            await self.save_data(all_posts, "all_data")
            self.logger.info(f"Scraping de Reddit terminé, {len(all_posts)} éléments collectés")
        else:
            self.logger.warning("Aucune donnée à sauvegarder")
            self.logger.info("Scraping de Reddit terminé, 0 éléments collectés")
