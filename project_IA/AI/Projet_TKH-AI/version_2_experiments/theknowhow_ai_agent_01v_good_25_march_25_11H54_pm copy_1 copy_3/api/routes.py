from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from storage.models.post import Post, PostCreate, PostUpdate, PostWithResponses
from scrapers.social_media.reddit_scraper import RedditScraper
from config.database import get_db_connection
import spacy

router = APIRouter()

# Initialisation de NLP
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"Impossible de charger le modèle NLP: {e}")
    nlp = None

# Initialisation du scraper Reddit
reddit_scraper = RedditScraper(nlp)

@router.get("/posts/", response_model=List[Post])
async def get_posts(
    subreddit: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = 0
):
    """
    Récupère les posts avec filtres optionnels
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM posts"
        params = []
        
        if subreddit:
            query += " WHERE subreddit = ?"
            params.append(subreddit)
            
        query += " ORDER BY created_utc DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        posts = cursor.fetchall()
        
        return [Post(**dict(zip([col[0] for col in cursor.description], post))) 
                for post in posts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}", response_model=PostWithResponses)
async def get_post(post_id: str):
    """
    Récupère un post spécifique avec ses réponses
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Récupérer le post
        cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post non trouvé")
            
        # Récupérer les réponses
        cursor.execute("SELECT * FROM responses WHERE post_id = ?", (post_id,))
        responses = cursor.fetchone()
        
        post_dict = dict(zip([col[0] for col in cursor.description], post))
        post_dict["responses"] = responses if responses else []
        
        return PostWithResponses(**post_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape/", response_model=List[Post])
async def scrape_subreddit(subreddit: str, limit: int = Query(100, le=1000)):
    """
    Scrape un subreddit et retourne les posts analysés
    """
    try:
        posts = reddit_scraper.scrape_subreddit(subreddit, limit)
        
        # Sauvegarder les posts dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for post in posts:
            cursor.execute("""
                INSERT OR REPLACE INTO posts 
                (id, title, body, url, created_utc, subreddit, author,
                 medical_relevance_score, urgency_score, second_opinion_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.id, post.title, post.body, post.url, post.created_utc,
                post.subreddit, post.author, post.medical_relevance_score,
                post.urgency_score, post.second_opinion_score
            ))
        
        conn.commit()
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 