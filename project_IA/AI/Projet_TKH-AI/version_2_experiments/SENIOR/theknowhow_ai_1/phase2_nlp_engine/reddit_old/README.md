# Bot Reddit - Structure du Projet

## Structure des Dossiers

```
reddit/
├── bot/                    # Code principal du bot
│   ├── main.py            # Point d'entrée du bot
│   └── reddit_manager.py  # Gestionnaire Reddit
├── nlp/                   # Composants NLP
│   ├── analyzer.py        # Analyse des posts
│   └── response_generator.py # Génération des réponses
├── config/                # Configuration
│   └── config.json       # Configuration du bot
├── tests/                 # Tests
├── data/                  # Données
└── utils/                 # Utilitaires
```

## Fichiers Principaux

1. **bot/main.py**
   - Point d'entrée du bot
   - Gestion du cycle de vie
   - Coordination des composants

2. **bot/reddit_manager.py**
   - Interaction avec l'API Reddit
   - Gestion des posts et réponses
   - Respect des limites d'API

3. **nlp/analyzer.py**
   - Analyse des posts
   - Détection des opportunités
   - Évaluation de la pertinence

4. **nlp/response_generator.py**
   - Génération des réponses
   - Personnalisation des messages
   - Gestion des templates

5. **config/config.json**
   - Configuration du bot
   - Paramètres Reddit
   - Templates de réponses

# Bot Reddit pour Assistance Médicale

Ce bot surveille les subreddits médicaux et engage des conversations avec les utilisateurs qui posent des questions médicales.

## Prérequis

- Python 3.8+
- Compte Reddit avec les permissions appropriées
- Modèle Ollama configuré et en cours d'exécution

## Installation

1. Clonez le dépôt
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez le fichier `config.json` avec vos informations Reddit :
```json
{
    "client_id": "votre_client_id",
    "client_secret": "votre_client_secret",
    "username": "votre_nom_utilisateur",
    "password": "votre_mot_de_passe",
    "user_agent": "votre_user_agent"
}
```

## Utilisation

Pour lancer le bot :

```bash
python run_reddit_bot.py
```

Le bot va :
- Surveiller les subreddits configurés
- Détecter les posts pertinents
- Générer des réponses appropriées
- Engager la conversation avec les utilisateurs

## Configuration

Vous pouvez personnaliser le comportement du bot en modifiant le fichier `config.json` :

- `subreddits_to_monitor` : Liste des subreddits à surveiller
- `medical_keywords` : Mots-clés pour détecter les posts pertinents
- `engagement_parameters` : Paramètres pour l'engagement (délais, limites, etc.)

## Logs

Les logs sont enregistrés dans `reddit_bot.log` et affichés dans la console.

## Sécurité

- Ne partagez jamais vos informations d'identification Reddit
- Respectez les règles de Reddit et les limites d'API
- Soyez transparent sur le fait qu'il s'agit d'un bot

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt. 