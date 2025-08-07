#!/usr/bin/env python3
"""
Script pour créer la nouvelle structure de projet propre
Organise le code existant dans une architecture modulaire
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Crée la nouvelle structure de répertoires"""
    print("🏗️  Création de la nouvelle structure de répertoires...")
    
    # Structure des répertoires
    directories = [
        "app",
        "app/api",
        "app/api/routes",
        "app/web", 
        "app/web/routes",
        "app/web/templates",
        "app/core",
        "app/core/models",
        "app/core/services", 
        "app/core/processors",
        "app/utils",
        "app/static",
        "app/static/css",
        "app/static/js",
        "app/static/images",
        "data",
        "data/samples",
        "storage",
        "storage/uploads",
        "storage/processed", 
        "storage/temp",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
        "scripts",
        "docs"
    ]
    
    # Créer les répertoires
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Créer __init__.py pour les packages Python
        if directory.startswith("app/") and not directory.endswith(("static", "templates", "css", "js", "images")):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Package initialization"""')
    
    print(f"   ✅ {len(directories)} répertoires créés")

def create_init_files():
    """Crée les fichiers __init__.py manquants"""
    print("📝 Création des fichiers __init__.py...")
    
    init_files = [
        "tests/__init__.py",
        "tests/unit/__init__.py", 
        "tests/integration/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).write_text('"""Package initialization"""')
    
    print(f"   ✅ {len(init_files)} fichiers __init__.py créés")

def move_existing_files():
    """Déplace les fichiers existants vers la nouvelle structure"""
    print("📦 Migration des fichiers existants...")
    
    # Mapping des fichiers à déplacer
    file_moves = [
        # Data files
        ("Master_BOM_Real.xlsx", "data/Master_BOM_Real.xlsx"),
        ("Sample_Input_Data.xlsx", "data/samples/Sample_Input_Data.xlsx"),
        
        # Templates
        ("templates/base_stable.html", "app/web/templates/base.html"),
        ("templates/index_stable.html", "app/web/templates/home.html"),
        ("templates/upload_complete.html", "app/web/templates/processing.html"),
        ("templates/results.html", "app/web/templates/results.html"),
        
        # Core processors
        ("data_cleaner.py", "app/core/processors/data_cleaner.py"),
        ("enhanced_lookup_processor.py", "app/core/processors/lookup_processor.py"),
        
        # Documentation
        ("README.md", "docs/README.md"),
        ("GUIDE_UTILISATION_FINAL.md", "docs/USER_GUIDE.md"),
    ]
    
    moved_count = 0
    for source, destination in file_moves:
        source_path = Path(source)
        dest_path = Path(destination)
        
        if source_path.exists():
            # Créer le répertoire de destination si nécessaire
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copier le fichier (garder l'original pour l'instant)
            shutil.copy2(source_path, dest_path)
            moved_count += 1
            print(f"   📄 {source} → {destination}")
    
    print(f"   ✅ {moved_count} fichiers migrés")

def create_main_entry_point():
    """Crée le point d'entrée principal"""
    print("🚀 Création du point d'entrée principal...")
    
    main_content = '''#!/usr/bin/env python3
"""
YAZAKI Component Processing System - Main Entry Point
Point d'entrée principal pour le système de traitement des composants
"""

import sys
import argparse
from pathlib import Path

# Ajouter le répertoire app au path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="YAZAKI Component Processing System")
    parser.add_argument("--mode", choices=["api", "web", "both"], default="both",
                       help="Mode de démarrage: api, web, ou both")
    parser.add_argument("--port-api", type=int, default=8000,
                       help="Port pour l'API (défaut: 8000)")
    parser.add_argument("--port-web", type=int, default=5000,
                       help="Port pour l'interface web (défaut: 5000)")
    parser.add_argument("--debug", action="store_true",
                       help="Mode debug")
    
    args = parser.parse_args()
    
    print("YAZAKI Component Processing System")
    print("=" * 50)

    if args.mode in ["api", "both"]:
        print(f"Demarrage API sur port {args.port_api}")
        # TODO: Importer et démarrer l'API

    if args.mode in ["web", "both"]:
        print(f"Demarrage interface web sur port {args.port_web}")
        # TODO: Importer et démarrer l'interface web

    if args.mode == "both":
        print("Mode complet: API + Interface Web")
        # TODO: Démarrer les deux services

if __name__ == "__main__":
    main()
'''
    
    Path("main.py").write_text(main_content, encoding='utf-8')
    print("   ✅ main.py créé")

def create_configuration():
    """Crée les fichiers de configuration"""
    print("⚙️  Création des fichiers de configuration...")
    
    # Configuration principale
    config_content = '''"""
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
'''
    
    Path("app/utils/config.py").write_text(config_content, encoding='utf-8')

    # Fichier .env.example
    env_example = '''# YAZAKI Component Processing System - Environment Variables

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Web Configuration
WEB_HOST=0.0.0.0
WEB_PORT=5000

# Logging
LOG_LEVEL=INFO

# Development/Production
DEBUG=False
ENVIRONMENT=development
'''

    Path(".env.example").write_text(env_example, encoding='utf-8')
    
    print("   ✅ Fichiers de configuration créés")

def create_gitignore():
    """Crée le fichier .gitignore"""
    print("📝 Création du .gitignore...")
    
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Storage
storage/uploads/*
storage/processed/*
storage/temp/*
!storage/uploads/.gitkeep
!storage/processed/.gitkeep
!storage/temp/.gitkeep

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
'''
    
    Path(".gitignore").write_text(gitignore_content, encoding='utf-8')
    print("   ✅ .gitignore créé")

def create_gitkeep_files():
    """Crée les fichiers .gitkeep pour les répertoires vides"""
    print("📁 Création des fichiers .gitkeep...")
    
    gitkeep_dirs = [
        "storage/uploads",
        "storage/processed", 
        "storage/temp",
        "app/static/css",
        "app/static/js",
        "app/static/images"
    ]
    
    for directory in gitkeep_dirs:
        gitkeep_file = Path(directory) / ".gitkeep"
        gitkeep_file.write_text("")
    
    print(f"   ✅ {len(gitkeep_dirs)} fichiers .gitkeep créés")

def main():
    """Fonction principale"""
    print("🧹 NETTOYAGE ET ORGANISATION DU CODE YAZAKI")
    print("=" * 60)
    
    # Créer la structure
    create_directory_structure()
    create_init_files()
    move_existing_files()
    create_main_entry_point()
    create_configuration()
    create_gitignore()
    create_gitkeep_files()
    
    print("\n" + "=" * 60)
    print("✅ STRUCTURE PROPRE CRÉÉE AVEC SUCCÈS !")
    print("\n📁 Nouvelle structure:")
    print("   • app/ - Application principale")
    print("   • data/ - Données (Master BOM, échantillons)")
    print("   • storage/ - Stockage (uploads, traités, temp)")
    print("   • tests/ - Tests unitaires et d'intégration")
    print("   • scripts/ - Scripts utilitaires")
    print("   • docs/ - Documentation")
    print("\n🚀 Prochaines étapes:")
    print("   1. Refactoriser l'API dans app/api/")
    print("   2. Refactoriser l'interface web dans app/web/")
    print("   3. Créer les services dans app/core/services/")
    print("   4. Migrer les tests dans tests/")
    print("   5. Mettre à jour la documentation")

if __name__ == "__main__":
    main()
