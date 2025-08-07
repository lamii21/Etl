"""
Routes API pour le traitement des données
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from ...core.processors.lookup_processor import EnhancedLookupProcessor
from ...utils.logger import setup_logger

logger = setup_logger("yazaki_api_processing")
router = APIRouter()

# Processeur de lookup
lookup_processor = EnhancedLookupProcessor()

class ProcessingRequest(BaseModel):
    """Requête de traitement"""
    filename: str
    sheet_name: str
    master_bom_path: Optional[str] = "data/Master_BOM_Real.xlsx"
    project_column_hint: Optional[str] = None
    processing_options: Optional[Dict[str, Any]] = None

@router.post("/start")
async def start_processing(request: ProcessingRequest):
    """
    Démarre le traitement d'un fichier
    """
    try:
        file_path = Path("storage/uploads") / request.filename
        master_bom_path = Path(request.master_bom_path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier d'entrée non trouvé")
        
        if not master_bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouvé")
        
        logger.info(f"Starting processing for {request.filename}")
        
        # Générer un ID de traitement
        processing_id = str(uuid.uuid4())
        
        # Démarrer le traitement
        processing_result = await lookup_processor.process_file(
            input_file=str(file_path),
            sheet_name=request.sheet_name,
            master_bom_file=str(master_bom_path),
            project_hint=request.project_column_hint,
            processing_id=processing_id,
            options=request.processing_options or {}
        )
        
        return JSONResponse({
            "success": True,
            "data": {
                "processing_id": processing_id,
                "filename": request.filename,
                "sheet_name": request.sheet_name,
                "status": "started",
                "start_time": datetime.now().isoformat(),
                "result": processing_result
            }
        })
        
    except Exception as e:
        logger.error(f"Error starting processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")

@router.get("/status/{processing_id}")
async def get_processing_status(processing_id: str):
    """
    Obtient le statut d'un traitement
    """
    try:
        # TODO: Implémenter le suivi des traitements en cours
        # Pour l'instant, retourner un statut basique
        
        return JSONResponse({
            "success": True,
            "data": {
                "processing_id": processing_id,
                "status": "completed",  # Temporaire
                "progress": 100
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting processing status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/analyze-master-bom")
async def analyze_master_bom(master_bom_path: Optional[str] = "data/Master_BOM_Real.xlsx"):
    """
    Analyse le Master BOM
    """
    try:
        bom_path = Path(master_bom_path)
        
        if not bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouvé")
        
        logger.info(f"Analyzing Master BOM: {master_bom_path}")
        
        # Analyser le Master BOM
        analysis_result = await lookup_processor.analyze_master_bom(str(bom_path))
        
        return JSONResponse({
            "success": True,
            "data": {
                "master_bom_path": master_bom_path,
                "analysis": analysis_result
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing Master BOM: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@router.post("/suggest-columns")
async def suggest_project_columns(request: ProcessingRequest):
    """
    Suggère les colonnes de projet pour le lookup
    """
    try:
        master_bom_path = Path(request.master_bom_path)
        
        if not master_bom_path.exists():
            raise HTTPException(status_code=404, detail="Master BOM non trouvé")
        
        logger.info(f"Suggesting columns for project hint: {request.project_column_hint}")
        
        # Suggérer les colonnes
        suggestions = await lookup_processor.suggest_project_columns(
            str(master_bom_path),
            request.project_column_hint
        )
        
        return JSONResponse({
            "success": True,
            "data": {
                "project_hint": request.project_column_hint,
                "suggestions": suggestions
            }
        })
        
    except Exception as e:
        logger.error(f"Error suggesting columns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suggestion: {str(e)}")

@router.delete("/cancel/{processing_id}")
async def cancel_processing(processing_id: str):
    """
    Annule un traitement en cours
    """
    try:
        # TODO: Implémenter l'annulation des traitements
        logger.info(f"Cancelling processing: {processing_id}")
        
        return JSONResponse({
            "success": True,
            "message": f"Traitement {processing_id} annulé"
        })
        
    except Exception as e:
        logger.error(f"Error cancelling processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'annulation: {str(e)}")
