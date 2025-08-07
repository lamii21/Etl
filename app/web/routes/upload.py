"""
Routes pour l'upload de fichiers
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
import requests
from werkzeug.utils import secure_filename
import os
from pathlib import Path

from ...utils.logger import setup_logger
from ...utils.config import API_HOST, API_PORT

logger = setup_logger("yazaki_web_upload")
upload_bp = Blueprint('upload', __name__)

# URL de base de l'API
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

@upload_bp.route('/')
def upload_page():
    """Page d'upload"""
    try:
        # Obtenir la liste des fichiers uploadés
        response = requests.get(f"{API_BASE_URL}/upload/files", timeout=10)
        files_data = response.json().get("data", {"files": []}) if response.status_code == 200 else {"files": []}
        
        return render_template('upload.html', files=files_data.get("files", []))
    except Exception as e:
        logger.error(f"Error loading upload page: {e}")
        return render_template('upload.html', files=[])

@upload_bp.route('/file', methods=['POST'])
def upload_file():
    """Upload un fichier"""
    try:
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(url_for('upload.upload_page'))
        
        file = request.files['file']
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(url_for('upload.upload_page'))
        
        if file and allowed_file(file.filename):
            # Envoyer le fichier à l'API
            files = {'file': (file.filename, file.stream, file.content_type)}
            response = requests.post(f"{API_BASE_URL}/upload/file", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    flash(f'Fichier {file.filename} uploadé avec succès', 'success')
                    return redirect(url_for('processing.select_sheet', 
                                          filename=result["data"]["safe_filename"]))
                else:
                    flash(f'Erreur lors de l\'upload: {result.get("message", "Erreur inconnue")}', 'error')
            else:
                flash('Erreur lors de l\'upload du fichier', 'error')
        else:
            flash('Type de fichier non autorisé. Seuls les fichiers Excel (.xlsx, .xls) sont acceptés.', 'error')
        
        return redirect(url_for('upload.upload_page'))
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        flash(f'Erreur lors de l\'upload: {str(e)}', 'error')
        return redirect(url_for('upload.upload_page'))

@upload_bp.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """Supprime un fichier uploadé"""
    try:
        response = requests.delete(f"{API_BASE_URL}/upload/file/{filename}", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                flash(f'Fichier {filename} supprimé avec succès', 'success')
            else:
                flash(f'Erreur lors de la suppression: {result.get("message", "Erreur inconnue")}', 'error')
        else:
            flash('Erreur lors de la suppression du fichier', 'error')
        
        return redirect(url_for('upload.upload_page'))
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
        return redirect(url_for('upload.upload_page'))

@upload_bp.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint pour upload AJAX"""
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "Aucun fichier"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "Nom de fichier vide"}), 400
        
        if file and allowed_file(file.filename):
            # Envoyer le fichier à l'API
            files = {'file': (file.filename, file.stream, file.content_type)}
            response = requests.post(f"{API_BASE_URL}/upload/file", files=files, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return jsonify({"success": False, "message": "Erreur API"}), 500
        else:
            return jsonify({"success": False, "message": "Type de fichier non autorisé"}), 400
        
    except Exception as e:
        logger.error(f"Error in API upload: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def allowed_file(filename):
    """Vérifie si le fichier est autorisé"""
    ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS
