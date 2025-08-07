"""
Routes pour les résultats
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
import requests
from pathlib import Path
import tempfile
import os

from ...utils.logger import setup_logger
from ...utils.config import API_HOST, API_PORT

logger = setup_logger("yazaki_web_results")
results_bp = Blueprint('results', __name__)

# URL de base de l'API
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

@results_bp.route('/')
def results_page():
    """Page des résultats"""
    try:
        # Obtenir la liste des résultats
        response = requests.get(f"{API_BASE_URL}/results/list", timeout=15)
        
        results_data = []
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                results_data = result["data"]["results"]
        
        # Obtenir les statistiques
        stats_response = requests.get(f"{API_BASE_URL}/results/stats", timeout=10)
        stats_data = {}
        if stats_response.status_code == 200:
            stats_result = stats_response.json()
            if stats_result.get("success"):
                stats_data = stats_result["data"]
        
        return render_template('results.html', 
                             results=results_data,
                             stats=stats_data)
        
    except Exception as e:
        logger.error(f"Error loading results page: {e}")
        return render_template('results.html', results=[], stats={})

@results_bp.route('/view/<processing_id>')
def view_result(processing_id):
    """Voir un résultat spécifique"""
    try:
        # Pour l'instant, rediriger vers la page des résultats
        # TODO: Implémenter la vue détaillée d'un résultat
        flash(f'Traitement {processing_id} terminé avec succès', 'success')
        return redirect(url_for('results.results_page'))
        
    except Exception as e:
        logger.error(f"Error viewing result: {e}")
        flash(f'Erreur lors de l\'affichage du résultat: {str(e)}', 'error')
        return redirect(url_for('results.results_page'))

@results_bp.route('/download/<filename>')
def download_result(filename):
    """Télécharge un fichier de résultat"""
    try:
        # Obtenir le fichier depuis l'API
        response = requests.get(f"{API_BASE_URL}/results/download/{filename}", 
                              timeout=30, stream=True)
        
        if response.status_code == 200:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            # Envoyer le fichier
            return send_file(tmp_file_path, 
                           as_attachment=True,
                           download_name=filename,
                           mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            flash('Fichier non trouvé', 'error')
            return redirect(url_for('results.results_page'))
        
    except Exception as e:
        logger.error(f"Error downloading result: {e}")
        flash(f'Erreur lors du téléchargement: {str(e)}', 'error')
        return redirect(url_for('results.results_page'))

@results_bp.route('/delete/<filename>', methods=['POST'])
def delete_result(filename):
    """Supprime un résultat"""
    try:
        response = requests.delete(f"{API_BASE_URL}/results/delete/{filename}", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                flash(f'Résultat {filename} supprimé avec succès', 'success')
            else:
                flash(f'Erreur lors de la suppression: {result.get("message", "Erreur inconnue")}', 'error')
        else:
            flash('Erreur lors de la suppression du résultat', 'error')
        
        return redirect(url_for('results.results_page'))
        
    except Exception as e:
        logger.error(f"Error deleting result: {e}")
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
        return redirect(url_for('results.results_page'))

@results_bp.route('/metadata/<filename>')
def get_metadata(filename):
    """Obtient les métadonnées d'un résultat"""
    try:
        response = requests.get(f"{API_BASE_URL}/results/metadata/{filename}", timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({"success": False, "message": "Métadonnées non trouvées"}), 404
        
    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@results_bp.route('/api/status/<processing_id>')
def get_processing_status(processing_id):
    """Obtient le statut d'un traitement"""
    try:
        response = requests.get(f"{API_BASE_URL}/processing/status/{processing_id}", timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({"success": False, "message": "Statut non trouvé"}), 404
        
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
