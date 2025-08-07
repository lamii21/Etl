"""
Routes API pour la gestion des résultats
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from ...utils.logger import setup_logger

logger = setup_logger("yazaki_api_results")
router = APIRouter()

@router.get("/list")
async def list_results():
    """
    Liste tous les résultats de traitement
    """
    try:
        processed_dir = Path("storage/processed")
        
        if not processed_dir.exists():
            return JSONResponse({
                "success": True,
                "data": {"results": []}
            })
        
        results = []
        
        # Parcourir les fichiers de résultats
        for result_file in processed_dir.glob("*.xlsx"):
            file_stat = result_file.stat()
            
            # Chercher le fichier de métadonnées associé
            metadata_file = result_file.with_suffix('.json')
            metadata = {}
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not read metadata for {result_file.name}: {e}")
            
            results.append({
                "filename": result_file.name,
                "size": file_stat.st_size,
                "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "path": str(result_file),
                "metadata": metadata
            })
        
        # Trier par date de création (plus récent en premier)
        results.sort(key=lambda x: x["created"], reverse=True)
        
        return JSONResponse({
            "success": True,
            "data": {"results": results}
        })
        
    except Exception as e:
        logger.error(f"Error listing results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la liste des résultats: {str(e)}")

@router.get("/download/{filename}")
async def download_result(filename: str):
    """
    Télécharge un fichier de résultat
    """
    try:
        file_path = Path("storage/processed") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier de résultat non trouvé")
        
        logger.info(f"Downloading result file: {filename}")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Error downloading result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du téléchargement: {str(e)}")

@router.get("/metadata/{filename}")
async def get_result_metadata(filename: str):
    """
    Obtient les métadonnées d'un résultat
    """
    try:
        result_file = Path("storage/processed") / filename
        metadata_file = result_file.with_suffix('.json')
        
        if not result_file.exists():
            raise HTTPException(status_code=404, detail="Fichier de résultat non trouvé")
        
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        return JSONResponse({
            "success": True,
            "data": {
                "filename": filename,
                "metadata": metadata
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métadonnées: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_result(filename: str):
    """
    Supprime un fichier de résultat et ses métadonnées
    """
    try:
        result_file = Path("storage/processed") / filename
        metadata_file = result_file.with_suffix('.json')
        
        if not result_file.exists():
            raise HTTPException(status_code=404, detail="Fichier de résultat non trouvé")
        
        # Supprimer le fichier de résultat
        result_file.unlink()
        
        # Supprimer les métadonnées si elles existent
        if metadata_file.exists():
            metadata_file.unlink()
        
        logger.info(f"Result deleted: {filename}")
        
        return JSONResponse({
            "success": True,
            "message": f"Résultat {filename} supprimé avec succès"
        })
        
    except Exception as e:
        logger.error(f"Error deleting result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

@router.get("/stats")
async def get_results_stats():
    """
    Obtient les statistiques des résultats
    """
    try:
        processed_dir = Path("storage/processed")
        
        if not processed_dir.exists():
            return JSONResponse({
                "success": True,
                "data": {
                    "total_files": 0,
                    "total_size": 0,
                    "latest_result": None
                }
            })
        
        files = list(processed_dir.glob("*.xlsx"))
        total_size = sum(f.stat().st_size for f in files)
        
        latest_result = None
        if files:
            latest_file = max(files, key=lambda f: f.stat().st_ctime)
            latest_result = {
                "filename": latest_file.name,
                "created": datetime.fromtimestamp(latest_file.stat().st_ctime).isoformat()
            }
        
        return JSONResponse({
            "success": True,
            "data": {
                "total_files": len(files),
                "total_size": total_size,
                "latest_result": latest_result
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors des statistiques: {str(e)}")
