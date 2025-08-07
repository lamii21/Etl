#!/usr/bin/env python3
"""
Script de nettoyage intelligent du projet YAZAKI
Supprime les fichiers obsolètes et garde seulement la nouvelle architecture propre
"""

import os
import shutil
from pathlib import Path
import json

def analyze_project_structure():
    """Analyse la structure actuelle du projet"""
    print("🔍 ANALYSE DE LA STRUCTURE ACTUELLE")
    print("-" * 50)
    
    # Fichiers à conserver (nouvelle architecture)
    keep_files = {
        # Nouvelle architecture
        "app/",
        "data/",
        "storage/",
        "tests/",
        "scripts/",
        "docs/",
        
        # Fichiers de configuration essentiels
        "main.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        
        # Documentation importante
        "docs/CLEAN_ARCHITECTURE_SUMMARY.md",
        "docs/README.md",
        "docs/USER_GUIDE.md",
        
        # Scripts utilitaires
        "demo_clean_architecture.py",
        "setup_clean_structure.py",
        
        # Données essentielles
        "data/Master_BOM_Real.xlsx",
        "data/samples/Sample_Input_Data.xlsx"
    }
    
    # Fichiers/dossiers obsolètes à supprimer
    obsolete_items = [
        # Anciens backends
        "backend_simple.py",
        "backend_stable.py",
        "simple_web.py",
        
        # Anciens frontends
        "frontend_stable.py",
        "frontend_api_client.py",
        "frontend_api_client_stable.py",
        "enhanced_web_interface.html",
        
        # Anciens processeurs
        "simple_lookup_processor.py",
        "enhanced_lookup_processor.py",
        "data_cleaner.py",
        
        # Anciens scripts de démarrage
        "START_STABLE_SYSTEM.py",
        "START_SYSTEM.py",
        "runner.py",
        
        # Ancienne configuration
        "config.py",
        
        # Anciens tests dispersés
        "test_complete_processing.py",
        "test_complete_system.py",
        "test_data_cleaning.py",
        "test_distribution_functionality.py",
        "test_download_fix.py",
        "test_download_functionality.py",
        "test_english_interface.py",
        "test_interface_unique.py",
        "test_main_file_identification.py",
        "test_sheet_selection.py",
        "test_stable_system.py",
        
        # Scripts d'analyse obsolètes
        "analyze_master_bom_management.py",
        "translate_to_english.py",
        
        # Anciens templates
        "templates/",
        
        # Ancien dossier frontend
        "frontend/",
        
        # Ancien dossier src
        "src/",
        
        # Anciens uploads
        "uploads/",
        "frontend_uploads/",
        
        # Anciens outputs
        "output/",
        
        # Logs obsolètes
        "*.log",
        
        # Documentation obsolète
        "README.md",
        "README_FINAL.md",
        "GUIDE_UTILISATION_FINAL.md",
        "GUIDE_TELECHARGEMENT.md",
        "project_structure.md",
        "master_bom_documentation.json",
        
        # Cache Python
        "__pycache__/",
        "*.pyc",
        "*.pyo"
    ]
    
    return keep_files, obsolete_items

def backup_important_files():
    """Sauvegarde les fichiers importants avant nettoyage"""
    print("💾 SAUVEGARDE DES FICHIERS IMPORTANTS")
    print("-" * 50)
    
    backup_dir = Path("backup_before_cleanup")
    backup_dir.mkdir(exist_ok=True)
    
    important_files = [
        "Master_BOM_Real.xlsx",
        "Sample_Input_Data.xlsx",
        "requirements.txt"
    ]
    
    backed_up = 0
    for file_name in important_files:
        # Chercher le fichier dans le projet
        for file_path in Path(".").rglob(file_name):
            if file_path.is_file():
                backup_path = backup_dir / file_name
                if not backup_path.exists():
                    shutil.copy2(file_path, backup_path)
                    print(f"   ✅ Sauvegardé: {file_name}")
                    backed_up += 1
                    break
    
    print(f"   📦 {backed_up} fichiers sauvegardés dans {backup_dir}")
    return backup_dir

def clean_obsolete_files(obsolete_items):
    """Supprime les fichiers et dossiers obsolètes"""
    print("\n🗑️  SUPPRESSION DES FICHIERS OBSOLÈTES")
    print("-" * 50)
    
    removed_count = 0
    
    for item_pattern in obsolete_items:
        # Gérer les patterns avec wildcards
        if "*" in item_pattern:
            for path in Path(".").glob(item_pattern):
                if path.exists():
                    try:
                        if path.is_file():
                            path.unlink()
                            print(f"   🗑️  Supprimé fichier: {path}")
                        elif path.is_dir():
                            shutil.rmtree(path)
                            print(f"   🗑️  Supprimé dossier: {path}")
                        removed_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Erreur suppression {path}: {e}")
        else:
            path = Path(item_pattern)
            if path.exists():
                try:
                    if path.is_file():
                        path.unlink()
                        print(f"   🗑️  Supprimé fichier: {path}")
                    elif path.is_dir():
                        shutil.rmtree(path)
                        print(f"   🗑️  Supprimé dossier: {path}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ⚠️  Erreur suppression {path}: {e}")
    
    print(f"   📊 {removed_count} éléments supprimés")
    return removed_count

