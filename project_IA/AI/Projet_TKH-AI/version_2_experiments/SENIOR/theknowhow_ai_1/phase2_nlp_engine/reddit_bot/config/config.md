# Documentation de la Configuration

## Section Reddit

### Identifiants
- `client_id` : ID client de l'application Reddit
- `client_secret` : Clé secrète de l'application
- `username` : Nom d'utilisateur du bot (Soft-Teaching5212)
- `password` : Mot de passe du compte
- `user_agent` : Description du bot

### Surveillance
- `subreddits` : Liste des subreddits à surveiller (AskDocs, medical_advice)

### Délais
- `min_delay` : 120 secondes (2 minutes) - Délai minimum entre les actions
- `max_delay` : 360 secondes (6 minutes) - Délai maximum entre les actions

### Limites
- `max_posts_per_iteration` : 2 - Nombre maximum de posts traités par cycle
- `max_replies_per_iteration` : 1 - Nombre maximum de réponses par cycle

## Section NLP

### Modèle
- `model_name` : microsoft/BioGPT-large - Modèle médical utilisé
- `min_confidence` : 0.7 - Niveau de confiance minimum pour les réponses
- `max_response_length` : 1000 - Longueur maximale des réponses

## Section Engagement

### Critères
- `min_upvotes` : 1 - Nombre minimum d'upvotes pour considérer un post
- `min_comments` : 0 - Nombre minimum de commentaires pour considérer un post

### Mots-clés
Liste des mots-clés pour détecter les demandes de second avis :
- second opinion
- not sure
- confused
- different doctor
- another opinion

## Section Redirection

### Site
- `website` : TheKnowHow.ae - Site vers lequel rediriger

### Phrases de redirection
Phrases utilisées pour la redirection subtile :
- You might find more information at
- For additional resources, check out
- There's a helpful platform called 