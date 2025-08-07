"""
API principale FastAPI pour le système YAZAKI
Point d'entrée principal de l'API backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from .routes import health, upload, sheets, cleaning, processing, results
from ..utils.config import API_HOST, API_PORT
from ..utils.logger import setup_logger

# Configuration du logging
logger = setup_logger("yazaki_api")

# Création de l'application FastAPI
app = FastAPI(
    title="YAZAKI Component Processing System API",
    description="API pour le traitement des composants YAZAKI",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(sheets.router, prefix="/sheets", tags=["Sheets"])
app.include_router(cleaning.router, prefix="/cleaning", tags=["Cleaning"])
app.include_router(processing.router, prefix="/processing", tags=["Processing"])
app.include_router(results.router, prefix="/results", tags=["Results"])


@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'application"""
    logger.info("=" * 60)
    logger.info("YAZAKI Component Processing System API - v3.0.0")
    logger.info("=" * 60)
    logger.info("Features:")
    logger.info("- Clean architecture with services")
    logger.info("- Comprehensive error handling")
    logger.info("- Structured logging")
    logger.info("- Data validation")
    logger.info("- Multi-sheet Excel support")
    logger.info("- Data cleaning capabilities")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Événement d'arrêt de l'application"""
    logger.info("YAZAKI API shutting down...")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.get("/")
async def root():
    """Point d'entrée racine de l'API"""
    return {
        "message": "YAZAKI Component Processing System API",
        "version": "3.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "sheets": "/sheets",
            "cleaning": "/cleaning",
            "processing": "/processing",
            "results": "/results",
            "docs": "/docs"
        }
    }


def create_app() -> FastAPI:
    """Factory function pour créer l'application"""
    return app


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting YAZAKI API on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "app.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
