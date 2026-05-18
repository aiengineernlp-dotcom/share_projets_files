"""Routes API pour l'application."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime

from src.phase1.database_manager import DatabaseManager
from src.phase2.text_processor import TextProcessor
from src.phase3.classifier import AdvancedClassifier
from src.phase4.evaluator import ModelEvaluator

router = APIRouter()

# Dépendances
def get_db():
    return DatabaseManager("data/phase1_data.db")

def get_text_processor():
    return TextProcessor()

def get_classifier():
    return AdvancedClassifier()

def get_evaluator():
    return ModelEvaluator()

# Routes de la Phase 1
@router.get("/posts", response_model=List[Dict[str, Any]])
async def get_posts(db: DatabaseManager = Depends(get_db), limit: int = 10):
    """Récupère les posts les plus récents."""
    return db.get_posts(limit)

@router.post("/scrape")
async def scrape_posts(subreddit: str, query: str, limit: int = 10, db: DatabaseManager = Depends(get_db)):
    """Lance le scraping de posts Reddit."""
    try:
        posts_count = scraper.scrape_subreddit(subreddit, query, limit, db)
        return {"message": f"{posts_count} nouveaux posts ont été récupérés"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Routes de la Phase 2
@router.post("/analyze/text")
async def analyze_text(text: str, processor: TextProcessor = Depends(get_text_processor)):
    """Analyse un texte avec le processeur de texte."""
    try:
        return {
            "processed_text": processor.preprocess(text),
            "keywords": processor.extract_keywords(text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Routes de la Phase 3
@router.post("/classify")
async def classify_text(text: str, classifier: AdvancedClassifier = Depends(get_classifier)):
    """Classifie un texte avec le classificateur avancé."""
    try:
        return {
            "category": classifier.predict(text),
            "probabilities": classifier.predict_proba(text).tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Routes de la Phase 4
@router.get("/evaluation")
async def get_evaluation(evaluator: ModelEvaluator = Depends(get_evaluator)):
    """Récupère les résultats d'évaluation des modèles."""
    try:
        return evaluator.generate_evaluation_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 