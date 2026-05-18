"""
Module API pour l'intégration avec TheKnowHow.
"""
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from phase3.agent import ConversationalAgent
import jwt
from databases import Database
import json

# Configuration
SECRET_KEY = "votre_clé_secrète"  # À déplacer dans les variables d'environnement
DATABASE_URL = "sqlite:///./data/phase4_data.db"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modèles de données
class UserMessage(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    context: Dict[str, Any]
    timestamp: datetime

class User(BaseModel):
    username: str
    email: str

# Configuration de l'application
app = FastAPI(
    title="TheKnowHow Medical Assistant API",
    description="API pour l'assistant médical IA",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration du rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuration de la base de données
database = Database(DATABASE_URL)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration du logging
logger = logging.getLogger(__name__)

# Initialisation de l'agent
agent = ConversationalAgent()

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

async def init_db():
    """Initialise la base de données."""
    query = """
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        response TEXT NOT NULL,
        context JSON,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    await database.execute(query)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Vérifie et retourne l'utilisateur actuel."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = User(**payload)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")

@app.get("/")
async def root():
    """Point d'entrée de l'API."""
    return {"message": "Bienvenue sur l'API de l'assistant médical IA"}

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat(
    request: Request,
    message: UserMessage,
    current_user: User = Depends(get_current_user)
):
    """
    Point d'entrée pour le chat avec rate limiting et historique.
    """
    try:
        # Traitement du message
        response = agent.process_message(message.text)
        
        # Enregistrement dans l'historique
        query = """
        INSERT INTO conversations (user_id, message, response, context)
        VALUES (:user_id, :message, :response, :context)
        """
        await database.execute(
            query,
            values={
                "user_id": current_user.username,
                "message": message.text,
                "response": response["response"],
                "context": json.dumps(response["context"])
            }
        )
        
        # Ajout du timestamp
        response["timestamp"] = datetime.utcnow()
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du message : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[ChatResponse])
async def get_history(
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """Récupère l'historique des conversations."""
    query = """
    SELECT response, context, timestamp
    FROM conversations
    WHERE user_id = :user_id
    ORDER BY timestamp DESC
    LIMIT :limit
    """
    rows = await database.fetch_all(
        query,
        values={"user_id": current_user.username, "limit": limit}
    )
    return [ChatResponse(**row) for row in rows]

@app.delete("/history")
async def clear_history(current_user: User = Depends(get_current_user)):
    """Efface l'historique des conversations."""
    query = "DELETE FROM conversations WHERE user_id = :user_id"
    await database.execute(query, values={"user_id": current_user.username})
    return {"message": "Historique effacé avec succès"} 