def organize_remaining_files():
    """Organise les fichiers restants dans la nouvelle structure"""
    print("\n📁 ORGANISATION DES FICHIERS RESTANTS")
    print("-" * 50)
    
    # Déplacer Master_BOM_Real.xlsx vers data/ s'il n'y est pas déjà
    master_bom_root = Path("Master_BOM_Real.xlsx")
    master_bom_data = Path("data/Master_BOM_Real.xlsx")
    
    if master_bom_root.exists() and not master_bom_data.exists():
        master_bom_data.parent.mkdir(exist_ok=True)
        shutil.move(str(master_bom_root), str(master_bom_data))
        print(f"   📄 Déplacé: Master_BOM_Real.xlsx → data/")
    
    # Déplacer Sample_Input_Data.xlsx vers data/samples/
    sample_root = Path("Sample_Input_Data.xlsx")
    sample_data = Path("data/samples/Sample_Input_Data.xlsx")
    
    if sample_root.exists() and not sample_data.exists():
        sample_data.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(sample_root), str(sample_data))
        print(f"   📄 Déplacé: Sample_Input_Data.xlsx → data/samples/")
    
    # Nettoyer les répertoires vides
    empty_dirs_removed = 0
    for root, dirs, files in os.walk(".", topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    empty_dirs_removed += 1
            except Exception:
                pass
    
    if empty_dirs_removed > 0:
        print(f"   🗂️  Supprimé {empty_dirs_removed} répertoires vides")

def create_clean_requirements():
    """Crée un fichier requirements.txt propre"""
    print("\n📋 CRÉATION DU REQUIREMENTS.TXT PROPRE")
    print("-" * 50)
    
    clean_requirements = """# YAZAKI Component Processing System - Clean Architecture
# Dependencies for the refactored system

# Core dependencies
fastapi>=0.68.0
uvicorn[standard]>=0.15.0
flask>=2.0.0
pandas>=1.3.0
openpyxl>=3.0.0
requests>=2.25.0

# Development dependencies
pytest>=6.0.0
pytest-asyncio>=0.15.0

# Optional dependencies for enhanced features
python-multipart>=0.0.5
aiofiles>=0.7.0
"""
    
    requirements_path = Path("requirements.txt")
    requirements_path.write_text(clean_requirements, encoding='utf-8')
    print(f"   ✅ Requirements.txt propre créé")

def generate_cleanup_report():
    """Génère un rapport de nettoyage"""
    print("\n📊 GÉNÉRATION DU RAPPORT DE NETTOYAGE")
    print("-" * 50)
    
    # Analyser la structure finale
    final_structure = {}
    
    for root, dirs, files in os.walk("."):
        # Ignorer les dossiers cachés et __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        level = root.replace(".", "").count(os.sep)
        if level < 3:  # Limiter la profondeur
            indent = " " * 2 * level
            final_structure[root] = {
                "dirs": dirs.copy(),
                "files": [f for f in files if not f.startswith('.') and not f.endswith('.pyc')]
            }
    
    # Créer le rapport
    report = {
        "cleanup_date": "2025-08-06",
        "project_name": "YAZAKI Component Processing System",
        "architecture": "Clean Architecture",
        "final_structure": final_structure,
        "key_components": {
            "api": "app/api/ - FastAPI backend refactorisé",
            "core": "app/core/ - Logique métier et services",
            "utils": "app/utils/ - Utilitaires communs",
            "data": "data/ - Master BOM et échantillons",
            "storage": "storage/ - Stockage organisé",
            "tests": "tests/ - Tests automatisés",
            "docs": "docs/ - Documentation"
        },
        "benefits": [
            "Code organisé selon Clean Architecture",
            "Services métier spécialisés",
            "Modèles de données structurés",
            "Logging professionnel",
            "Tests automatisés",
            "Documentation complète"
        ]
    }
    
    report_path = Path("docs/CLEANUP_REPORT.json")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"   📄 Rapport généré: {report_path}")
    return report

def main():
    """Fonction principale de nettoyage"""
    print("🧹 NETTOYAGE COMPLET DU PROJET YAZAKI")
    print("=" * 60)
    print("Suppression des fichiers obsolètes et organisation de la nouvelle architecture")
    print("=" * 60)
    
    # Analyser la structure
    keep_files, obsolete_items = analyze_project_structure()
    
    # Demander confirmation
    print(f"\n⚠️  ATTENTION: Ce script va supprimer {len(obsolete_items)} types d'éléments obsolètes")
    print("Les fichiers importants seront sauvegardés avant suppression.")
    
    response = input("\nContinuer le nettoyage ? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Nettoyage annulé")
        return
    
    # Effectuer le nettoyage
    backup_dir = backup_important_files()
    removed_count = clean_obsolete_files(obsolete_items)
    organize_remaining_files()
    create_clean_requirements()
    report = generate_cleanup_report()
    
    # Résumé final
    print("\n" + "=" * 60)
    print("✅ NETTOYAGE TERMINÉ AVEC SUCCÈS !")
    print("=" * 60)
    print(f"📊 Statistiques:")
    print(f"   • {removed_count} éléments obsolètes supprimés")
    print(f"   • Fichiers sauvegardés dans: {backup_dir}")
    print(f"   • Structure organisée selon Clean Architecture")
    print(f"   • Rapport généré: docs/CLEANUP_REPORT.json")
    
    print(f"\n🎯 Structure finale:")
    print(f"   📁 app/ - Application principale (nouvelle architecture)")
    print(f"   📁 data/ - Données (Master BOM, échantillons)")
    print(f"   📁 storage/ - Stockage organisé")
    print(f"   📁 tests/ - Tests automatisés")
    print(f"   📁 docs/ - Documentation")
    print(f"   📁 scripts/ - Scripts utilitaires")
    
    print(f"\n🚀 Prêt pour:")
    print(f"   ✅ Développement avec architecture propre")
    print(f"   ✅ Maintenance facilitée")
    print(f"   ✅ Tests automatisés")
    print(f"   ✅ Déploiement en production")
    
    print(f"\n🎉 Le projet YAZAKI est maintenant propre et organisé !")

if __name__ == "__main__":
    main()
