"""
Point d'entrée principal pour l'interface web Flask
"""

from . import create_app
from ..utils.config import WEB_HOST, WEB_PORT, DEBUG_MODE
from ..utils.logger import setup_logger

logger = setup_logger("yazaki_web_main")

def run_web_app():
    """Lance l'application web Flask"""
    try:
        app = create_app()
        
        logger.info(f"Starting YAZAKI Web Interface on {WEB_HOST}:{WEB_PORT}")
        logger.info(f"Debug mode: {DEBUG_MODE}")
        
        app.run(
            host=WEB_HOST,
            port=WEB_PORT,
            debug=DEBUG_MODE,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Error starting web application: {e}")
        raise

if __name__ == "__main__":
    run_web_app()
