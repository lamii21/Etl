#!/usr/bin/env python3
"""
Tests pour valider la nouvelle architecture propre
Vérifie que tous les composants fonctionnent correctement
"""

import sys
import unittest
from pathlib import Path
import tempfile
import pandas as pd

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.models.file_info import FileInfo, UploadResult
from app.core.models.sheet_info import SheetInfo, SheetAnalysisResult
from app.core.services.file_service import FileService
from app.core.services.sheet_service import SheetService
from app.utils.logger import setup_logger


class TestCleanArchitecture(unittest.TestCase):
    """Tests pour la nouvelle architecture"""
    
    def setUp(self):
        """Configuration des tests"""
        self.logger = setup_logger("test")
        self.file_service = FileService()
        self.sheet_service = SheetService()
    
    def test_file_info_model(self):
        """Test du modèle FileInfo"""
        file_info = FileInfo(
            file_id="test123",
            original_name="test.xlsx",
            stored_path=Path("test.xlsx"),
            file_size=1024,
            upload_timestamp=pd.Timestamp.now(),
            file_type="excel",
            is_excel=True
        )
        
        self.assertEqual(file_info.file_id, "test123")
        self.assertEqual(file_info.extension, ".xlsx")
        self.assertAlmostEqual(file_info.size_mb, 0.001, places=3)
    
    def test_sheet_info_model(self):
        """Test du modèle SheetInfo"""
        sheet_info = SheetInfo(
            name="Test Sheet",
            rows=100,
            columns=5,
            column_names=["A", "B", "C", "D", "E"],
            pn_columns=["PN"],
            data_density=85.5,
            is_data_sheet=True,
            sample_data=[],
            recommended=True
        )
        
        self.assertTrue(sheet_info.has_pn_columns)
        self.assertGreater(sheet_info.quality_score, 70)
        
        # Test de conversion en dictionnaire
        sheet_dict = sheet_info.to_dict()
        self.assertIn("name", sheet_dict)
        self.assertIn("quality_score", sheet_dict)
    
    def test_file_service_validation(self):
        """Test de validation des fichiers"""
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            
            # Créer un fichier Excel simple
            df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
            df.to_excel(tmp_path, index=False)
        
        try:
            # Tester la validation
            validation = self.file_service.validate_file(tmp_path, "test.xlsx")
            
            self.assertTrue(validation.is_valid)
            self.assertEqual(validation.file_type, "excel")
            self.assertEqual(len(validation.issues), 0)
            
        finally:
            # Nettoyer
            tmp_path.unlink(missing_ok=True)
    
    def test_sheet_service_analysis(self):
        """Test d'analyse des feuilles Excel"""
        # Créer un fichier Excel multi-feuilles
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            
            # Créer plusieurs feuilles
            with pd.ExcelWriter(tmp_path, engine='openpyxl') as writer:
                # Feuille avec PN
                df1 = pd.DataFrame({
                    "PN": ["ABC123", "DEF456"],
                    "Description": ["Part A", "Part B"],
                    "Quantity": [10, 20]
                })
                df1.to_excel(writer, sheet_name="Main_Data", index=False)
                
                # Feuille sans PN
                df2 = pd.DataFrame({
                    "Category": ["A", "B"],
                    "Count": [5, 10]
                })
                df2.to_excel(writer, sheet_name="Summary", index=False)
        
        try:
            # Tester l'analyse
            analysis = self.sheet_service.analyze_excel_sheets(tmp_path)
            
            self.assertIsInstance(analysis, SheetAnalysisResult)
            self.assertEqual(analysis.total_sheets, 2)
            self.assertGreater(len(analysis.sheets_with_pn), 0)
            self.assertEqual(analysis.recommended_sheet, "Main_Data")
            
            # Vérifier les détails des feuilles
            main_sheet = next((s for s in analysis.sheets if s.name == "Main_Data"), None)
            self.assertIsNotNone(main_sheet)
            self.assertTrue(main_sheet.has_pn_columns)
            self.assertTrue(main_sheet.recommended)
            
        finally:
            # Nettoyer
            tmp_path.unlink(missing_ok=True)
    
    def test_logging_system(self):
        """Test du système de logging"""
        from app.utils.logger import get_structured_logger
        
        # Créer un logger structuré
        logger = get_structured_logger("test", {"component": "test_suite"})
        
        # Tester les différents niveaux
        logger.info("Test message", test_id="123")
        logger.warning("Test warning", test_id="456")
        
        # Tester le contexte additionnel
        context_logger = logger.with_context(operation="file_upload")
        context_logger.info("Upload started")
        
        # Si on arrive ici, le logging fonctionne
        self.assertTrue(True)
    
    def test_configuration_loading(self):
        """Test du chargement de la configuration"""
        from app.utils.config import BASE_DIR, UPLOADS_DIR, MASTER_BOM_PATH
        
        # Vérifier que les chemins sont définis
        self.assertIsInstance(BASE_DIR, Path)
        self.assertIsInstance(UPLOADS_DIR, Path)
        self.assertIsInstance(MASTER_BOM_PATH, Path)
        
        # Vérifier que les répertoires peuvent être créés
        test_dir = UPLOADS_DIR / "test"
        test_dir.mkdir(parents=True, exist_ok=True)
        self.assertTrue(test_dir.exists())
        test_dir.rmdir()
    
    def test_models_serialization(self):
        """Test de sérialisation des modèles"""
        from app.core.models.processing_result import CleaningStats, ProcessingStats
        
        # Test CleaningStats
        cleaning_stats = CleaningStats(
            original_rows=100,
            original_columns=10,
            final_rows=95,
            final_columns=8,
            operations_performed=["remove_empty_rows", "clean_whitespace"],
            issues_found=["5 empty rows", "whitespace issues"],
            issues_fixed=["removed empty rows", "cleaned whitespace"]
        )
        
        stats_dict = cleaning_stats.to_dict()
        self.assertIn("rows_removed", stats_dict)
        self.assertEqual(stats_dict["rows_removed"], 5)
        
        # Test ProcessingStats
        processing_stats = ProcessingStats(
            input_rows=100,
            output_rows=100,
            master_bom_rows=1000,
            lookup_matches=85,
            lookup_misses=15,
            processing_time=2.5
        )
        
        proc_dict = processing_stats.to_dict()
        self.assertIn("match_rate", proc_dict)
        self.assertEqual(proc_dict["match_rate"], 85.0)


