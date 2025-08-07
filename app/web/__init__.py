"""
Interface Web Flask pour le système YAZAKI
Application web moderne avec intégration API
"""

from flask import Flask
from pathlib import Path
import os

from ..utils.config import WEB_HOST, WEB_PORT, DEBUG_MODE
from ..utils.logger import setup_logger

logger = setup_logger("yazaki_web")

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)

    # Configuration
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'yazaki-dev-key-change-in-production'),
        'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB max file size
        'UPLOAD_FOLDER': str(Path(__file__).parent.parent.parent / 'storage' / 'uploads'),
        'PROCESSED_FOLDER': str(Path(__file__).parent.parent.parent / 'storage' / 'processed'),
        'DEBUG': DEBUG_MODE
    })

    # Créer les dossiers nécessaires
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(app.config['PROCESSED_FOLDER']).mkdir(parents=True, exist_ok=True)

    # Enregistrer les blueprints
    from .routes.main import main_bp
    from .routes.upload import upload_bp
    from .routes.processing import processing_bp
    from .routes.results import results_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(processing_bp, url_prefix='/processing')
    app.register_blueprint(results_bp, url_prefix='/results')

    logger.info("Flask application created successfully")
    return app