# Bonnes pratiques pour le bot Reddit médical

## 🔐 1. Transparence & éthique

### Configuration du compte
- Créer un compte distinct pour le bot
- Bio claire : "Ce compte utilise un modèle d'IA pour discuter autour des sujets médicaux. Il ne remplace pas un professionnel de santé."
- Nom non-bot : PatientInsight, CareHelperAI, SecondThoughtsBot
- Photo de profil neutre et professionnelle
- Flair personnalisé si possible

### Engagement initial
- Participer à 2-3 posts manuellement avant l'automatisation
- Montrer une présence humaine et naturelle
- Établir une réputation positive

## 🕰 2. Gestion du temps et des limites

### Délais entre les réponses
```python
# Configuration recommandée
min_delay = 120  # 2 minutes minimum
max_delay = 300  # 5 minutes maximum
time.sleep(random.uniform(min_delay, max_delay))
```

### Limites quotidiennes
- Maximum 30 commentaires par jour au début
- Augmenter progressivement après 1-2 semaines
- Ne jamais dépasser 50 commentaires par jour

## 🧠 3. Variété des réponses

### Templates de réponses
```python
response_templates = [
    {
        "context": "doute diagnostic",
        "templates": [
            "Je comprends ce que tu ressens. C'est difficile de faire confiance après un premier diagnostic.",
            "Tu n'es pas seul·e à douter d'un premier avis médical, c'est très courant.",
            "C'est totalement normal d'avoir envie d'un deuxième regard sur ton cas."
        ]
    },
    {
        "context": "demande conseil",
        "templates": [
            "Je peux comprendre ton inquiétude. As-tu pensé à demander un second avis ?",
            "C'est une bonne idée de chercher d'autres perspectives sur ta situation.",
            "Ton questionnement est tout à fait légitime dans ce cas."
        ]
    }
]
```

### Personnalisation
- Adapter le ton selon le contexte
- Utiliser des synonymes et variations
- Éviter les réponses identiques

## 📨 4. Gestion des liens externes

### Stratégie de redirection
1. Première réponse : conseil général sans lien
2. Deuxième interaction : mention subtile du site
3. Troisième interaction : lien direct si pertinent

### Exemples de phrases
- "Tu peux peut-être voir ce qu'ils disent sur TheKnowHow.ae, ça m'a aidé à y voir plus clair."
- "J'ai trouvé des informations intéressantes sur TheKnowHow.ae qui pourraient t'aider."
- "Sur TheKnowHow.ae, ils abordent ce sujet de manière détaillée."

## 👀 5. Choix des subreddits

### Subreddits recommandés
1. r/medical_advice (peu modéré)
2. r/HealthAnxiety (communauté supportive)
3. r/AskDocs (modéré, commencer doucement)

### Règles à respecter
- Lire les règles de chaque subreddit
- Respecter les interdictions de liens externes
- Adapter le ton à chaque communauté

## 🛡 6. Surveillance et sécurité

### Monitoring des réponses
```python
def monitor_response(comment):
    score = comment.score
    if score < -2:  # Trop de downvotes
        return "disable_bot"
    elif comment.removed:  # Commentaire supprimé
        return "change_strategy"
    return "continue"
```

### Actions correctives
- Désactiver temporairement en cas de downvotes
- Modifier la stratégie si nécessaire
- Garder un log des incidents

## 💬 7. Gestion des accusations de bot

### Réponses préparées
```python
bot_accusation_responses = [
    "J'utilise une IA pour enrichir les discussions santé, mais je suis là pour aider, pas pour remplacer un pro.",
    "Je suis un assistant IA formé sur des discussions médicales Reddit, si ça dérange je peux quitter le thread.",
    "Mon objectif est d'aider à trouver des informations pertinentes, pas de remplacer un avis médical professionnel."
]
```

## 📊 8. Métriques de performance

### À surveiller
- Taux d'upvotes/downvotes
- Nombre de réponses supprimées
- Temps moyen entre les réponses
- Nombre de conversions vers le site

### Seuils d'alerte
- Score moyen < 0 : revoir la stratégie
- Plus de 10% de réponses supprimées : pause immédiate
- Taux de conversion < 1% : optimiser les messages

## 🔄 9. Maintenance régulière

### Tâches quotidiennes
- Vérifier les logs d'erreurs
- Analyser les métriques
- Ajuster les délais si nécessaire
- Mettre à jour les templates

### Tâches hebdomadaires
- Revue des performances
- Mise à jour des mots-clés
- Optimisation des réponses
- Sauvegarde des configurations

## ⚠️ 10. Signaux d'alerte

### À surveiller
- Messages de modération
- Plaintes d'utilisateurs
- Baisse soudaine des performances
- Changements dans les règles des subreddits

### Actions immédiates
- Pause du bot
- Analyse de la situation
- Consultation des modérateurs
- Ajustement de la stratégie 