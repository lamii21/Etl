"""
Routes principales de l'interface web
"""

from flask import Blueprint, render_template, request, jsonify, current_app
import requests
import os
from pathlib import Path

from ...utils.logger import setup_logger
from ...utils.config import API_HOST, API_PORT

logger = setup_logger("yazaki_web_main")
main_bp = Blueprint('main', __name__)

# URL de base de l'API
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

@main_bp.route('/')
def home():
    """Page d'accueil"""
    try:
        # Obtenir les statistiques depuis l'API
        try:
            health_response = requests.get(f"{API_BASE_URL}/health/status", timeout=5)
            api_status = health_response.json() if health_response.status_code == 200 else {"status": "unknown"}
        except:
            api_status = {"status": "offline"}
        
        try:
            results_response = requests.get(f"{API_BASE_URL}/results/stats", timeout=5)
            results_stats = results_response.json().get("data", {}) if results_response.status_code == 200 else {}
        except:
            results_stats = {}
        
        return render_template('home.html', 
                             api_status=api_status,
                             results_stats=results_stats)
    except Exception as e:
        logger.error(f"Error loading home page: {e}")
        return render_template('home.html', 
                             api_status={"status": "error"},
                             results_stats={})

@main_bp.route('/health')
def health():
    """Page de santé du système"""
    try:
        # Vérifier l'API
        api_health = requests.get(f"{API_BASE_URL}/health/status", timeout=5)
        api_data = api_health.json() if api_health.status_code == 200 else {"status": "offline"}
        
        # Vérifier les dossiers
        upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
        processed_dir = Path(current_app.config['PROCESSED_FOLDER'])
        
        system_health = {
            "api": api_data,
            "storage": {
                "upload_folder": {
                    "exists": upload_dir.exists(),
                    "writable": upload_dir.exists() and os.access(upload_dir, os.W_OK),
                    "path": str(upload_dir)
                },
                "processed_folder": {
                    "exists": processed_dir.exists(),
                    "writable": processed_dir.exists() and os.access(processed_dir, os.W_OK),
                    "path": str(processed_dir)
                }
            },
            "web_app": {
                "status": "running",
                "debug_mode": current_app.config.get('DEBUG', False)
            }
        }
        
        return jsonify(system_health)
        
    except Exception as e:
        logger.error(f"Error checking health: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/about')
def about():
    """Page à propos"""
    return render_template('about.html')

@main_bp.errorhandler(404)
def not_found(error):
    """Page 404"""
    return render_template('error.html', 
                         error_code=404,
                         error_message="Page non trouvée"), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Page 500"""
    return render_template('error.html',
                         error_code=500,
                         error_message="Erreur interne du serveur"), 500
