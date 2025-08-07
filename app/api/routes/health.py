"""
Routes de santé et statut du système
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from pathlib import Path
import os

from app.utils.config import MASTER_BOM_PATH, UPLOADS_DIR
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("health")


@router.get("/")
async def health_check():
    """Vérification de l'état du système"""
    try:
        # Vérifier l'existence du Master BOM
        master_bom_exists = MASTER_BOM_PATH.exists()
        
        # Vérifier l'accès au répertoire d'uploads
        uploads_accessible = UPLOADS_DIR.exists() and UPLOADS_DIR.is_dir()
        
        # Calculer l'espace disque disponible
        try:
            disk_usage = UPLOADS_DIR.stat()
            disk_info = {
                "uploads_dir": str(UPLOADS_DIR),
                "accessible": uploads_accessible
            }
        except Exception:
            disk_info = {
                "uploads_dir": str(UPLOADS_DIR),
                "accessible": False
            }
        
        # Compter les fichiers uploadés
        uploaded_files_count = 0
        if uploads_accessible:
            try:
                uploaded_files_count = len([f for f in UPLOADS_DIR.glob("*.xlsx") if f.is_file()])
            except Exception:
                pass
        
        # Déterminer le statut global
        is_healthy = master_bom_exists and uploads_accessible
        status = "healthy" if is_healthy else "degraded"
        
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "components": {
                "master_bom": {
                    "available": master_bom_exists,
                    "path": str(MASTER_BOM_PATH)
                },
                "storage": disk_info,
                "uploaded_files": uploaded_files_count
            },
            "system_info": {
                "api_version": "3.0.0",
                "architecture": "clean_modular",
                "features": [
                    "multi_sheet_support",
                    "data_cleaning",
                    "structured_logging",
                    "error_handling"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detailed")
async def detailed_health_check():
    """Vérification détaillée de l'état du système"""
    try:
        basic_health = await health_check()
        
        # Informations détaillées sur le Master BOM
        master_bom_info = {"available": False}
        if MASTER_BOM_PATH.exists():
            try:
                import pandas as pd
                df = pd.read_excel(MASTER_BOM_PATH)
                master_bom_info = {
                    "available": True,
                    "path": str(MASTER_BOM_PATH),
                    "size_mb": round(MASTER_BOM_PATH.stat().st_size / (1024 * 1024), 2),
                    "rows": len(df),
                    "columns": len(df.columns),
                    "last_modified": datetime.fromtimestamp(
                        MASTER_BOM_PATH.stat().st_mtime
                    ).isoformat()
                }
            except Exception as e:
                master_bom_info = {
                    "available": True,
                    "path": str(MASTER_BOM_PATH),
                    "error": f"Cannot read file: {str(e)}"
                }
        
        # Informations sur les répertoires
        directories_info = {}
        for dir_name, dir_path in [
            ("uploads", UPLOADS_DIR),
            ("data", MASTER_BOM_PATH.parent),
        ]:
            try:
                if dir_path.exists():
                    file_count = len([f for f in dir_path.glob("*") if f.is_file()])
                    directories_info[dir_name] = {
                        "exists": True,
                        "path": str(dir_path),
                        "file_count": file_count,
                        "writable": os.access(dir_path, os.W_OK) if dir_path.exists() else False
                    }
                else:
                    directories_info[dir_name] = {
                        "exists": False,
                        "path": str(dir_path)
                    }
            except Exception as e:
                directories_info[dir_name] = {
                    "exists": False,
                    "path": str(dir_path),
                    "error": str(e)
                }
        
        # Mise à jour de la réponse de base
        detailed_response = basic_health.copy()
        detailed_response["components"]["master_bom"] = master_bom_info
        detailed_response["components"]["directories"] = directories_info
        
        return detailed_response
        
    except Exception as e:
        logger.error(f"Detailed health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/version")
async def get_version():
    """Obtient les informations de version"""
    return {
        "api_version": "3.0.0",
        "architecture": "clean_modular",
        "build_date": "2025-08-05",
        "features": {
            "multi_sheet_excel": True,
            "data_cleaning": True,
            "structured_services": True,
            "comprehensive_logging": True,
            "error_handling": True,
            "file_validation": True
        },
        "dependencies": {
            "fastapi": ">=0.68.0",
            "pandas": ">=1.3.0",
            "openpyxl": ">=3.0.0"
        }
    }
