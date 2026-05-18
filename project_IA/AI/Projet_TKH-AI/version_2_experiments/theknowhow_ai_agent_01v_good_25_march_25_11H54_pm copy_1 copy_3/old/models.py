from pydantic import BaseModel
from typing import Optional, List

class PostResponse(BaseModel):
    id: str
    title: str
    url: str
    created_utc: float
    subreddit: str
    category: str
    second_opinion_score: float
    urgency_score: float
    medical_relevance_score: float
    sentiment_score: float
    overall_score: float
    body_excerpt: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ScrapingRequest(BaseModel):
    subreddit: str
    query: str
    limit: int = 100

class AnalysisRequest(BaseModel):
    title: str
    body: Optional[str] = ""

class ConversationRequest(BaseModel):
    post_id: str
    user_id: str
    message: str

class ConversationResponse(BaseModel):
    message: str
    response: str
    timestamp: float
    sentiment_score: float 