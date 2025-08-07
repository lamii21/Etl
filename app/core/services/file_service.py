"""
Service de gestion des fichiers
Responsable de l'upload, validation et gestion des fichiers
"""

import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from app.core.models.file_info import FileInfo, UploadResult, FileValidationResult
from app.utils.config import UPLOADS_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE


class FileService:
    """Service de gestion des fichiers"""
    
    def __init__(self):
        """Initialise le service de fichiers"""
        # Créer le répertoire d'uploads s'il n'existe pas
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, file_path: Path, original_name: str) -> FileValidationResult:
        """Valide un fichier uploadé"""
        issues = []
        warnings = []
        
        # Vérifier l'existence
        if not file_path.exists():
            issues.append("File does not exist")
            return FileValidationResult(False, "unknown", issues, warnings)
        
        # Vérifier la taille
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            issues.append(f"File too large: {file_size / (1024*1024):.1f}MB > {MAX_FILE_SIZE / (1024*1024):.1f}MB")
        
        if file_size == 0:
            issues.append("File is empty")
        
        # Vérifier l'extension
        extension = file_path.suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            issues.append(f"Invalid file type: {extension}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Déterminer le type de fichier
        file_type = "excel" if extension in [".xlsx", ".xls"] else "unknown"
        
        # Avertissements
        if file_size > 10 * 1024 * 1024:  # 10MB
            warnings.append("Large file may take longer to process")
        
        is_valid = len(issues) == 0
        
        return FileValidationResult(is_valid, file_type, issues, warnings)
    
    def save_uploaded_file(self, file_content: bytes, original_name: str) -> UploadResult:
        """Sauvegarde un fichier uploadé"""
        try:
            # Générer un ID unique
            file_id = uuid.uuid4().hex[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Créer le nom de fichier avec timestamp et ID
            file_extension = Path(original_name).suffix
            stored_filename = f"{timestamp}_{file_id}_{original_name}"
            stored_path = UPLOADS_DIR / stored_filename
            
            # Sauvegarder le fichier
            with open(stored_path, 'wb') as f:
                f.write(file_content)
            
            # Valider le fichier sauvegardé
            validation = self.validate_file(stored_path, original_name)
            if not validation.is_valid:
                # Supprimer le fichier invalide
                stored_path.unlink(missing_ok=True)
                return UploadResult(False, None, f"Invalid file: {', '.join(validation.issues)}")
            
            # Créer les informations du fichier
            file_info = FileInfo(
                file_id=file_id,
                original_name=original_name,
                stored_path=stored_path,
                file_size=len(file_content),
                upload_timestamp=datetime.now(),
                file_type=validation.file_type,
                is_excel=validation.file_type == "excel"
            )
            
            return UploadResult(True, file_info)
            
        except Exception as e:
            return UploadResult(False, None, f"Upload error: {str(e)}")
    
    def find_file_by_id(self, file_id: str) -> Optional[FileInfo]:
        """Trouve un fichier par son ID"""
        try:
            # Chercher dans le répertoire d'uploads
            for file_path in UPLOADS_DIR.glob(f"*{file_id}*"):
                if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    # Extraire les informations du nom de fichier
                    filename_parts = file_path.name.split('_', 2)
                    if len(filename_parts) >= 3:
                        timestamp_str = filename_parts[0] + '_' + filename_parts[1]
                        original_name = filename_parts[2]
                        
                        try:
                            upload_timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        except ValueError:
                            upload_timestamp = datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        return FileInfo(
                            file_id=file_id,
                            original_name=original_name,
                            stored_path=file_path,
                            file_size=file_path.stat().st_size,
                            upload_timestamp=upload_timestamp,
                            file_type="excel" if file_path.suffix.lower() in [".xlsx", ".xls"] else "unknown",
                            is_excel=file_path.suffix.lower() in [".xlsx", ".xls"]
                        )
            
            return None
            
        except Exception:
            return None
    
    def get_file_path(self, file_id: str) -> Optional[Path]:
        """Obtient le chemin d'un fichier par son ID"""
        file_info = self.find_file_by_id(file_id)
        return file_info.stored_path if file_info else None
    
    def list_uploaded_files(self) -> List[FileInfo]:
        """Liste tous les fichiers uploadés"""
        files = []
        
        try:
            for file_path in UPLOADS_DIR.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    # Extraire l'ID du fichier du nom
                    filename_parts = file_path.name.split('_', 2)
                    if len(filename_parts) >= 2:
                        file_id = filename_parts[1]
                        file_info = self.find_file_by_id(file_id)
                        if file_info:
                            files.append(file_info)
            
            # Trier par timestamp de upload (plus récent en premier)
            files.sort(key=lambda f: f.upload_timestamp, reverse=True)
            
        except Exception:
            pass
        
        return files
    
    def cleanup_old_files(self, days_old: int = 7) -> int:
        """Nettoie les fichiers anciens"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            removed_count = 0
            
            for file_path in UPLOADS_DIR.glob("*"):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_date:
                        file_path.unlink()
                        removed_count += 1
            
            return removed_count
            
        except Exception:
            return 0
