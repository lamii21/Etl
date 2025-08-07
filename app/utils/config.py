"""
Configuration du système YAZAKI
"""

import os
from pathlib import Path

# Répertoires
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
PROCESSED_DIR = STORAGE_DIR / "processed"
TEMP_DIR = STORAGE_DIR / "temp"

# Master BOM
MASTER_BOM_PATH = DATA_DIR / "Master_BOM_Real.xlsx"

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Web Configuration
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 5000))

# Debug Mode
DEBUG_MODE = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "yazaki_system.log"

# File Upload
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".xlsx", ".xls"}

# Processing
DEFAULT_CLEANING_OPTIONS = {
    "remove_empty_rows": True,
    "remove_empty_columns": True,
    "clean_column_names": True,
    "standardize_pn": True,
    "remove_duplicates": True,
    "clean_whitespace": True,
    "standardize_case": True,
    "fix_data_types": True,
    "handle_missing": True,
    "validate_data": True
}
