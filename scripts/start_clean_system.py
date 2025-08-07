#!/usr/bin/env python3
"""
Script de démarrage pour le système YAZAKI refactorisé
Démarre l'API et l'interface web avec la nouvelle architecture propre
"""

import sys
import subprocess
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import signal
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.logger import configure_global_logging, get_structured_logger
from app.utils.config import API_HOST, API_PORT, WEB_HOST, WEB_PORT

# Configuration du logging
logger = get_structured_logger("system_starter")

class SystemStarter:
    """Gestionnaire de démarrage du système"""
    
    def __init__(self):
        self.api_process = None
        self.web_process = None
        self.running = True
        
        # Gestionnaire de signaux pour arrêt propre
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour arrêt propre"""
        logger.info("Signal received, shutting down...")
        self.running = False
        self.stop_all()
        sys.exit(0)
    
    def check_dependencies(self) -> bool:
        """Vérifie les dépendances du système"""
        logger.info("Checking system dependencies...")
        
        try:
            # Vérifier les imports Python
            import fastapi
            import flask
            import pandas
            import openpyxl
            logger.info("Python dependencies: OK")
            
            # Vérifier les fichiers de configuration
            from app.utils.config import MASTER_BOM_PATH, UPLOADS_DIR
            
            if not MASTER_BOM_PATH.exists():
                logger.warning(f"Master BOM not found: {MASTER_BOM_PATH}")
                return False
            
            # Créer les répertoires nécessaires
            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("File system: OK")
            
            return True
            
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            return False
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
            return False
    
    def start_api(self) -> bool:
        """Démarre l'API FastAPI"""
        logger.info(f"Starting API on {API_HOST}:{API_PORT}")
        
        try:
            # Commande pour démarrer l'API
            cmd = [
                sys.executable, "-m", "uvicorn",
                "app.api.main:app",
                "--host", API_HOST,
                "--port", str(API_PORT),
                "--reload"
            ]
            
            self.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent.parent
            )
            
            # Attendre que l'API soit prête
            if self._wait_for_service(f"http://{API_HOST}:{API_PORT}/health", "API"):
                logger.info("API started successfully")
                return True
            else:
                logger.error("API failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting API: {e}")
            return False
    
    def start_web(self) -> bool:
        """Démarre l'interface web Flask"""
        logger.info(f"Starting Web interface on {WEB_HOST}:{WEB_PORT}")
        
        try:
            # TODO: Créer l'interface web refactorisée
            # Pour l'instant, utiliser l'ancienne interface
            cmd = [
                sys.executable, "frontend_stable.py"
            ]
            
            self.web_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent.parent
            )
            
            # Attendre que l'interface web soit prête
            if self._wait_for_service(f"http://{WEB_HOST}:{WEB_PORT}", "Web interface"):
                logger.info("Web interface started successfully")
                return True
            else:
                logger.error("Web interface failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting web interface: {e}")
            return False
    
    def _wait_for_service(self, url: str, service_name: str, timeout: int = 30) -> bool:
        """Attend qu'un service soit prêt"""
        logger.info(f"Waiting for {service_name} to be ready...")
        
        for i in range(timeout):
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            if i % 5 == 0:
                logger.info(f"Still waiting for {service_name}... ({i}/{timeout}s)")
        
        return False
    
    def check_services_health(self) -> dict:
        """Vérifie la santé des services"""
        health_status = {
            "api": False,
            "web": False,
            "overall": False
        }
        
        # Vérifier l'API
        try:
            response = requests.get(f"http://{API_HOST}:{API_PORT}/health", timeout=5)
            health_status["api"] = response.status_code == 200
        except Exception:
            pass
        
        # Vérifier l'interface web
        try:
            response = requests.get(f"http://{WEB_HOST}:{WEB_PORT}/api/status", timeout=5)
            health_status["web"] = response.status_code == 200
        except Exception:
            pass
        
        health_status["overall"] = health_status["api"] and health_status["web"]
        
        return health_status
    
    def monitor_services(self):
        """Surveille les services en continu"""
        logger.info("Starting service monitoring...")
        
        while self.running:
            try:
                health = self.check_services_health()
                
                if not health["overall"]:
                    logger.warning("Service health check failed")
                    if not health["api"]:
                        logger.warning("API is not responding")
                    if not health["web"]:
                        logger.warning("Web interface is not responding")
                
                time.sleep(30)  # Vérifier toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                time.sleep(10)
    
    def stop_all(self):
        """Arrête tous les services"""
        logger.info("Stopping all services...")
        
        if self.api_process:
            logger.info("Stopping API...")
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.api_process.kill()
        
        if self.web_process:
            logger.info("Stopping Web interface...")
            self.web_process.terminate()
            try:
                self.web_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.web_process.kill()
        
        logger.info("All services stopped")
    
    def start_system(self) -> bool:
        """Démarre le système complet"""
        logger.info("=" * 60)
        logger.info("YAZAKI Component Processing System - Clean Architecture")
        logger.info("=" * 60)
        
        # Vérifier les dépendances
        if not self.check_dependencies():
            logger.error("Dependency check failed")
            return False
        
        # Démarrer les services
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Démarrer l'API en premier
            api_future = executor.submit(self.start_api)
            
            # Attendre un peu puis démarrer l'interface web
            time.sleep(3)
            web_future = executor.submit(self.start_web)
            
            # Attendre les résultats
            api_success = api_future.result()
            web_success = web_future.result()
        
        if api_success and web_success:
            logger.info("=" * 60)
            logger.info("SYSTEM STARTED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"API: http://{API_HOST}:{API_PORT}")
            logger.info(f"Web Interface: http://{WEB_HOST}:{WEB_PORT}")
            logger.info(f"API Documentation: http://{API_HOST}:{API_PORT}/docs")
            logger.info("=" * 60)
            
            # Démarrer la surveillance
            self.monitor_services()
            
            return True
        else:
            logger.error("Failed to start system")
            self.stop_all()
            return False


def main():
    """Fonction principale"""
    # Configurer le logging global
    configure_global_logging()
    
    # Démarrer le système
    starter = SystemStarter()
    
    try:
        success = starter.start_system()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        starter.stop_all()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        starter.stop_all()
        sys.exit(1)


if __name__ == "__main__":
    main()
