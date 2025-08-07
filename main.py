#!/usr/bin/env python3
"""
YAZAKI Component Processing System - Main Entry Point
Point d'entrée principal pour le système de traitement des composants
"""

import sys
import argparse
import threading
import time
import uvicorn
from pathlib import Path

# Ajouter le répertoire app au path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.utils.logger import setup_logger
from app.utils.config import API_HOST, API_PORT, WEB_HOST, WEB_PORT, DEBUG_MODE

logger = setup_logger("yazaki_main")

def start_api_server(host: str, port: int, debug: bool = False):
    """Démarre le serveur API FastAPI"""
    try:
        logger.info(f"Starting API server on {host}:{port}")
        uvicorn.run(
            "app.api.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug"
        )
    except Exception as e:
        logger.error(f"Error starting API server: {e}")

def start_web_server(host: str, port: int, debug: bool = False):
    """Démarre le serveur Web Flask"""
    try:
        logger.info(f"Starting Web server on {host}:{port}")
        from app.web import create_app

        app = create_app()
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=False  # Éviter les conflits avec uvicorn
        )
    except Exception as e:
        logger.error(f"Error starting Web server: {e}")

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="YAZAKI Component Processing System")
    parser.add_argument("--mode", choices=["api", "web", "both"], default="both",
                       help="Mode de démarrage: api, web, ou both")
    parser.add_argument("--port-api", type=int, default=API_PORT,
                       help=f"Port pour l'API (défaut: {API_PORT})")
    parser.add_argument("--port-web", type=int, default=WEB_PORT,
                       help=f"Port pour l'interface web (défaut: {WEB_PORT})")
    parser.add_argument("--debug", action="store_true", default=DEBUG_MODE,
                       help="Mode debug")

    args = parser.parse_args()

    print("🚀 YAZAKI Component Processing System v3.0.0")
    print("=" * 60)
    print("Clean Architecture - Production Ready")
    print("=" * 60)

    if args.mode == "api":
        print(f"📡 Démarrage API uniquement sur {API_HOST}:{args.port_api}")
        start_api_server(API_HOST, args.port_api, args.debug)

    elif args.mode == "web":
        print(f"🌐 Démarrage interface web uniquement sur {WEB_HOST}:{args.port_web}")
        start_web_server(WEB_HOST, args.port_web, args.debug)

    elif args.mode == "both":
        print(f"🔄 Mode complet: API + Interface Web")
        print(f"📡 API: http://{API_HOST}:{args.port_api}")
        print(f"🌐 Web: http://{WEB_HOST}:{args.port_web}")
        print("=" * 60)

        # Démarrer l'API dans un thread séparé
        api_thread = threading.Thread(
            target=start_api_server,
            args=(API_HOST, args.port_api, args.debug),
            daemon=True
        )
        api_thread.start()

        # Attendre un peu que l'API démarre
        time.sleep(2)

        # Démarrer l'interface web dans le thread principal
        start_web_server(WEB_HOST, args.port_web, args.debug)

if __name__ == "__main__":
    main()
