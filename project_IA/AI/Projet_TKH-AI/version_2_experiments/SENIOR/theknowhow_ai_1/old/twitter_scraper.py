"""
Scraper pour Twitter.
Ce module permet de collecter des tweets liés aux avis médicaux.
"""

import os
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import tweepy

class TwitterScraper:
    """Scraper spécialisé pour Twitter."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le scraper Twitter.
        
        Args:
            config_path (str, optional): Chemin vers le fichier de configuration.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration par défaut
        self.config = {
            'api_key': os.environ.get('TWITTER_API_KEY', ''),
            'api_key_secret': os.environ.get('TWITTER_API_KEY_SECRET', ''),
            'access_token': os.environ.get('TWITTER_ACCESS_TOKEN', ''),
            'access_token_secret': os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', ''),
            'bearer_token': os.environ.get('TWITTER_BEARER_TOKEN', ''),
            'search_queries': [
                'second opinion doctor', 'need medical advice', 'doctor diagnosis help',
                'medical uncertainty', 'health concern advice', 'medical second opinion',
                'deuxième avis médical', 'avis médical urgent', 'doute diagnostic',
                'consultation médicale en ligne', 'besoin avis médecin'
            ],
            'max_tweets_per_query': 100,
            'tweet_limit': 1000,
            'days_to_search': 7,
            'storage_path': 'data/databases/social_media/twitter'
        }
        
        # Charger la configuration si fournie
        if config_path:
            self._load_config(config_path)
        
        # Initialiser les clients Twitter
        self.client_v1 = None
        self.client_v2 = None
        self.initialize_twitter_clients()
        
        # Créer le dossier de stockage
        os.makedirs(self.config['storage_path'], exist_ok=True)
        
        self.logger.info("TwitterScraper initialisé")
    
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
    
    def initialize_twitter_clients(self):
        """Initialise les clients Twitter avec les identifiants."""
        try:
            # Client v1 (API traditionnelle)
            auth = tweepy.OAuth1UserHandler(
                self.config['api_key'],
                self.config['api_key_secret'],
                self.config['access_token'],
                self.config['access_token_secret']
            )
            self.client_v1 = tweepy.API(auth)
            
            # Client v2 (API moderne)
            self.client_v2 = tweepy.Client(
                bearer_token=self.config['bearer_token'],
                consumer_key=self.config['api_key'],
                consumer_secret=self.config['api_key_secret'],
                access_token=self.config['access_token'],
                access_token_secret=self.config['access_token_secret']
            )
            
            self.logger.info("Clients Twitter initialisés")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation des clients Twitter: {e}")
            self.client_v1 = None
            self.client_v2 = None
    
    async def search_tweets(self, query: str) -> List[Dict[str, Any]]:
        """
        Recherche des tweets par requête.
        
        Args:
            query (str): Requête de recherche.
            
        Returns:
            List[Dict[str, Any]]: Liste des tweets récupérés.
        """
        if not self.client_v1 or not self.client_v2:
            self.logger.error("Clients Twitter non initialisés")
            return []
        
        tweets = []
        try:
            # Calculer la date limite
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.config['days_to_search'])
            
            # Recherche avec l'API v2
            response = self.client_v2.search_recent_tweets(
                query=query,
                max_results=self.config['max_tweets_per_query'],
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang', 'geo'],
                user_fields=['name', 'username', 'description', 'location', 'verified'],
                expansions=['author_id', 'referenced_tweets.id', 'geo.place_id'],
                start_time=start_date.isoformat() + 'Z',
                end_time=end_date.isoformat() + 'Z'
            )
            
            if response.data:
                # Créer un dictionnaire pour accéder facilement aux utilisateurs
                users = {user.id: user for user in response.includes['users']} if 'users' in response.includes else {}
                
                for tweet in response.data:
                    user = users.get(tweet.author_id, None)
                    
                    tweet_data = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'author_id': tweet.author_id,
                        'author_name': user.name if user else None,
                        'author_username': user.username if user else None,
                        'author_verified': user.verified if user else None,
                        'author_location': user.location if user and hasattr(user, 'location') else None,
                        'retweet_count': tweet.public_metrics['retweet_count'] if hasattr(tweet, 'public_metrics') else 0,
                        'reply_count': tweet.public_metrics['reply_count'] if hasattr(tweet, 'public_metrics') else 0,
                        'like_count': tweet.public_metrics['like_count'] if hasattr(tweet, 'public_metrics') else 0,
                        'quote_count': tweet.public_metrics['quote_count'] if hasattr(tweet, 'public_metrics') else 0,
                        'lang': tweet.lang if hasattr(tweet, 'lang') else None,
                        'is_retweet': any(ref.type == 'retweeted' for ref in tweet.referenced_tweets) if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets else False,
                        'is_reply': any(ref.type == 'replied_to' for ref in tweet.referenced_tweets) if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets else False,
                        'is_quote': any(ref.type == 'quoted' for ref in tweet.referenced_tweets) if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets else False,
                        'query': query,
                        'collected_at': datetime.now().isoformat(),
                        'source': 'Twitter'
                    }
                    
                    tweets.append(tweet_data)
            
            self.logger.info(f"Récupéré {len(tweets)} tweets pour la requête '{query}'")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche de tweets pour '{query}': {e}")
        
        return tweets
    
    async def save_data(self, data: List[Dict[str, Any]]):
        """
        Sauvegarde les données dans un fichier JSON.
        
        Args:
            data (List[Dict[str, Any]]): Données à sauvegarder.
        """
        if not data:
            self.logger.warning("Aucune donnée à sauvegarder")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"twitter_{timestamp}.json"
        filepath = os.path.join(self.config['storage_path'], filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Données sauvegardées dans {filepath}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des données: {e}")
    
    async def run(self):
        """Exécute le processus de scraping pour Twitter."""
        if not self.client_v1 or not self.client_v2:
            self.logger.error("Clients Twitter non initialisés, impossible de continuer")
            return
        
        self.logger.info("Début du scraping de Twitter")
        all_data = []
        
        # Rechercher des tweets par requête
        for query in self.config['search_queries']:
            tweets = await self.search_tweets(query)
            all_data.extend(tweets)
            
            # Pause pour éviter de surcharger l'API
            await asyncio.sleep(2)
        
        # Limiter le nombre total de tweets
        if len(all_data) > self.config['tweet_limit']:
            all_data = all_data[:self.config['tweet_limit']]
        
        # Sauvegarder les données
        await self.save_data(all_data)
        
        self.logger.info(f"Scraping de Twitter terminé, {len(all_data)} tweets collectés")

if __name__ == "__main__":
    # Configuration du logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test du scraper
    async def main():
        scraper = TwitterScraper()
        await scraper.run()
    
    asyncio.run(main())
