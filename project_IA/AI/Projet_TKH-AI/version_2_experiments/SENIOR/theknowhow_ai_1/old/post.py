"""Modèle de données pour les posts."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Post(BaseModel):
    """Modèle de données pour un post Reddit."""
    id: str = Field(..., description="Identifiant unique du post")
    title: str = Field(..., description="Titre du post")
    content: str = Field(..., description="Contenu du post")
    author: str = Field(..., description="Auteur du post")
    created_utc: float = Field(..., description="Timestamp de création")
    score: float = Field(..., description="Score du post (0-1)")
    category: str = Field(..., description="Catégorie du post (Urgent/Non-Urgent)")
    keywords: List[str] = Field(default_factory=list, description="Mots-clés extraits")
    sentiment: Optional[float] = Field(None, description="Score de sentiment (-1 à 1)")
    entities: List[str] = Field(default_factory=list, description="Entités médicales détectées")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "abc123",
                "title": "Question médicale urgente",
                "content": "J'ai des symptômes de...",
                "author": "user123",
                "created_utc": 1647123456.789,
                "score": 0.85,
                "category": "Urgent",
                "keywords": ["symptômes", "fièvre", "douleur"],
                "sentiment": -0.5,
                "entities": ["COVID-19", "Paracétamol"]
            }
        } 