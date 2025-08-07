"""
Modèles de données pour les résultats de traitement
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path


@dataclass
class CleaningStats:
    """Statistiques de nettoyage des données"""
    original_rows: int
    original_columns: int
    final_rows: int
    final_columns: int
    operations_performed: List[str]
    issues_found: List[str]
    issues_fixed: List[str]
    
    @property
    def rows_removed(self) -> int:
        """Nombre de lignes supprimées"""
        return self.original_rows - self.final_rows
    
    @property
    def columns_removed(self) -> int:
        """Nombre de colonnes supprimées"""
        return self.original_columns - self.final_columns
    
    @property
    def data_reduction_percent(self) -> float:
        """Pourcentage de réduction des données"""
        if self.original_rows == 0:
            return 0.0
        return (self.rows_removed / self.original_rows) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API"""
        return {
            "original_rows": self.original_rows,
            "original_columns": self.original_columns,
            "final_rows": self.final_rows,
            "final_columns": self.final_columns,
            "rows_removed": self.rows_removed,
            "columns_removed": self.columns_removed,
            "operations_performed": self.operations_performed,
            "issues_found": self.issues_found,
            "issues_fixed": self.issues_fixed,
            "data_reduction_percent": round(self.data_reduction_percent, 1)
        }


@dataclass
class CleaningResult:
    """Résultat du nettoyage des données"""
    success: bool
    original_file: str
    cleaned_file: str
    cleaning_stats: CleaningStats
    cleaning_report: Dict[str, Any]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API"""
        if self.success:
            return {
                "success": True,
                "message": "Data cleaned successfully",
                "original_file": self.original_file,
                "cleaned_file": self.cleaned_file,
                "cleaning_report": self.cleaning_report,
                "original_stats": {
                    "rows": self.cleaning_stats.original_rows,
                    "columns": self.cleaning_stats.original_columns
                },
                "cleaned_stats": {
                    "rows": self.cleaning_stats.final_rows,
                    "columns": self.cleaning_stats.final_columns
                }
            }
        else:
            return {
                "success": False,
                "message": self.error_message or "Cleaning failed"
            }


@dataclass
class ProcessingStats:
    """Statistiques de traitement principal"""
    input_rows: int
    output_rows: int
    master_bom_rows: int
    lookup_matches: int
    lookup_misses: int
    processing_time: float
    
    @property
    def match_rate(self) -> float:
        """Taux de correspondance du lookup"""
        if self.input_rows == 0:
            return 0.0
        return (self.lookup_matches / self.input_rows) * 100
    
    @property
    def miss_rate(self) -> float:
        """Taux d'échec du lookup"""
        return 100.0 - self.match_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API"""
        return {
            "input_rows": self.input_rows,
            "output_rows": self.output_rows,
            "master_bom_rows": self.master_bom_rows,
            "lookup_matches": self.lookup_matches,
            "lookup_misses": self.lookup_misses,
            "match_rate": round(self.match_rate, 1),
            "miss_rate": round(self.miss_rate, 1),
            "processing_time": round(self.processing_time, 2)
        }


@dataclass
class ProcessingResult:
    """Résultat du traitement principal"""
    success: bool
    output_file: Path
    processing_stats: ProcessingStats
    distribution_data: Dict[str, Any]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API"""
        if self.success:
            return {
                "success": True,
                "message": "Processing completed successfully",
                "output_file": str(self.output_file),
                "processing_stats": self.processing_stats.to_dict(),
                "distribution_data": self.distribution_data
            }
        else:
            return {
                "success": False,
                "message": self.error_message or "Processing failed"
            }
