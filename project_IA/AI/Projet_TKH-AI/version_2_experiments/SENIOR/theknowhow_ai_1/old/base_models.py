"""
Modèles de données de base pour le projet.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SourceType(str, Enum):
    """Types de sources de données supportées."""
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    QUORA = "quora"
    FORUM = "forum"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    CUSTOM = "custom"

class ContentType(str, Enum):
    """Types de contenu supportés."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    MIXED = "mixed"

class DomainType(str, Enum):
    """Domaines d'application supportés."""
    MEDICAL = "medical"
    LEGAL = "legal"
    FINANCE = "finance"
    EDUCATION = "education"
    CUSTOM = "custom"

class BaseContent(BaseModel):
    """Modèle de base pour tout contenu."""
    id: str = Field(..., description="Identifiant unique du contenu")
    source_type: SourceType = Field(..., description="Type de source")
    content_type: ContentType = Field(..., description="Type de contenu")
    domain_type: DomainType = Field(..., description="Domaine d'application")
    raw_content: Dict[str, Any] = Field(..., description="Contenu brut")
    processed_content: Optional[Dict[str, Any]] = Field(None, description="Contenu traité")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")
    updated_at: datetime = Field(default_factory=datetime.now, description="Date de mise à jour")
    
    class Config:
        arbitrary_types_allowed = True

class BaseUser(BaseModel):
    """Modèle de base pour les utilisateurs."""
    id: str = Field(..., description="Identifiant unique de l'utilisateur")
    username: str = Field(..., description="Nom d'utilisateur")
    domain_type: DomainType = Field(..., description="Domaine d'expertise")
    credentials: Dict[str, Any] = Field(default_factory=dict, description="Informations d'identification")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")
    updated_at: datetime = Field(default_factory=datetime.now, description="Date de mise à jour")

class BaseInteraction(BaseModel):
    """Modèle de base pour les interactions."""
    id: str = Field(..., description="Identifiant unique de l'interaction")
    user_id: str = Field(..., description="Identifiant de l'utilisateur")
    content_id: str = Field(..., description="Identifiant du contenu")
    interaction_type: str = Field(..., description="Type d'interaction")
    domain_type: DomainType = Field(..., description="Domaine concerné")
    data: Dict[str, Any] = Field(..., description="Données de l'interaction")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")

class BaseAnalysis(BaseModel):
    """Modèle de base pour les analyses."""
    id: str = Field(..., description="Identifiant unique de l'analyse")
    content_id: str = Field(..., description="Identifiant du contenu analysé")
    domain_type: DomainType = Field(..., description="Domaine d'analyse")
    analysis_type: str = Field(..., description="Type d'analyse")
    results: Dict[str, Any] = Field(..., description="Résultats de l'analyse")
    confidence_score: float = Field(..., ge=0, le=1, description="Score de confiance")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")

class DomainConfig(BaseModel):
    """Configuration spécifique à un domaine."""
    domain_type: DomainType = Field(..., description="Type de domaine")
    name: str = Field(..., description="Nom du domaine")
    description: str = Field(..., description="Description du domaine")
    enabled_sources: List[SourceType] = Field(..., description="Sources activées")
    keywords: List[str] = Field(..., description="Mots-clés du domaine")
    rules: Dict[str, Any] = Field(..., description="Règles spécifiques")
    validation_criteria: Dict[str, Any] = Field(..., description="Critères de validation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")
    updated_at: datetime = Field(default_factory=datetime.now, description="Date de mise à jour") 