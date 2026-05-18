"""
Module de base de données.
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 951-1100 : gestion de la base de données)
"""

from .connection import get_db_connection, init_database, execute_query, execute_many
from .models.phase1_models import Base, Post, GCCUser, Response
from .schemas.phase1_schemas import (
    PostBase, PostCreate, PostResponse,
    GCCUserBase, GCCUserCreate, GCCUserResponse,
    ResponseBase, ResponseCreate, ResponseResponse,
    StatsResponse, GCCStatsResponse, AfricanStatsResponse
)

__all__ = [
    # Connexion
    'get_db_connection',
    'init_database',
    'execute_query',
    'execute_many',
    
    # Modèles
    'Base',
    'Post',
    'GCCUser',
    'Response',
    
    # Schémas
    'PostBase',
    'PostCreate',
    'PostResponse',
    'GCCUserBase',
    'GCCUserCreate',
    'GCCUserResponse',
    'ResponseBase',
    'ResponseCreate',
    'ResponseResponse',
    'StatsResponse',
    'GCCStatsResponse',
    'AfricanStatsResponse'
] 