"""
Modèles de données pour les informations de fichiers
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime


@dataclass
class FileInfo:
    """Informations sur un fichier uploadé"""
    file_id: str
    original_name: str
    stored_path: Path
    file_size: int
    upload_timestamp: datetime
    file_type: str
    is_excel: bool = False
    
    @property
    def size_mb(self) -> float:
        """Taille du fichier en MB"""
        return self.file_size / (1024 * 1024)
    
    @property
    def extension(self) -> str:
        """Extension du fichier"""
        return self.stored_path.suffix.lower()


@dataclass
class UploadResult:
    """Résultat d'un upload de fichier"""
    success: bool
    file_info: Optional[FileInfo] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API"""
        if self.success and self.file_info:
            return {
                "success": True,
                "file_id": self.file_info.file_id,
                "filename": self.file_info.original_name,
                "file_size": self.file_info.file_size,
                "size_mb": self.file_info.size_mb,
                "upload_timestamp": self.file_info.upload_timestamp.isoformat()
            }
        else:
            return {
                "success": False,
                "message": self.error_message or "Upload failed"
            }


@dataclass
class FileValidationResult:
    """Résultat de validation d'un fichier"""
    is_valid: bool
    file_type: str
    issues: List[str]
    warnings: List[str]
    
    @property
    def has_issues(self) -> bool:
        """Vérifie s'il y a des problèmes"""
        return len(self.issues) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Vérifie s'il y a des avertissements"""
        return len(self.warnings) > 0