class TestSystemIntegration(unittest.TestCase):
    """Tests d'intégration du système"""
    
    def test_full_workflow_simulation(self):
        """Simule un workflow complet"""
        # Ce test simule le workflow sans démarrer les serveurs
        
        # 1. Upload de fichier
        file_service = FileService()
        
        # Créer un fichier de test
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            df = pd.DataFrame({
                "PN": ["ABC123", "DEF456"],
                "Description": ["Component A", "Component B"]
            })
            df.to_excel(tmp_file.name, index=False)
            
            # Lire le contenu
            with open(tmp_file.name, 'rb') as f:
                file_content = f.read()
        
        # Simuler l'upload
        upload_result = file_service.save_uploaded_file(file_content, "test.xlsx")
        self.assertTrue(upload_result.success)
        
        # 2. Analyse des feuilles
        sheet_service = SheetService()
        file_path = upload_result.file_info.stored_path
        
        analysis = sheet_service.analyze_excel_sheets(file_path)
        self.assertIsInstance(analysis, SheetAnalysisResult)
        
        # 3. Sélection de feuille
        selection_result = sheet_service.set_working_sheet(
            upload_result.file_info.file_id,
            analysis.recommended_sheet
        )
        self.assertTrue(selection_result.success)
        
        # Nettoyer
        file_path.unlink(missing_ok=True)


def run_architecture_tests():
    """Exécute tous les tests d'architecture"""
    print("🧪 TESTS DE LA NOUVELLE ARCHITECTURE PROPRE")
    print("=" * 60)
    
    # Créer la suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter les tests
    suite.addTests(loader.loadTestsFromTestCase(TestCleanArchitecture))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ TOUS LES TESTS RÉUSSIS !")
        print("🎉 La nouvelle architecture est fonctionnelle !")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print(f"Échecs: {len(result.failures)}")
        print(f"Erreurs: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_architecture_tests()
    sys.exit(0 if success else 1)
