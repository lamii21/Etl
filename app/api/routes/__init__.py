"""
Routes API pour le système YAZAKI
"""

# Import des routes pour faciliter l'utilisation
from . import health, upload, sheets, cleaning, processing, results

__all__ = ["health", "upload", "sheets", "cleaning", "processing", "results"]