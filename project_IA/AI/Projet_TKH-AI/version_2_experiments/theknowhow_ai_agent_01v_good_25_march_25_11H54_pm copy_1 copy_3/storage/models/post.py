"""
Modèles de données pour les posts
"""

from typing import Optional
from pydantic import BaseModel

class PostCreate(BaseModel):
    """Modèle pour la création d'un post"""
    id: str
    title: Optional[str] = None
    body: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    created_utc: float
    created_at: Optional[float] = None
    subreddit: Optional[str] = None
    author: Optional[str] = None
    author_id: Optional[str] = None
    medical_relevance_score: float
    urgency_score: float
    second_opinion_score: float
    sentiment_score: Optional[float] = None
    overall_score: Optional[float] = None
    category: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Post(PostCreate):
    """Modèle complet d'un post"""
    pass 