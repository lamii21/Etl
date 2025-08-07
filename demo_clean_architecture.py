#!/usr/bin/env python3
"""
Démonstration de la nouvelle architecture propre
Montre les capacités et l'organisation du code refactorisé
"""

import sys
from pathlib import Path
import pandas as pd
import tempfile

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.models.file_info import FileInfo, UploadResult
from app.core.models.sheet_info import SheetInfo, SheetAnalysisResult
from app.core.services.file_service import FileService
from app.core.services.sheet_service import SheetService
from app.utils.logger import get_structured_logger, configure_global_logging
from app.utils.config import BASE_DIR, UPLOADS_DIR


def demo_logging_system():
    """Démonstration du système de logging"""
    print("📝 DÉMONSTRATION DU SYSTÈME DE LOGGING")
    print("-" * 50)
    
    # Configurer le logging global
    configure_global_logging()
    
    # Créer un logger structuré
    logger = get_structured_logger("demo", {"component": "architecture_demo"})
    
    print("✅ Logger structuré créé avec contexte")
    
    # Démontrer les différents niveaux
    logger.info("Démarrage de la démonstration", demo_id="arch_001")
    logger.warning("Ceci est un avertissement", level="demo")
    
    # Démontrer le contexte additionnel
    upload_logger = logger.with_context(operation="file_upload", user="demo_user")
    upload_logger.info("Upload simulé démarré")
    upload_logger.info("Upload simulé terminé", status="success")
    
    print("✅ Logs structurés avec contexte générés")
    print()


def demo_models():
    """Démonstration des modèles de données"""
    print("📊 DÉMONSTRATION DES MODÈLES DE DONNÉES")
    print("-" * 50)
    
    # Démonstration FileInfo
    file_info = FileInfo(
        file_id="demo123",
        original_name="demo_file.xlsx",
        stored_path=Path("demo_file.xlsx"),
        file_size=2048000,  # 2MB
        upload_timestamp=pd.Timestamp.now(),
        file_type="excel",
        is_excel=True
    )
    
    print(f"📄 FileInfo créé:")
    print(f"   • ID: {file_info.file_id}")
    print(f"   • Nom: {file_info.original_name}")
    print(f"   • Taille: {file_info.size_mb:.2f} MB")
    print(f"   • Extension: {file_info.extension}")
    print(f"   • Type Excel: {file_info.is_excel}")
    
    # Démonstration SheetInfo
    sheet_info = SheetInfo(
        name="Main_Data",
        rows=150,
        columns=8,
        column_names=["PN", "Description", "Quantity", "Price", "Status", "Project", "Notes", "Date"],
        pn_columns=["PN"],
        data_density=92.5,
        is_data_sheet=True,
        sample_data=[
            {"PN": "ABC123", "Description": "Component A", "Quantity": "10"},
            {"PN": "DEF456", "Description": "Component B", "Quantity": "20"}
        ],
        recommended=True
    )
    
    print(f"\n📋 SheetInfo créé:")
    print(f"   • Nom: {sheet_info.name}")
    print(f"   • Dimensions: {sheet_info.rows} × {sheet_info.columns}")
    print(f"   • Colonnes PN: {sheet_info.pn_columns}")
    print(f"   • Densité: {sheet_info.data_density}%")
    print(f"   • Score qualité: {sheet_info.quality_score:.1f}/100")
    print(f"   • Recommandée: {sheet_info.recommended}")
    
    # Démonstration de sérialisation
    sheet_dict = sheet_info.to_dict()
    print(f"\n🔄 Sérialisation JSON:")
    print(f"   • Clés disponibles: {list(sheet_dict.keys())}")
    print(f"   • Prêt pour API: ✅")
    print()


def demo_file_service():
    """Démonstration du service de fichiers"""
    print("📁 DÉMONSTRATION DU SERVICE DE FICHIERS")
    print("-" * 50)
    
    # Créer le service
    file_service = FileService()
    print("✅ FileService initialisé")
    
    # Créer un fichier Excel de démonstration
    demo_data = pd.DataFrame({
        "PN": ["ABC123", "DEF456", "GHI789"],
        "Description": ["Component A", "Component B", "Component C"],
        "Quantity": [10, 20, 30],
        "Project": ["V710_AWD_PP_YOTK"] * 3
    })
    
    # Sauvegarder temporairement
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        demo_data.to_excel(tmp_file.name, index=False)
        
        # Lire le contenu
        with open(tmp_file.name, 'rb') as f:
            file_content = f.read()
        
        tmp_path = Path(tmp_file.name)
    
    try:
        # Démonstration de validation
        validation = file_service.validate_file(tmp_path, "demo.xlsx")
        print(f"📋 Validation du fichier:")
        print(f"   • Valide: {validation.is_valid}")
        print(f"   • Type: {validation.file_type}")
        print(f"   • Problèmes: {len(validation.issues)}")
        print(f"   • Avertissements: {len(validation.warnings)}")
        
        # Démonstration d'upload
        upload_result = file_service.save_uploaded_file(file_content, "demo.xlsx")
        print(f"\n📤 Upload simulé:")
        print(f"   • Succès: {upload_result.success}")
        
        if upload_result.success:
            file_info = upload_result.file_info
            print(f"   • File ID: {file_info.file_id}")
            print(f"   • Chemin stocké: {file_info.stored_path.name}")
            print(f"   • Taille: {file_info.size_mb:.2f} MB")
            
            # Démonstration de recherche
            found_file = file_service.find_file_by_id(file_info.file_id)
            print(f"\n🔍 Recherche par ID:")
            print(f"   • Trouvé: {found_file is not None}")
            if found_file:
                print(f"   • Nom original: {found_file.original_name}")
            
            # Nettoyer le fichier uploadé
            file_info.stored_path.unlink(missing_ok=True)
        
    finally:
        # Nettoyer le fichier temporaire
        tmp_path.unlink(missing_ok=True)
    
    print()


