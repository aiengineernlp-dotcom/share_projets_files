# Guide de création du bot Reddit médical

## 📝 1. Création du compte Reddit

### Étape 1 : Créer un nouveau compte
1. Aller sur https://www.reddit.com/register
2. Choisir le nom d'utilisateur parmi les options suivantes :
   - `NoraFromKnowHow` : Prénom féminin, chaleureux et professionnel
   - `Eli_KnowHow` : Prénom mixte, simple et direct
   - `TheKnowHow_Jam` : Style décontracté mais professionnel
   - `CareWithKnowHow` : Accent sur l'aspect soin et expertise
   - `HealthKnowHow` : Option plus générique si préféré

   Critères de choix :
   - Lié à la marque "TheKnowHow"
   - Prénom pour un effet humain
   - Ne sonne pas comme un bot
   - Facile à retenir et professionnel
   - Évoque la confiance et l'expertise

3. Utiliser une adresse email dédiée
4. Choisir un mot de passe sécurisé

### Étape 2 : Configurer le profil
1. Ajouter une photo de profil :
   - Option 1 : Icône santé (cœur, stéthoscope, cerveau)
   - Option 2 : Illustration style flat d'une personne souriante
   - Style : sobre et professionnel
   - Format : carré, minimum 256x256 pixels

2. Rédiger la bio suivante :
   ```
   🧠 Passionné par la clarté médicale.
   🤝 Ici pour discuter santé, partager des expériences et aider ceux qui cherchent à mieux comprendre leur situation.
   ⚠️ Ce compte utilise un assistant IA formé à interagir sur Reddit autour de sujets médicaux. Il ne remplace aucun professionnel de santé.
   🌍 Pour ceux qui veulent y voir plus clair : theknowhow.ae
   ```

3. Ajouter un flair personnalisé si possible :
   - Texte : "Health Assistant"
   - Style : sobre et professionnel

## 🔑 2. Configuration de l'application Reddit

### Étape 1 : Créer une application
1. Aller sur https://www.reddit.com/prefs/apps
2. Cliquer sur "create another app..."
3. Remplir les informations :
   - Name: TheKnowHow Medical Bot
   - Type: script
   - Description: Bot assistant pour discussions médicales
   - About URL: https://theknowhow.ae
   - Redirect URI: http://localhost:8080

### Étape 2 : Récupérer les identifiants
1. Notez le `client_id` (sous le nom de l'application)
2. Notez le `client_secret`
3. Ces identifiants seront utilisés dans le fichier de configuration

## ⚙️ 3. Configuration du bot

### Étape 1 : Structure des dossiers
```
reddit_bot/
├── config/
│   └── config.json
├── nlp/
│   ├── analyzer.py
│   └── response_generator.py
├── utils/
│   └── logger.py
├── run_reddit_bot.py
└── requirements.txt
```

### Étape 2 : Fichier de configuration
```json
{
    "reddit": {
        "client_id": "VOTRE_CLIENT_ID",
        "client_secret": "VOTRE_CLIENT_SECRET",
        "username": "VOTRE_NOM_UTILISATEUR",
        "password": "VOTRE_MOT_DE_PASSE",
        "user_agent": "TheKnowHow Medical Bot/1.0",
        "subreddits": ["AskDocs", "medical_advice"],
        "min_delay": 120,
        "max_delay": 300,
        "max_posts_per_iteration": 3,
        "max_replies_per_iteration": 1
    },
    "nlp": {
        "model_name": "microsoft/BioGPT-large",
        "min_confidence": 0.7,
        "max_response_length": 1000
    }
}
```

### Étape 3 : Installation des dépendances
```bash
pip install -r requirements.txt
```

## 🤖 4. Code du bot

### Étape 1 : Imports nécessaires
```python
import praw
import logging
from typing import Dict, List
import time
import random
from pathlib import Path
import json
```

### Étape 2 : Classe RedditManager
```python
class RedditManager:
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
```

### Étape 3 : Méthodes principales
```python
def monitor_subreddits(self):
    """Surveille les subreddits pour trouver des opportunités."""
    relevant_posts = []
    for subreddit_name in self.config['reddit']['subreddits']:
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = list(subreddit.new(limit=50))
        # Analyse des posts...
    return relevant_posts

def engage_with_post(self, post: Dict, response: str):
    """Répond à un post avec gestion des délais."""
    delay = random.uniform(
        self.config['reddit']['min_delay'],
        self.config['reddit']['max_delay']
    )
    time.sleep(delay)
    # Post de la réponse...
```

## 🧪 5. Test du bot

### Étape 1 : Test initial
1. Lancer le bot en mode test
2. Vérifier les logs
3. Tester avec un seul subreddit

### Étape 2 : Vérifications
- Authentification fonctionnelle
- Détection des posts pertinents
- Génération des réponses
- Respect des délais

### Étape 3 : Ajustements
- Modifier les délais si nécessaire
- Ajuster les critères de pertinence
- Optimiser les templates de réponses

## 📊 6. Monitoring et maintenance

### Étape 1 : Configuration des logs
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_bot.log'),
        logging.StreamHandler()
    ]
)
```

### Étape 2 : Métriques à surveiller
- Nombre de posts analysés
- Nombre de réponses postées
- Taux de succès des réponses
- Temps moyen entre les réponses

### Étape 3 : Maintenance régulière
- Vérification quotidienne des logs
- Analyse des performances
- Mise à jour des configurations

## ⚠️ 7. Sécurité et bonnes pratiques

### Étape 1 : Protection des identifiants
- Ne jamais commiter les identifiants
- Utiliser des variables d'environnement
- Changer régulièrement les mots de passe

### Étape 2 : Respect des limites
- Ne pas dépasser les limites d'API
- Respecter les règles des subreddits
- Gérer les erreurs et les exceptions

### Étape 3 : Backup et récupération
- Sauvegarder régulièrement la configuration
- Prévoir un plan de récupération
- Garder des logs détaillés 