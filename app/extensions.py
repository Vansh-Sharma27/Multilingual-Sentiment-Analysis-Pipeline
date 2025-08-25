"""
Flask extensions initialization
Centralizes extension configuration and initialization
"""

import logging
from logging.handlers import RotatingFileHandler
import os

def init_extensions(app):
    """
    Initialize Flask extensions
    
    Args:
        app: Flask application instance
    """
    # Initialize logging
    init_logging(app)
    
    # Initialize other extensions here as needed
    # For example: db.init_app(app), migrate.init_app(app, db), etc.

def init_logging(app):
    """
    Configure application logging
    
    Args:
        app: Flask application instance
    """
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Set up file handler with rotation
        file_handler = RotatingFileHandler(
            f'logs/{app.config["LOG_FILE"]}',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        # Configure formatter
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        
        # Set log level from configuration
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('Multilingual Sentiment Analysis Pipeline startup')
