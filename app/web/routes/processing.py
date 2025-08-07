"""
Routes pour le traitement des données
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import requests
from pathlib import Path

from ...utils.logger import setup_logger
from ...utils.config import API_HOST, API_PORT

logger = setup_logger("yazaki_web_processing")
processing_bp = Blueprint('processing', __name__)

# URL de base de l'API
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

@processing_bp.route('/select-sheet/<filename>')
def select_sheet(filename):
    """Page de sélection de feuille"""
    try:
        # Analyser les feuilles du fichier
        response = requests.get(f"{API_BASE_URL}/sheets/analyze/{filename}", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                sheets_data = result["data"]
                return render_template('select_sheet.html', 
                                     filename=filename,
                                     sheets=sheets_data["sheets"])
            else:
                flash('Erreur lors de l\'analyse des feuilles', 'error')
        else:
            flash('Erreur lors de l\'analyse du fichier', 'error')
        
        return redirect(url_for('upload.upload_page'))
        
    except Exception as e:
        logger.error(f"Error analyzing sheets: {e}")
        flash(f'Erreur lors de l\'analyse: {str(e)}', 'error')
        return redirect(url_for('upload.upload_page'))

@processing_bp.route('/preview/<filename>/<sheet_name>')
def preview_sheet(filename, sheet_name):
    """Aperçu d'une feuille"""
    try:
        # Obtenir l'aperçu de la feuille
        response = requests.get(f"{API_BASE_URL}/sheets/preview/{filename}/{sheet_name}?rows=10", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                preview_data = result["data"]
                return render_template('preview_sheet.html',
                                     filename=filename,
                                     sheet_name=sheet_name,
                                     preview=preview_data["preview"])
            else:
                flash('Erreur lors de l\'aperçu', 'error')
        else:
            flash('Erreur lors de l\'aperçu de la feuille', 'error')
        
        return redirect(url_for('processing.select_sheet', filename=filename))
        
    except Exception as e:
        logger.error(f"Error previewing sheet: {e}")
        flash(f'Erreur lors de l\'aperçu: {str(e)}', 'error')
        return redirect(url_for('processing.select_sheet', filename=filename))

@processing_bp.route('/clean/<filename>/<sheet_name>')
def clean_data(filename, sheet_name):
    """Page de nettoyage des données"""
    try:
        # Analyser la qualité des données
        response = requests.post(f"{API_BASE_URL}/cleaning/analyze/{filename}/{sheet_name}", timeout=15)
        
        quality_data = {}
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                quality_data = result["data"]["quality_report"]
        
        # Obtenir les options de nettoyage par défaut
        options_response = requests.get(f"{API_BASE_URL}/cleaning/options/default", timeout=10)
        default_options = {}
        if options_response.status_code == 200:
            options_result = options_response.json()
            if options_result.get("success"):
                default_options = options_result["data"]["options"]
        
        return render_template('clean_data.html',
                             filename=filename,
                             sheet_name=sheet_name,
                             quality_data=quality_data,
                             default_options=default_options)
        
    except Exception as e:
        logger.error(f"Error loading clean page: {e}")
        flash(f'Erreur lors du chargement: {str(e)}', 'error')
        return redirect(url_for('processing.select_sheet', filename=filename))

@processing_bp.route('/process/<filename>/<sheet_name>')
def process_data(filename, sheet_name):
    """Page de traitement des données"""
    try:
        # Analyser le Master BOM
        bom_response = requests.post(f"{API_BASE_URL}/processing/analyze-master-bom", timeout=15)
        
        bom_analysis = {}
        if bom_response.status_code == 200:
            result = bom_response.json()
            if result.get("success"):
                bom_analysis = result["data"]["analysis"]
        
        return render_template('process_data.html',
                             filename=filename,
                             sheet_name=sheet_name,
                             bom_analysis=bom_analysis)
        
    except Exception as e:
        logger.error(f"Error loading process page: {e}")
        flash(f'Erreur lors du chargement: {str(e)}', 'error')
        return redirect(url_for('processing.select_sheet', filename=filename))

@processing_bp.route('/start', methods=['POST'])
def start_processing():
    """Démarre le traitement"""
    try:
        data = request.get_json() or request.form.to_dict()
        
        # Envoyer la requête de traitement à l'API
        response = requests.post(f"{API_BASE_URL}/processing/start", json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                processing_id = result["data"]["processing_id"]
                return jsonify({
                    "success": True,
                    "processing_id": processing_id,
                    "redirect_url": url_for('results.view_result', processing_id=processing_id)
                })
            else:
                return jsonify({"success": False, "message": "Erreur lors du traitement"})
        else:
            return jsonify({"success": False, "message": "Erreur API"}), 500
        
    except Exception as e:
        logger.error(f"Error starting processing: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@processing_bp.route('/api/clean', methods=['POST'])
def api_clean():
    """API endpoint pour le nettoyage"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        sheet_name = data.get('sheet_name')
        options = data.get('options', {})
        
        # Envoyer la requête de nettoyage à l'API
        response = requests.post(f"{API_BASE_URL}/cleaning/clean/{filename}/{sheet_name}", 
                               json=options, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({"success": False, "message": "Erreur API"}), 500
        
    except Exception as e:
        logger.error(f"Error in API clean: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
