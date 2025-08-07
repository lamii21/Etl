"""
Service d'analyse des feuilles Excel
Responsable de l'analyse et la sélection des feuilles Excel
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Optional

from app.core.models.sheet_info import SheetInfo, SheetAnalysisResult, SheetSelectionResult
from app.utils.config import UPLOADS_DIR


class SheetService:
    """Service d'analyse des feuilles Excel"""
    
    def __init__(self):
        """Initialise le service d'analyse des feuilles"""
        pass
    
    def analyze_excel_sheets(self, file_path: Path) -> SheetAnalysisResult:
        """Analyse toutes les feuilles d'un fichier Excel"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Charger le fichier Excel
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        # Analyser chaque feuille
        sheets_info = []
        for sheet_name in sheet_names:
            sheet_info = self._analyze_single_sheet(file_path, sheet_name)
            sheets_info.append(sheet_info)
        
        # Déterminer la feuille recommandée
        recommended_sheet = self._find_best_sheet(sheets_info)
        
        return SheetAnalysisResult(
            file_path=str(file_path),
            total_sheets=len(sheet_names),
            sheets=sheets_info,
            recommended_sheet=recommended_sheet
        )
    
    def _analyze_single_sheet(self, file_path: Path, sheet_name: str) -> SheetInfo:
        """Analyse une feuille Excel spécifique"""
        try:
            # Lire un échantillon pour l'analyse rapide
            df_sample = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
            
            # Lire la feuille complète pour les statistiques
            df_full = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Analyser les colonnes pour détecter les PN
            pn_columns = self._find_pn_columns(df_full.columns)
            
            # Calculer la densité des données
            total_cells = len(df_full) * len(df_full.columns)
            empty_cells = df_full.isnull().sum().sum()
            data_density = ((total_cells - empty_cells) / total_cells * 100) if total_cells > 0 else 0
            
            # Déterminer si c'est une feuille de données
            is_data_sheet = (
                len(df_full) > 1 and  # Plus que l'en-tête
                len(df_full.columns) > 1 and  # Plusieurs colonnes
                data_density > 10  # Au moins 10% de données
            )
            
            # Déterminer si recommandée
            recommended = len(pn_columns) > 0 and is_data_sheet
            
            return SheetInfo(
                name=str(sheet_name),
                rows=int(len(df_full)),
                columns=int(len(df_full.columns)),
                column_names=[str(col) for col in df_full.columns.tolist()[:10]],
                pn_columns=[str(col) for col in pn_columns],
                data_density=float(round(data_density, 1)),
                is_data_sheet=bool(is_data_sheet),
                sample_data=df_sample.head(3).fillna("").astype(str).to_dict('records') if len(df_sample) > 0 else [],
                recommended=bool(recommended)
            )
            
        except Exception as e:
            return SheetInfo(
                name=str(sheet_name),
                rows=0,
                columns=0,
                column_names=[],
                pn_columns=[],
                data_density=0.0,
                is_data_sheet=False,
                sample_data=[],
                recommended=False,
                error=str(e)
            )
    
    def _find_pn_columns(self, columns) -> List[str]:
        """Trouve les colonnes Part Number"""
        pn_patterns = ['pn', 'part number', 'part_number', 'yazaki pn', 'yazaki_pn', 'partnumber']
        pn_columns = []
        
        for col in columns:
            col_lower = str(col).lower().strip()
            if any(pattern in col_lower for pattern in pn_patterns):
                pn_columns.append(str(col))
        
        return pn_columns
    
    def _find_best_sheet(self, sheets: List[SheetInfo]) -> str:
        """Trouve la meilleure feuille à recommander"""
        # Filtrer les feuilles recommandées
        recommended_sheets = [s for s in sheets if s.recommended and not s.error]
        
        if recommended_sheets:
            # Trier par score de qualité
            recommended_sheets.sort(key=lambda x: x.quality_score, reverse=True)
            return recommended_sheets[0].name
        
        # Fallback: première feuille de données
        data_sheets = [s for s in sheets if s.is_data_sheet and not s.error]
        if data_sheets:
            data_sheets.sort(key=lambda x: x.quality_score, reverse=True)
            return data_sheets[0].name
        
        # Fallback final: première feuille
        valid_sheets = [s for s in sheets if not s.error]
        return valid_sheets[0].name if valid_sheets else sheets[0].name
    
    def set_working_sheet(self, file_id: str, sheet_name: str) -> SheetSelectionResult:
        """Définit la feuille de travail pour un fichier"""
        try:
            # Trouver le fichier
            file_path = None
            for file in UPLOADS_DIR.glob(f"*{file_id}*"):
                if file.suffix.lower() in ['.xlsx', '.xls']:
                    file_path = file
                    break
            
            if not file_path or not file_path.exists():
                return SheetSelectionResult(
                    success=False,
                    sheet_name="",
                    sheet_stats={},
                    message="File not found"
                )
            
            # Vérifier que la feuille existe et la charger
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Sauvegarder la sélection de feuille
                sheet_info_file = UPLOADS_DIR / f"{file_id}_sheet_info.json"
                
                sheet_info = {
                    "file_id": file_id,
                    "selected_sheet": sheet_name,
                    "sheet_stats": {
                        "rows": int(len(df)),
                        "columns": int(len(df.columns)),
                        "column_names": [str(col) for col in df.columns.tolist()]
                    },
                    "timestamp": pd.Timestamp.now().isoformat()
                }
                
                with open(sheet_info_file, 'w', encoding='utf-8') as f:
                    json.dump(sheet_info, f, indent=2)
                
                return SheetSelectionResult(
                    success=True,
                    sheet_name=sheet_name,
                    sheet_stats=sheet_info["sheet_stats"],
                    message=f"Working sheet set to '{sheet_name}'"
                )
                
            except ValueError:
                return SheetSelectionResult(
                    success=False,
                    sheet_name="",
                    sheet_stats={},
                    message=f"Sheet '{sheet_name}' not found in file"
                )
            
        except Exception as e:
            return SheetSelectionResult(
                success=False,
                sheet_name="",
                sheet_stats={},
                message=f"Error setting working sheet: {str(e)}"
            )
    
    def get_selected_sheet(self, file_id: str) -> Optional[str]:
        """Obtient la feuille sélectionnée pour un fichier"""
        try:
            sheet_info_file = UPLOADS_DIR / f"{file_id}_sheet_info.json"
            
            if sheet_info_file.exists():
                with open(sheet_info_file, 'r', encoding='utf-8') as f:
                    sheet_info = json.load(f)
                    return sheet_info.get('selected_sheet')
            
            return None
            
        except Exception:
            return None
