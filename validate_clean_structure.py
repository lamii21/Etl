#!/usr/bin/env python3
"""
Validation de la structure propre du projet YAZAKI
Vérifie que le nettoyage a été effectué correctement
"""

import os
from pathlib import Path
import json

def validate_clean_structure():
    """Valide la structure propre du projet"""
    print("✅ VALIDATION DE LA STRUCTURE PROPRE")
    print("=" * 60)
    
    # Structure attendue après nettoyage
    expected_structure = {
        "directories": [
            "app",
            "app/api",
            "app/core",
            "app/core/models",
            "app/core/services",
            "app/core/processors",
            "app/utils",
            "app/web",
            "app/static",
            "data",
            "data/samples",
            "storage",
            "storage/uploads",
            "storage/processed",
            "storage/temp",
            "tests",
            "tests/unit",
            "tests/integration",
            "scripts",
            "docs"
        ],
        "essential_files": [
            "main.py",
            "requirements.txt",
            "data/Master_BOM_Real.xlsx",
            "app/utils/config.py",
            "app/utils/logger.py",
            "app/core/models/file_info.py",
            "app/core/models/sheet_info.py",
            "app/core/models/processing_result.py",
            "app/core/services/file_service.py",
            "app/core/services/sheet_service.py",
            "app/api/main.py",
            "app/api/routes/health.py",
            "tests/test_clean_architecture.py",
            "docs/CLEAN_ARCHITECTURE_SUMMARY.md"
        ],
        "obsolete_files_removed": [
            "backend_stable.py",
            "frontend_stable.py",
            "enhanced_lookup_processor.py",
            "data_cleaner.py",
            "config.py",
            "templates/",
            "uploads/",
            "output/"
        ]
    }
    
    validation_results = {
        "directories_ok": 0,
        "directories_missing": [],
        "files_ok": 0,
        "files_missing": [],
        "obsolete_removed": 0,
        "obsolete_still_present": []
    }
    
    # Vérifier les répertoires
    print("📁 Vérification des répertoires...")
    for directory in expected_structure["directories"]:
        dir_path = Path(directory)
        if dir_path.exists() and dir_path.is_dir():
            validation_results["directories_ok"] += 1
            print(f"   ✅ {directory}")
        else:
            validation_results["directories_missing"].append(directory)
            print(f"   ❌ {directory} - MANQUANT")
    
    # Vérifier les fichiers essentiels
    print("\n📄 Vérification des fichiers essentiels...")
    for file_path in expected_structure["essential_files"]:
        file_obj = Path(file_path)
        if file_obj.exists() and file_obj.is_file():
            validation_results["files_ok"] += 1
            print(f"   ✅ {file_path}")
        else:
            validation_results["files_missing"].append(file_path)
            print(f"   ❌ {file_path} - MANQUANT")
    
    # Vérifier que les fichiers obsolètes ont été supprimés
    print("\n🗑️  Vérification de la suppression des fichiers obsolètes...")
    for obsolete_item in expected_structure["obsolete_files_removed"]:
        obsolete_path = Path(obsolete_item)
        if not obsolete_path.exists():
            validation_results["obsolete_removed"] += 1
            print(f"   ✅ {obsolete_item} - SUPPRIMÉ")
        else:
            validation_results["obsolete_still_present"].append(obsolete_item)
            print(f"   ⚠️  {obsolete_item} - ENCORE PRÉSENT")
    
    return validation_results

def analyze_project_size():
    """Analyse la taille du projet après nettoyage"""
    print("\n📊 ANALYSE DE LA TAILLE DU PROJET")
    print("-" * 50)
    
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk("."):
        # Ignorer les dossiers de backup et cache
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'backup_before_cleanup']
        
        for file in files:
            if not file.startswith('.') and not file.endswith('.pyc'):
                file_path = Path(root) / file
                try:
                    file_size = file_path.stat().st_size
                    total_files += 1
                    total_size += file_size
                except Exception:
                    pass
    
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"   📁 Total fichiers: {total_files}")
    print(f"   💾 Taille totale: {total_size_mb:.2f} MB")
    
    return total_files, total_size_mb

