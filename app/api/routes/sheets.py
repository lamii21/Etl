"""
Routes API pour la gestion des feuilles Excel
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Optional

from ...core.services.sheet_service import SheetService
from ...utils.logger import setup_logger

logger = setup_logger("yazaki_api_sheets")
router = APIRouter()

# Service de gestion des feuilles
sheet_service = SheetService()

@router.get("/analyze/{filename}")
async def analyze_sheets(filename: str):
    """
    Analyse les feuilles d'un fichier Excel
    """
    try:
        file_path = Path("storage/uploads") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        logger.info(f"Analyzing sheets for file: {filename}")
        
        # Analyser les feuilles
        sheets_info = await sheet_service.analyze_sheets(str(file_path))
        
        return JSONResponse({
            "success": True,
            "data": {
                "filename": filename,
                "sheets": [sheet.dict() for sheet in sheets_info]
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing sheets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@router.get("/preview/{filename}/{sheet_name}")
async def preview_sheet(filename: str, sheet_name: str, rows: Optional[int] = 10):
    """
    Aperçu d'une feuille Excel
    """
    try:
        file_path = Path("storage/uploads") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        logger.info(f"Previewing sheet {sheet_name} from {filename}")
        
        # Obtenir l'aperçu
        preview_data = await sheet_service.get_sheet_preview(
            str(file_path), sheet_name, rows
        )
        
        return JSONResponse({
            "success": True,
            "data": {
                "filename": filename,
                "sheet_name": sheet_name,
                "preview": preview_data
            }
        })
        
    except Exception as e:
        logger.error(f"Error previewing sheet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'aperçu: {str(e)}")

@router.get("/columns/{filename}/{sheet_name}")
async def get_sheet_columns(filename: str, sheet_name: str):
    """
    Obtient les colonnes d'une feuille Excel
    """
    try:
        file_path = Path("storage/uploads") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        logger.info(f"Getting columns for sheet {sheet_name} from {filename}")
        
        # Obtenir les colonnes
        columns_info = await sheet_service.get_sheet_columns(
            str(file_path), sheet_name
        )
        
        return JSONResponse({
            "success": True,
            "data": {
                "filename": filename,
                "sheet_name": sheet_name,
                "columns": columns_info
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting columns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des colonnes: {str(e)}")

@router.post("/validate/{filename}/{sheet_name}")
async def validate_sheet(filename: str, sheet_name: str):
    """
    Valide une feuille Excel pour le traitement
    """
    try:
        file_path = Path("storage/uploads") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        logger.info(f"Validating sheet {sheet_name} from {filename}")
        
        # Valider la feuille
        validation_result = await sheet_service.validate_sheet(
            str(file_path), sheet_name
        )
        
        return JSONResponse({
            "success": True,
            "data": {
                "filename": filename,
                "sheet_name": sheet_name,
                "validation": validation_result
            }
        })
        
    except Exception as e:
        logger.error(f"Error validating sheet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la validation: {str(e)}")
