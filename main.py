#!/usr/bin/env python3
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
