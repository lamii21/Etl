"""
Routes API pour l'upload de fichiers
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
from datetime import datetime
from typing import List

from ...core.services.file_service import FileService
from ...utils.logger import setup_logger

logger = setup_logger("yazaki_api_upload")
router = APIRouter()

# Service de gestion des fichiers
file_service = FileService()

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload un fichier Excel pour traitement
    """
    try:
        logger.info(f"Receiving file upload: {file.filename}")
        
        # Validation du type de fichier
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="Seuls les fichiers Excel (.xlsx, .xls) sont acceptés"
            )
        
        # Générer un ID unique pour le fichier
        file_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file_id}_{file.filename}"
        
        # Chemin de sauvegarde
        upload_dir = Path("storage/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / safe_filename
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analyser le fichier avec le service
        file_info = await file_service.analyze_file(str(file_path))
        
        logger.info(f"File uploaded successfully: {safe_filename}")
        
        return JSONResponse({
            "success": True,
            "message": "Fichier uploadé avec succès",
            "data": {
                "file_id": file_id,
                "filename": file.filename,
                "safe_filename": safe_filename,
                "file_path": str(file_path),
                "file_info": file_info.dict() if file_info else None,
                "upload_time": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

@router.get("/files")
async def list_uploaded_files():
    """
    Liste tous les fichiers uploadés
    """
    try:
        upload_dir = Path("storage/uploads")
        if not upload_dir.exists():
            return JSONResponse({
                "success": True,
                "data": {"files": []}
            })
        
        files = []
        for file_path in upload_dir.glob("*.xlsx"):
            file_stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": file_stat.st_size,
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "path": str(file_path)
            })
        
        return JSONResponse({
            "success": True,
            "data": {"files": files}
        })
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la liste des fichiers: {str(e)}")

@router.delete("/file/{filename}")
async def delete_file(filename: str):
    """
    Supprime un fichier uploadé
    """
    try:
        file_path = Path("storage/uploads") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        file_path.unlink()
        logger.info(f"File deleted: {filename}")
        
        return JSONResponse({
            "success": True,
            "message": f"Fichier {filename} supprimé avec succès"
        })
        
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")
