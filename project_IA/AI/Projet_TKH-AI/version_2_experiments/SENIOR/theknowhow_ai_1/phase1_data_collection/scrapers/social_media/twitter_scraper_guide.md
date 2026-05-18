# Guide d'Utilisation du Scraper Twitter

## Vue d'ensemble

Le scraper Twitter est conçu pour collecter des posts médicaux à partir de Twitter en utilisant des hashtags et mots-clés spécifiques. Il analyse chaque tweet pour déterminer sa pertinence médicale, son niveau d'urgence et son besoin de second avis médical.

## Prérequis

1. **Clés API Twitter**
   - Bearer Token
   - Consumer Key
   - Consumer Secret
   - Access Token
   - Access Token Secret

2. **Dépendances Python**
   ```bash
   pip install tweepy spacy tqdm
   python -m spacy download en_core_web_sm
   ```

## Configuration

1. **Configurer les clés API**
   - Ouvrir `config/twitter_config.py`
   - Remplir les champs dans `TWITTER_CONFIG`

2. **Personnaliser les paramètres de recherche**
   - Modifier `MEDICAL_HASHTAGS` pour cibler des hashtags spécifiques
   - Ajuster `SEARCH_PARAMS` pour modifier les critères de recherche
   - Personnaliser `MEDICAL_KEYWORDS` pour le filtrage des tweets

## Utilisation

1. **Lancer le scraper**
   ```bash
   PYTHONPATH=$PYTHONPATH:. python phase1_data_collection/scrapers/social_media/twitter_scraper.py
   ```

2. **Résultats**
   - Les tweets sont stockés dans `data/database/sqlite/twitter.db`
   - Chaque tweet est analysé et catégorisé
   - Les scores suivants sont calculés :
     - Score de pertinence médicale
     - Score d'urgence
     - Score de besoin de second avis
     - Score global

## Structure de la Base de Données

La base de données contient une table principale `twitter_posts` avec les champs suivants :
- `id`: Identifiant unique
- `tweet_id`: ID du tweet original
- `author_id`: ID de l'auteur
- `author_username`: Nom d'utilisateur de l'auteur
- `title`: Première ligne ou début du tweet
- `body`: Contenu complet du tweet
- `created_utc`: Date de création
- `score`: Nombre de likes
- `retweet_count`: Nombre de retweets
- `reply_count`: Nombre de réponses
- `quote_count`: Nombre de citations
- Scores d'analyse :
  - `medical_relevance_score`
  - `urgency_score`
  - `second_opinion_score`
  - `overall_score`
- `category`: Catégorie attribuée
- `language`: Langue détectée
- `keywords`: Mots-clés extraits
- `search_term`: Hashtag utilisé pour trouver le tweet

## Surveillance et Logs

- Les logs sont enregistrés avec différents niveaux (INFO, ERROR)
- Consultez les logs pour suivre :
  - Le nombre de tweets collectés
  - Les erreurs éventuelles
  - Les statistiques de catégorisation

## Maintenance

1. **Mise à jour des hashtags**
   - Modifier `MEDICAL_HASHTAGS` dans `config/twitter_config.py`
   - Ajouter/supprimer des hashtags selon les besoins

2. **Ajustement des scores**
   - Les seuils de catégorisation peuvent être ajustés dans le code
   - Les poids des différents scores peuvent être modifiés

## Dépannage

1. **Erreurs d'API**
   - Vérifier les clés API
   - Respecter les limites de rate limiting

2. **Problèmes de base de données**
   - Vérifier les permissions du fichier
   - S'assurer que le schéma est correctement initialisé

3. **Problèmes de collecte**
   - Vérifier la connexion Internet
   - Confirmer que les hashtags sont actifs
   - Ajuster les paramètres de recherche 