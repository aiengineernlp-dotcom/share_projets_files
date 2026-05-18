# Bot Reddit pour Second Avis Médical

Bot capable d'interagir naturellement sur Reddit, de détecter les opportunités de second avis médical, et de rediriger subtilement les utilisateurs vers TheKnowHow.ae.

## Structure

```
reddit_bot/
├── config/
│   └── config.json         # Configuration du bot
├── nlp/
│   ├── analyzer.py         # Analyse des posts
│   └── response_generator.py # Génération des réponses
├── utils/
│   └── __init__.py
├── reddit_manager.py       # Gestion des interactions Reddit
└── run_reddit_bot.py       # Point d'entrée principal
```

## Configuration

1. Créez un fichier `credentials.json` dans le dossier `config/` avec vos identifiants Reddit :
```json
{
    "client_id": "votre_client_id",
    "client_secret": "votre_client_secret",
    "username": "votre_username",
    "password": "votre_password",
    "user_agent": "votre_user_agent"
}
```

2. Ajustez les paramètres dans `config.json` selon vos besoins.

## Installation

1. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

Lancez le bot :
```bash
python run_reddit_bot.py
```

## Fonctionnalités

- Détection automatique des demandes de second avis
- Réponses naturelles et personnalisées
- Redirection subtile vers TheKnowHow.ae
- Respect des limites de taux Reddit
- Gestion des erreurs et logging 