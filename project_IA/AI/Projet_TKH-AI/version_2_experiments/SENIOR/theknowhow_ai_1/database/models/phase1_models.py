"""
Modèles de données pour la Phase 1.
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 1001-1050 : modèles de données)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Post(Base):
    """Modèle pour les posts Reddit."""
    __tablename__ = 'posts'

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(String)
    url = Column(String)
    created_utc = Column(Float)
    subreddit = Column(String)
    author = Column(String)
    category = Column(String)
    second_opinion_score = Column(Float)
    urgency_score = Column(Float)
    medical_relevance_score = Column(Float)
    sentiment_score = Column(Float)
    overall_score = Column(Float)
    country = Column(String)
    city = Column(String)
    region = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    # Relations
    gcc_user = relationship("GCCUser", back_populates="post", uselist=False)
    responses = relationship("Response", back_populates="post")

    def __repr__(self):
        return f"<Post(id='{self.id}', title='{self.title[:30]}...', category='{self.category}')>"

class GCCUser(Base):
    """Modèle pour les utilisateurs du GCC."""
    __tablename__ = 'gcc_users'

    id = Column(Integer, primary_key=True)
    post_id = Column(String, ForeignKey('posts.id'))
    country = Column(String)
    city = Column(String)
    region = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(Float)

    # Relation
    post = relationship("Post", back_populates="gcc_user")

    def __repr__(self):
        return f"<GCCUser(id={self.id}, country='{self.country}', city='{self.city}')>"

class Response(Base):
    """Modèle pour les réponses aux posts."""
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True)
    post_id = Column(String, ForeignKey('posts.id'))
    response_text = Column(String)
    sent_time = Column(Float)
    response_status = Column(String)

    # Relation
    post = relationship("Post", back_populates="responses")

    def __repr__(self):
        return f"<Response(id={self.id}, post_id='{self.post_id}', status='{self.response_status}')>" 