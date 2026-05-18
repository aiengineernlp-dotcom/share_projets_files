"""
Point d'entrée principal de l'application FastAPI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.config import API_CONFIG
from app.scraping.coordinator import ScrapingCoordinator
from app.utils.logger import setup_logger

# Configuration du logger
logger = setup_logger("main")

# Création de l'application FastAPI
app = FastAPI(
    title=API_CONFIG["title"],
    description=API_CONFIG["description"],
    version=API_CONFIG["version"],
    docs_url=API_CONFIG["docs_url"],
    redoc_url=API_CONFIG["redoc_url"]
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du coordinateur de scraping
scraping_coordinator = ScrapingCoordinator()

@app.get("/")
async def root():
    """Route racine de l'API"""
    return {
        "message": "Bienvenue sur l'API Medical AI Agent",
        "version": API_CONFIG["version"],
        "docs_url": API_CONFIG["docs_url"]
    }

@app.post("/scraping/start")
async def start_scraping(source_types: Optional[List[str]] = None):
    """
    Démarre le scraping pour les types de sources spécifiés
    
    Args:
        source_types: Liste des types de sources à scraper. Si None, scrape tout.
    """
    try:
        await scraping_coordinator.start_scraping(source_types)
        return {"message": "Scraping démarré avec succès", "source_types": source_types or "all"}
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scraping/stop")
async def stop_scraping(source_types: Optional[List[str]] = None):
    """
    Arrête le scraping pour les types de sources spécifiés
    
    Args:
        source_types: Liste des types de sources à arrêter. Si None, arrête tout.
    """
    try:
        await scraping_coordinator.stop_scraping(source_types)
        return {"message": "Scraping arrêté avec succès", "source_types": source_types or "all"}
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt du scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scraping/status")
async def get_scraping_status():
    """Récupère le statut de tous les scrapers"""
    try:
        status = await scraping_coordinator.get_status()
        return {"status": status}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 