"""
Routes API pour le nettoyage des données
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Optional

from ...core.processors.data_cleaner import DataCleaner
from ...utils.logger import setup_logger

logger = setup_logger("yazaki_api_cleaning")
router = APIRouter()

# Processeur de nettoyage
data_cleaner = DataCleaner()

class CleaningOptions(BaseModel):
    """Options de nettoyage des données"""
    remove_empty_rows: bool = True
    remove_empty_columns: bool = True
    clean_column_names: bool = True
    standardize_pn: bool = True
    remove_duplicates: bool = True
    clean_whitespace: bool = True
    standardize_case: bool = True
    fix_data_types: bool = True
    handle_missing: bool = True
    validate_data: bool = True

@router.post("/analyze/{filename}/{sheet_name}")
async def analyze_data_quality(filename: str, sheet_name: str):
    """
    Analyse la qualité des données d'une feuille
    """
    try:
        file_path = Path("storage/uploads") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        logger.info(f"Analyzing data quality for {sheet_name} in {filename}")
        
        # Analyser la qualité des données
        quality_report = await data_cleaner.analyze_data_quality(
            str(file_path), sheet_name
        )
        
        return JSONResponse({
            "success": True,
            "data": {
                "filename": filename,
                "sheet_name": sheet_name,
                "quality_report": quality_report
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing data quality: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@router.post("/clean/{filename}/{sheet_name}")
async def clean_data(filename: str, sheet_name: str, options: Optional[CleaningOptions] = None):
    """
    Nettoie les données d'une feuille Excel
    """
    try:
        file_path = Path("storage/uploads") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        logger.info(f"Cleaning data for {sheet_name} in {filename}")
        
        # Options de nettoyage
        cleaning_opts = options.dict() if options else data_cleaner.get_default_cleaning_options()
        
        # Nettoyer les données
        cleaning_result = await data_cleaner.clean_sheet_data(
            str(file_path), sheet_name, cleaning_opts
        )
        
        return JSONResponse({
            "success": True,
            "data": {
                "filename": filename,
                "sheet_name": sheet_name,
                "cleaning_result": cleaning_result
            }
        })
        
    except Exception as e:
        logger.error(f"Error cleaning data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du nettoyage: {str(e)}")

@router.get("/options/default")
async def get_default_cleaning_options():
    """
    Obtient les options de nettoyage par défaut
    """
    try:
        options = data_cleaner.get_default_cleaning_options()
        
        return JSONResponse({
            "success": True,
            "data": {"options": options}
        })
        
    except Exception as e:
        logger.error(f"Error getting default options: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/preview/{filename}/{sheet_name}")
async def preview_cleaning(filename: str, sheet_name: str, options: Optional[CleaningOptions] = None):
    """
    Aperçu du nettoyage sans sauvegarder
    """
    try:
        file_path = Path("storage/uploads") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        logger.info(f"Previewing cleaning for {sheet_name} in {filename}")
        
        # Options de nettoyage
        cleaning_opts = options.dict() if options else data_cleaner.get_default_cleaning_options()
        
        # Aperçu du nettoyage
        preview_result = await data_cleaner.preview_cleaning(
            str(file_path), sheet_name, cleaning_opts
        )
        
        return JSONResponse({
            "success": True,
            "data": {
                "filename": filename,
                "sheet_name": sheet_name,
                "preview": preview_result
            }
        })
        
    except Exception as e:
        logger.error(f"Error previewing cleaning: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'aperçu: {str(e)}")
