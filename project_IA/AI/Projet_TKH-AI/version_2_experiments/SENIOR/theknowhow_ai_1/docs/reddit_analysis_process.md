# Processus d'Analyse des Posts Reddit Médicaux

## 1. Collecte des Données

### 1.1 Sources de Données
- **Titre du post** : Le titre de la publication Reddit
- **Corps du texte** : Le contenu principal du post (selftext)
- **Métadonnées** : 
  - ID du post
  - Subreddit
  - Auteur
  - Date de création
  - Score (upvotes)
  - Nombre de commentaires

### 1.2 Combinaison des Données
```python
post_text = f"{post.title} {post.selftext}"
```
Le programme combine le titre et le corps du texte pour une analyse complète.

## 2. Analyse Linguistique

### 2.1 Détection de la Langue
```python
detected_lang = self.detect_language(post_text)
```
- Utilise TextBlob pour détecter automatiquement la langue
- Supporte plusieurs langues (en, fr, ar)
- Si la détection échoue, utilise la langue par défaut

### 2.2 Vérification de la Pertinence Médicale
```python
if not self.is_medical_related(post_text, detected_lang):
    continue
```
- Utilise des mots-clés médicaux spécifiques à chaque langue
- Exemples de mots-clés :
  - Anglais : symptom, diagnosis, treatment, doctor, hospital, pain, illness, disease, condition
  - Français : symptôme, diagnostic, traitement, médecin, hôpital, douleur, maladie, état
  - Arabe : عَرَض, تَشخِيص, عِلاج, طَبيب, مُستَشفى, أَلَم, مَرَض, حَالَة

## 3. Analyse Médicale Approfondie

### 3.1 Analyse par le Modèle NLP
```python
analysis = self.medical_analyzers[detected_lang].analyze_medical_text(post_text)
```
- Utilise spaCy pour l'analyse du texte
- Identifie les entités médicales :
  - Maladies (DISEASE)
  - Médicaments (DRUG)
  - Parties du corps (BODY_PART)
  - Conditions médicales (MEDICAL_CONDITION)

### 3.2 Détection des Éléments Médicaux
```python
medical_elements = self.has_medical_elements(analysis)
```
Vérifie la présence de :
- Symptômes (présence de DISEASE ou MEDICAL_CONDITION)
- Diagnostics (présence de DISEASE ou MEDICAL_CONDITION)
- Traitements (présence de DRUG)

## 4. Calcul des Scores

### 4.1 Scores de Base
```python
scores = {
    'medical_relevance_score': analysis['medical_score'],
    'urgency_score': analysis['urgency_score'],
    'second_opinion_score': analysis['second_opinion_score']
}
```
- Score de pertinence médicale
- Score d'urgence
- Score de besoin de second avis

### 4.2 Score Global
```python
overall_score = (
    scores['medical_relevance_score'] * SCORE_WEIGHTS['medical_relevance'] +
    scores['urgency_score'] * SCORE_WEIGHTS['urgency'] +
    scores['second_opinion_score'] * SCORE_WEIGHTS['second_opinion']
)
```
- Pondération des différents scores
- Ajustements basés sur les éléments médicaux présents :
  - +20% si symptômes présents
  - +10% si diagnostic présent
  - +10% si traitement présent

## 5. Catégorisation

### 5.1 Processus de Catégorisation
```python
post_category = self.categorize_post(scores, category)
```
Catégories possibles :
1. Medical Emergency (Urgence médicale)
   - Si score d'urgence > seuil urgent_help
2. Urgent Second Opinion (Second avis urgent)
   - Si score de second avis > seuil urgent_second_opinion
3. Priority Second Opinion (Second avis prioritaire)
   - Si score de second avis > seuil priority_second_opinion
4. Standard Second Opinion (Second avis standard)
   - Si score de second avis > seuil standard_second_opinion
5. Quick Consultation Recommended (Consultation rapide recommandée)
   - Par défaut

### 5.2 Seuils de Catégorisation
```python
CATEGORIZATION_THRESHOLDS = {
    'urgent_help': 0.8,
    'urgent_second_opinion': 0.7,
    'priority_second_opinion': 0.5,
    'standard_second_opinion': 0.3
}
```

## 6. Stockage des Données

### 6.1 Structure de la Base de Données
```sql
CREATE TABLE posts (
    id TEXT PRIMARY KEY,
    subreddit TEXT,
    title TEXT,
    body TEXT,
    author TEXT,
    created_utc INTEGER,
    score INTEGER,
    num_comments INTEGER,
    category TEXT,
    search_category TEXT,
    search_term TEXT,
    language TEXT,
    medical_relevance_score REAL,
    urgency_score REAL,
    second_opinion_score REAL,
    overall_score REAL,
    keywords TEXT,
    is_medical_related BOOLEAN,
    has_symptoms BOOLEAN,
    has_diagnosis BOOLEAN,
    has_treatment BOOLEAN
)
```

### 6.2 Sauvegarde des Données
- Enregistrement de toutes les informations analysées
- Mise à jour des posts existants si nécessaire
- Conservation des métadonnées importantes

## 7. Logging et Suivi

### 7.1 Informations Loguées
- Début de l'analyse
- Progression de la recherche
- Posts enregistrés avec leurs catégories
- Statistiques finales

### 7.2 Format des Logs
```
[Timestamp] - INFO - Post enregistré: [Titre]... Catégorie: [Catégorie], Score: [Score]
```

## 8. Gestion des Erreurs

### 8.1 Points de Contrôle
- Vérification de la connexion à l'API Reddit
- Validation des modèles NLP
- Gestion des erreurs de base de données

### 8.2 Gestion des Exceptions
- Erreurs de traitement des posts
- Erreurs de scraping des subreddits
- Erreurs d'analyse médicale 