def generate_final_structure_tree():
    """Génère l'arbre de la structure finale"""
    print("\n🌳 STRUCTURE FINALE DU PROJET")
    print("-" * 50)
    
    def print_tree(directory, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
        
        try:
            items = sorted(Path(directory).iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for i, item in enumerate(items):
                if item.name.startswith('.') or item.name == '__pycache__' or item.name == 'backup_before_cleanup':
                    continue
                
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                print(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir() and current_depth < max_depth - 1:
                    extension = "    " if is_last else "│   "
                    print_tree(item, prefix + extension, max_depth, current_depth + 1)
        except Exception:
            pass
    
    print("yazaki_system/")
    print_tree(".", max_depth=3)

def create_final_readme():
    """Crée un README final pour la structure propre"""
    print("\n📝 CRÉATION DU README FINAL")
    print("-" * 50)
    
    readme_content = """# YAZAKI Component Processing System - Clean Architecture

## 🎯 **Système de Traitement des Composants YAZAKI**

Version refactorisée avec architecture propre et modulaire.

---

## 🏗️ **Architecture**

### **Structure du Projet**
```
yazaki_system/
├── 📁 app/                          # Application principale
│   ├── 📁 api/                      # API FastAPI
│   ├── 📁 core/                     # Logique métier
│   │   ├── 📁 models/               # Modèles de données
│   │   ├── 📁 services/             # Services métier
│   │   └── 📁 processors/           # Processeurs de données
│   ├── 📁 utils/                    # Utilitaires communs
│   └── 📁 web/                      # Interface Web (à implémenter)
├── 📁 data/                         # Données (Master BOM)
├── 📁 storage/                      # Stockage (uploads, traités)
├── 📁 tests/                        # Tests automatisés
├── 📁 scripts/                      # Scripts utilitaires
└── 📁 docs/                         # Documentation
```

---

## 🚀 **Démarrage Rapide**

### **1. Installation**
```bash
pip install -r requirements.txt
```

### **2. Démarrage du Système**
```bash
# Démarrage complet (API + Web)
python main.py

# Ou utiliser le script de démarrage
python scripts/start_clean_system.py
```

### **3. Accès aux Services**
- **API:** http://localhost:8000
- **Documentation API:** http://localhost:8000/docs
- **Interface Web:** http://localhost:5000 (à implémenter)

---

## 🔧 **Fonctionnalités**

### **✅ Fonctionnalités Implémentées**
- 🏗️ Architecture modulaire propre
- 📊 Modèles de données structurés
- ⚙️ Services métier spécialisés
- 📝 Logging professionnel
- 🧪 Tests automatisés
- 📋 Analyse multi-feuilles Excel
- 🧹 Nettoyage des données

### **🔄 À Implémenter**
- 🌐 Interface Web refactorisée
- 🔧 Services de traitement complets
- 📊 Monitoring et métriques
- 🚀 Déploiement automatisé

---

## 📚 **Documentation**

- **Architecture:** [docs/CLEAN_ARCHITECTURE_SUMMARY.md](docs/CLEAN_ARCHITECTURE_SUMMARY.md)
- **Guide Utilisateur:** [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- **Rapport de Nettoyage:** [docs/CLEANUP_REPORT.json](docs/CLEANUP_REPORT.json)

---

## 🧪 **Tests**

```bash
# Exécuter tous les tests
python -m pytest tests/

# Tests spécifiques
python tests/test_clean_architecture.py
```

---

## 🎯 **Avantages de la Nouvelle Architecture**

### **🏗️ Clean Architecture**
- Séparation claire des responsabilités
- Code modulaire et maintenable
- Services testables unitairement

### **📊 Qualité du Code**
- Modèles de données validés
- Logging structuré
- Gestion d'erreurs robuste

### **🚀 Évolutivité**
- Architecture prête pour nouvelles fonctionnalités
- Déploiement facilité
- Maintenance simplifiée

---

## 👥 **Équipe de Développement**

Ce projet utilise une architecture propre facilitant :
- Le développement en équipe
- La maintenance à long terme
- L'ajout de nouvelles fonctionnalités
- Les tests automatisés

---

## 📄 **Licence**

Système propriétaire YAZAKI - Usage interne uniquement.

---

*Dernière mise à jour: 2025-08-06 - Version Clean Architecture*
"""
    
    readme_path = Path("README.md")
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"   ✅ README.md final créé")

def main():
    """Fonction principale de validation"""
    print("🔍 VALIDATION DE LA STRUCTURE PROPRE DU PROJET YAZAKI")
    print("=" * 70)
    
    # Validation de la structure
    results = validate_clean_structure()
    
    # Analyse de la taille
    total_files, total_size_mb = analyze_project_size()
    
    # Arbre de structure
    generate_final_structure_tree()
    
    # README final
    create_final_readme()
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DE LA VALIDATION")
    print("=" * 70)
    
    print(f"✅ Répertoires validés: {results['directories_ok']}/{len(results['directories_ok']) + len(results['directories_missing'])}")
    print(f"✅ Fichiers essentiels: {results['files_ok']}/{len(results['files_ok']) + len(results['files_missing'])}")
    print(f"✅ Fichiers obsolètes supprimés: {results['obsolete_removed']}")
    print(f"📁 Total fichiers: {total_files}")
    print(f"💾 Taille projet: {total_size_mb:.2f} MB")
    
    if results['directories_missing'] or results['files_missing']:
        print(f"\n⚠️  Éléments manquants:")
        for item in results['directories_missing'] + results['files_missing']:
            print(f"   • {item}")
    
    if results['obsolete_still_present']:
        print(f"\n⚠️  Fichiers obsolètes encore présents:")
        for item in results['obsolete_still_present']:
            print(f"   • {item}")
    
    # Score de validation
    total_expected = (len(results['directories_ok']) + len(results['directories_missing']) + 
                     len(results['files_ok']) + len(results['files_missing']))
    total_valid = results['directories_ok'] + results['files_ok']
    
    if total_expected > 0:
        validation_score = (total_valid / total_expected) * 100
        print(f"\n🎯 Score de validation: {validation_score:.1f}%")
        
        if validation_score >= 90:
            print("🎉 STRUCTURE PROPRE VALIDÉE AVEC SUCCÈS !")
            print("✅ Le projet est prêt pour le développement")
        elif validation_score >= 75:
            print("⚠️  Structure majoritairement correcte")
            print("💡 Quelques ajustements mineurs nécessaires")
        else:
            print("❌ Structure incomplète")
            print("🔧 Corrections nécessaires avant utilisation")
    
    print("\n🚀 PROCHAINES ÉTAPES:")
    print("   1. Implémenter l'interface web dans app/web/")
    print("   2. Compléter les services de traitement")
    print("   3. Ajouter plus de tests")
    print("   4. Configurer le déploiement")

if __name__ == "__main__":
    main()