def demo_sheet_service():
    """Démonstration du service d'analyse des feuilles"""
    print("📊 DÉMONSTRATION DU SERVICE D'ANALYSE DES FEUILLES")
    print("-" * 50)
    
    # Créer le service
    sheet_service = SheetService()
    print("✅ SheetService initialisé")
    
    # Créer un fichier Excel multi-feuilles
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        
        with pd.ExcelWriter(tmp_path, engine='openpyxl') as writer:
            # Feuille principale avec PN
            main_data = pd.DataFrame({
                "PN": ["ABC123", "DEF456", "GHI789", "JKL012"],
                "Description": ["Component A", "Component B", "Component C", "Component D"],
                "Quantity": [10, 20, 30, 40],
                "V710_AWD_PP_YOTK": ["Active", "Active", "Inactive", "Active"]
            })
            main_data.to_excel(writer, sheet_name="Main_Data", index=False)
            
            # Feuille de résumé sans PN
            summary_data = pd.DataFrame({
                "Category": ["Electronics", "Mechanical"],
                "Count": [25, 15],
                "Status": ["OK", "Review"]
            })
            summary_data.to_excel(writer, sheet_name="Summary", index=False)
            
            # Feuille alternative avec PN différent
            alt_data = pd.DataFrame({
                "YAZAKI_PN": ["MNO345", "PQR678"],
                "Part_Name": ["Alt Component 1", "Alt Component 2"],
                "Stock": [5, 15]
            })
            alt_data.to_excel(writer, sheet_name="Alternative", index=False)
    
    try:
        # Démonstration d'analyse
        analysis = sheet_service.analyze_excel_sheets(tmp_path)
        
        print(f"📋 Analyse des feuilles:")
        print(f"   • Total feuilles: {analysis.total_sheets}")
        print(f"   • Feuilles avec données: {len(analysis.data_sheets)}")
        print(f"   • Feuilles avec PN: {len(analysis.sheets_with_pn)}")
        print(f"   • Feuille recommandée: {analysis.recommended_sheet}")
        
        print(f"\n📊 Détail des feuilles:")
        for sheet in analysis.sheets:
            pn_info = f" (PN: {', '.join(sheet.pn_columns)})" if sheet.pn_columns else " (No PN)"
            quality_info = f" [Score: {sheet.quality_score:.1f}]"
            recommended_mark = " ⭐" if sheet.recommended else ""
            
            print(f"   • {sheet.name}: {sheet.rows} rows, {sheet.data_density}% density{pn_info}{quality_info}{recommended_mark}")
        
        # Démonstration de sélection
        file_id = "demo_sheet_123"
        selection_result = sheet_service.set_working_sheet(file_id, analysis.recommended_sheet)
        
        print(f"\n🎯 Sélection de feuille:")
        print(f"   • Succès: {selection_result.success}")
        print(f"   • Message: {selection_result.message}")
        
        if selection_result.success:
            print(f"   • Feuille sélectionnée: {selection_result.sheet_name}")
            print(f"   • Statistiques: {selection_result.sheet_stats['rows']} rows, {selection_result.sheet_stats['columns']} cols")
        
    finally:
        # Nettoyer
        tmp_path.unlink(missing_ok=True)
    
    print()


def demo_architecture_benefits():
    """Démonstration des bénéfices de l'architecture"""
    print("🎯 BÉNÉFICES DE LA NOUVELLE ARCHITECTURE")
    print("-" * 50)
    
    benefits = [
        ("🏗️ Modularité", "Code organisé en modules spécialisés"),
        ("🔧 Maintenabilité", "Ajout/modification de fonctionnalités facilité"),
        ("🧪 Testabilité", "Services testables unitairement"),
        ("📝 Traçabilité", "Logging structuré pour debugging"),
        ("🔒 Robustesse", "Validation des données à tous les niveaux"),
        ("📊 Évolutivité", "Architecture prête pour nouvelles fonctionnalités"),
        ("👥 Collaboration", "Structure claire pour équipe de développement"),
        ("🚀 Performance", "Services optimisés et spécialisés")
    ]
    
    for benefit, description in benefits:
        print(f"   {benefit} {description}")
    
    print()


def main():
    """Fonction principale de démonstration"""
    print("🎉 DÉMONSTRATION DE LA NOUVELLE ARCHITECTURE YAZAKI")
    print("=" * 70)
    print("Architecture Clean - Code Organisé et Professionnel")
    print("=" * 70)
    print()
    
    # Démonstrations
    demo_logging_system()
    demo_models()
    demo_file_service()
    demo_sheet_service()
    demo_architecture_benefits()
    
    print("=" * 70)
    print("✅ DÉMONSTRATION TERMINÉE AVEC SUCCÈS !")
    print("=" * 70)
    print()
    print("🎯 RÉSUMÉ DE LA TRANSFORMATION:")
    print("   • Code refactorisé selon Clean Architecture")
    print("   • Services métier spécialisés et testables")
    print("   • Modèles de données structurés et validés")
    print("   • Logging professionnel avec contexte")
    print("   • Architecture modulaire et évolutive")
    print()
    print("🚀 PRÊT POUR:")
    print("   • Développement d'équipe")
    print("   • Maintenance à long terme")
    print("   • Ajout de nouvelles fonctionnalités")
    print("   • Déploiement en production")
    print()
    print("🎉 Le système YAZAKI est maintenant professionnel et maintenable !")


if __name__ == "__main__":
    main()
