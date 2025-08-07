"""
Modèles de données pour les informations de feuilles Excel
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class SheetInfo:
    """Informations sur une feuille Excel"""
    name: str
    rows: int
    columns: int
    column_names: List[str]
    pn_columns: List[str]
    data_density: float
    is_data_sheet: bool
    sample_data: List[Dict[str, Any]]
    recommended: bool
    error: Optional[str] = None
    
    @property
    def has_pn_columns(self) -> bool:
        """Vérifie si la feuille a des colonnes PN"""
        return len(self.pn_columns) > 0
    
    @property
    def quality_score(self) -> float:
        """Score de qualité de la feuille (0-100)"""
        score = 0.0
        
        # Points pour les données
        if self.is_data_sheet:
            score += 30
        
        # Points pour les colonnes PN
        if self.has_pn_columns:
            score += 40
        
        # Points pour la densité des données
        score += self.data_density * 0.3
        
        return min(100.0, score)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API"""
        return {
            "name": self.name,
            "rows": self.rows,
            "columns": self.columns,
            "column_names": self.column_names,
            "pn_columns": self.pn_columns,
            "data_density": self.data_density,
            "is_data_sheet": self.is_data_sheet,
            "sample_data": self.sample_data,
            "recommended": self.recommended,
            "quality_score": self.quality_score,
            "error": self.error
        }


@dataclass
class SheetAnalysisResult:
    """Résultat de l'analyse des feuilles Excel"""
    file_path: str
    total_sheets: int
    sheets: List[SheetInfo]
    recommended_sheet: str
    
    @property
    def data_sheets(self) -> List[SheetInfo]:
        """Feuilles contenant des données"""
        return [s for s in self.sheets if s.is_data_sheet]
    
    @property
    def sheets_with_pn(self) -> List[SheetInfo]:
        """Feuilles contenant des colonnes PN"""
        return [s for s in self.sheets if s.has_pn_columns]
    
    @property
    def recommended_sheet_info(self) -> Optional[SheetInfo]:
        """Informations sur la feuille recommandée"""
        for sheet in self.sheets:
            if sheet.name == self.recommended_sheet:
                return sheet
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API"""
        return {
            "success": True,
            "file_path": self.file_path,
            "total_sheets": self.total_sheets,
            "sheets": [sheet.to_dict() for sheet in self.sheets],
            "recommended_sheet": self.recommended_sheet,
            "analysis_summary": {
                "data_sheets": len(self.data_sheets),
                "sheets_with_pn": len(self.sheets_with_pn),
                "recommended_sheets": len([s for s in self.sheets if s.recommended])
            }
        }


@dataclass
class SheetSelectionResult:
    """Résultat de la sélection d'une feuille de travail"""
    success: bool
    sheet_name: str
    sheet_stats: Dict[str, Any]
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API"""
        return {
            "success": self.success,
            "message": self.message,
            "sheet_name": self.sheet_name,
            "sheet_stats": self.sheet_stats
        }
