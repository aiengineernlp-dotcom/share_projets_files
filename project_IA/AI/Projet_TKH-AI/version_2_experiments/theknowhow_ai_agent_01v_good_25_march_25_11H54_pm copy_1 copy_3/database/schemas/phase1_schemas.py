"""
Schémas de validation pour la Phase 1.
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 1051-1100 : schémas de validation)
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class PostBase(BaseModel):
    """Schéma de base pour les posts."""
    title: str
    body: Optional[str] = None
    url: Optional[str] = None
    created_utc: float
    subreddit: str
    author: str
    category: str
    second_opinion_score: float = Field(ge=0.0, le=1.0)
    urgency_score: float = Field(ge=0.0, le=1.0)
    medical_relevance_score: float = Field(ge=0.0, le=1.0)
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=1.0)
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

class PostCreate(PostBase):
    """Schéma pour la création d'un post."""
    id: str

class PostResponse(PostBase):
    """Schéma pour la réponse d'un post."""
    id: str
    body_excerpt: Optional[str] = None

    class Config:
        from_attributes = True

class GCCUserBase(BaseModel):
    """Schéma de base pour les utilisateurs GCC."""
    country: str
    city: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    created_at: float

class GCCUserCreate(GCCUserBase):
    """Schéma pour la création d'un utilisateur GCC."""
    post_id: str

class GCCUserResponse(GCCUserBase):
    """Schéma pour la réponse d'un utilisateur GCC."""
    id: int
    post_id: str

    class Config:
        from_attributes = True

class ResponseBase(BaseModel):
    """Schéma de base pour les réponses."""
    response_text: str
    sent_time: float
    response_status: str

class ResponseCreate(ResponseBase):
    """Schéma pour la création d'une réponse."""
    post_id: str

class ResponseResponse(ResponseBase):
    """Schéma pour la réponse d'une réponse."""
    id: int
    post_id: str

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    """Schéma pour les statistiques."""
    total_posts: int
    categories: dict
    average_score: float
    top_subreddits: List[dict]

class GCCStatsResponse(BaseModel):
    """Schéma pour les statistiques GCC."""
    total_gcc_users: int
    countries: dict
    cities: dict
    average_score: float

class AfricanStatsResponse(BaseModel):
    """Schéma pour les statistiques africaines."""
    total_african_countries: int
    total_african_posts: int
    regions: dict 