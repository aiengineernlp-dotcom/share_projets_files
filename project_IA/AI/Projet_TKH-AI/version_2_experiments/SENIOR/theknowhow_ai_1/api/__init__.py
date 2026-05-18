from fastapi import FastAPI
from .routes import router as main_router
from .endpoints import router as endpoints_router

app = FastAPI(
    title="Phase 1 - API de Collecte et Analyse",
    description="API pour la collecte et l'analyse des données médicales",
    version="1.0.0"
)

# Inclure les routers
app.include_router(main_router, prefix="/api/v1")
app.include_router(endpoints_router, prefix="/api/v1") 