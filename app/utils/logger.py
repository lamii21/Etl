"""
Configuration du système de logging
Logging centralisé et structuré pour le système YAZAKI
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from .config import LOG_LEVEL, BASE_DIR


def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure un logger avec formatage structuré
    
    Args:
        name: Nom du logger
        log_file: Fichier de log optionnel
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # Format des messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour fichier si spécifié
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotation des logs (10MB max, 5 fichiers)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_default_log_file(component: str) -> str:
    """
    Obtient le chemin du fichier de log par défaut
    
    Args:
        component: Nom du composant (api, web, etc.)
        
    Returns:
        Chemin du fichier de log
    """
    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    return str(logs_dir / f"yazaki_{component}_{date_str}.log")


# Loggers pré-configurés pour les composants principaux
def get_api_logger() -> logging.Logger:
    """Logger pour l'API"""
    return setup_logger("yazaki_api", get_default_log_file("api"))


def get_web_logger() -> logging.Logger:
    """Logger pour l'interface web"""
    return setup_logger("yazaki_web", get_default_log_file("web"))


def get_service_logger(service_name: str) -> logging.Logger:
    """Logger pour un service spécifique"""
    return setup_logger(f"yazaki_service_{service_name}", get_default_log_file("services"))


def get_processor_logger(processor_name: str) -> logging.Logger:
    """Logger pour un processeur spécifique"""
    return setup_logger(f"yazaki_processor_{processor_name}", get_default_log_file("processors"))


class StructuredLogger:
    """
    Logger structuré avec contexte
    Permet d'ajouter du contexte aux messages de log
    """
    
    def __init__(self, logger: logging.Logger, context: dict = None):
        self.logger = logger
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """Formate le message avec le contexte"""
        if self.context:
            context_str = " | ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"{message} | {context_str}"
        return message
    
    def debug(self, message: str, **kwargs):
        """Log debug avec contexte"""
        full_context = {**self.context, **kwargs}
        self.logger.debug(self._format_message(message))
    
    def info(self, message: str, **kwargs):
        """Log info avec contexte"""
        full_context = {**self.context, **kwargs}
        self.logger.info(self._format_message(message))
    
    def warning(self, message: str, **kwargs):
        """Log warning avec contexte"""
        full_context = {**self.context, **kwargs}
        self.logger.warning(self._format_message(message))
    
    def error(self, message: str, **kwargs):
        """Log error avec contexte"""
        full_context = {**self.context, **kwargs}
        self.logger.error(self._format_message(message))
    
    def critical(self, message: str, **kwargs):
        """Log critical avec contexte"""
        full_context = {**self.context, **kwargs}
        self.logger.critical(self._format_message(message))
    
    def with_context(self, **context) -> 'StructuredLogger':
        """Crée un nouveau logger avec contexte additionnel"""
        new_context = {**self.context, **context}
        return StructuredLogger(self.logger, new_context)


def get_structured_logger(name: str, context: dict = None) -> StructuredLogger:
    """
    Obtient un logger structuré
    
    Args:
        name: Nom du logger
        context: Contexte initial
        
    Returns:
        Logger structuré
    """
    base_logger = setup_logger(name)
    return StructuredLogger(base_logger, context)


# Configuration globale du logging
def configure_global_logging():
    """Configure le logging global pour l'application"""
    # Désactiver les logs trop verbeux des librairies externes
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("pandas").setLevel(logging.WARNING)
    
    # Logger racine pour l'application
    root_logger = setup_logger("yazaki", get_default_log_file("main"))
    root_logger.info("YAZAKI Component Processing System - Logging initialized")
    
    return root_logger
