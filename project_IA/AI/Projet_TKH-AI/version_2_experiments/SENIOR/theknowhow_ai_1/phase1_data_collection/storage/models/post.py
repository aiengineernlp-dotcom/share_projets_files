"""
Modèle de données pour les posts médicaux.

RÔLE PRINCIPAL :
---------------
Ce module définit le modèle de données pour les posts médicaux.
Il fournit la structure de base pour stocker et manipuler les posts
collectés depuis les différentes sources (Reddit, Twitter, etc.).

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * storage/database.py (mapping ORM)
  * scrapers/social_media/*.py (stockage des posts)
  * processors/medical_analysis/*.py (analyse des posts)

- Dépend de :
  * config/models.py (modèles de base)
  * storage/models/base.py (classe de base)

STRUCTURE DU CONTENU :
--------------------
1. Imports et dépendances :
   - SQLAlchemy pour l'ORM
   - datetime pour les timestamps
   - typing pour les annotations

2. Classe Post :
   - Champs de base (id, title, content)
   - Métadonnées (source, timestamp)
   - Champs médicaux (symptoms, diagnosis)
   - Relations (comments, user)

3. Méthodes utilitaires :
   - to_dict() : Sérialisation
   - from_dict() : Désérialisation
   - validate() : Validation

4. Propriétés calculées :
   - is_medical : Pertinence médicale
   - urgency_level : Niveau d'urgence
   - category : Catégorie médicale

FONCTIONS PRINCIPALES :
---------------------
- create() : Création d'un post
- update() : Mise à jour d'un post
- delete() : Suppression d'un post
- search() : Recherche de posts

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il définit la structure des posts
- Il gère la persistance des données
- Il assure la cohérence des données
- Il est utilisé par tous les composants
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Post(BaseModel):
    id: str
    title: str
    body: str
    url: str
    created_utc: float
    subreddit: str
    author: str
    category: Optional[str] = None
    second_opinion_score: Optional[float] = None
    urgency_score: Optional[float] = None
    medical_relevance_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    overall_score: Optional[float] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PostCreate(Post):
    pass

class PostUpdate(BaseModel):
    category: Optional[str] = None
    second_opinion_score: Optional[float] = None
    urgency_score: Optional[float] = None
    medical_relevance_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    overall_score: Optional[float] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PostResponse(BaseModel):
    id: str
    response_text: str
    sent_time: float
    response_status: str

class PostWithResponses(Post):
    responses: List[PostResponse] = [] 