from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from storage.models.post import Post, PostResponse
from config.database import get_db_connection
from datetime import datetime

router = APIRouter()

@router.get("/urgent-posts/", response_model=List[Post])
async def get_urgent_posts(
    threshold: float = Query(0.3, ge=0.0, le=1.0),
    limit: int = Query(100, le=1000)
):
    """
    Récupère les posts urgents basés sur le score d'urgence
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM posts 
            WHERE urgency_score >= ? 
            ORDER BY urgency_score DESC 
            LIMIT ?
        """, (threshold, limit))
        
        posts = cursor.fetchall()
        return [Post(**dict(zip([col[0] for col in cursor.description], post))) 
                for post in posts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medical-posts/", response_model=List[Post])
async def get_medical_posts(
    threshold: float = Query(0.3, ge=0.0, le=1.0),
    limit: int = Query(100, le=1000)
):
    """
    Récupère les posts médicaux basés sur le score de pertinence médicale
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM posts 
            WHERE medical_relevance_score >= ? 
            ORDER BY medical_relevance_score DESC 
            LIMIT ?
        """, (threshold, limit))
        
        posts = cursor.fetchall()
        return [Post(**dict(zip([col[0] for col in cursor.description], post))) 
                for post in posts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/respond", response_model=PostResponse)
async def respond_to_post(
    post_id: str,
    response_text: str
):
    """
    Ajoute une réponse à un post
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier si le post existe
        cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Post non trouvé")
        
        # Ajouter la réponse
        response = PostResponse(
            id=post_id,
            response_text=response_text,
            sent_time=datetime.now().timestamp(),
            response_status="SENT"
        )
        
        cursor.execute("""
            INSERT INTO responses (post_id, response_text, sent_time, response_status)
            VALUES (?, ?, ?, ?)
        """, (
            response.id, response.response_text,
            response.sent_time, response.response_status
        ))
        
        conn.commit()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 