# Explication du Système d'IA Médicale

## 1. Architecture Globale

Le système est divisé en deux phases principales :

### Phase 1 : Collecte des Données
- **Sources de données** :
  - Réseaux sociaux (Reddit, Twitter)
  - Forums médicaux (MedHelp, HealthBoards, etc.)
  - Sites web médicaux
- **Stockage** : Bases de données SQLite
- **Analyse** : Classification des données selon :
  - Pertinence médicale
  - Présence de symptômes
  - Présence de diagnostics
  - Présence de traitements

### Phase 2 : Entraînement et Utilisation
- **Préparation des données**
- **Entraînement du modèle**
- **Déploiement du bot**
- **Suivi des performances**

## 2. Processus Détaillé

### 2.1 Collecte des Données (Phase 1)
```python
# Exemple de structure de données collectées
{
    "id": "post_123",
    "source": "reddit",
    "subreddit": "AskDocs",
    "content": "J'ai mal à la tête depuis 3 jours",
    "medical_relevance": 0.95,
    "has_symptoms": true,
    "has_diagnosis": false,
    "has_treatment": false,
    "keywords": ["mal de tête", "douleur", "persistant"]
}
```

### 2.2 Préparation des Données (Phase 2)
La classe `TrainingDataLoader` :
1. Charge les données depuis la base SQLite
2. Filtre les posts médicaux pertinents
3. Transforme en paires d'entraînement

```python
# Exemple de paire d'entraînement
{
    "input": "Contexte: symptome\nQuestion: J'ai mal à la tête depuis 3 jours",
    "output": "Je comprends votre situation. Des maux de tête persistants nécessitent une attention médicale..."
}
```

### 2.3 Entraînement du Modèle
- **Division des données** :
  - 70% entraînement
  - 15% validation
  - 15% test
- **Processus d'entraînement** :
  - Fine-tuning du modèle de base
  - Optimisation des hyperparamètres
  - Validation des performances

### 2.4 Utilisation en Production
Le bot :
1. Surveille les subreddits médicaux
2. Détecte les posts pertinents
3. Génère des réponses appropriées
4. Respecte les règles des subreddits

## 3. Métriques de Performance

Le système suit plusieurs indicateurs :
- **Taux de détection** : Pourcentage de posts médicaux correctement identifiés
- **Temps de réponse** : Délai moyen pour générer une réponse
- **Qualité des réponses** : Pertinence et précision des réponses
- **Engagement** : Nombre d'interactions avec les utilisateurs

## 4. Problèmes Actuels et Solutions

### 4.1 Problème de Transformation des Données
Les données de la phase 1 ne sont pas encore correctement transformées pour l'entraînement.

### 4.2 Solution Proposée
Créer un script de transformation qui :
1. Lit les données de la base SQLite
2. Les transforme en format JSON
3. Les sauvegarde dans `fine_tuning/data/'

## 5. Sécurité et Conformité

Le système respecte :
- Les règles des subreddits
- La confidentialité des données
- La transparence sur sa nature d'IA
- Les bonnes pratiques médicales

## 6. Prochaines Étapes

1. Création du script de transformation des données
2. Optimisation du processus d'entraînement
3. Amélioration des métriques de performance
4. Extension à d'autres plateformes 