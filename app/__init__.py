"""
Flask Application Factory
Initializes and configures the Flask application with extensions and blueprints
"""

from flask import Flask, render_template, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

def create_app(config_name='development'):
    """
    Application factory function
    Creates and configures the Flask application
    
    Args:
        config_name: Configuration environment name
    
    Returns:
        Flask application instance
    """
    # Load environment variables
    load_dotenv()
    
    # Create Flask app instance
    app = Flask(__name__, template_folder="../frontend", static_url_path="", static_folder="../frontend")

    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])

    # Initialize extensions
    from app.extensions import init_extensions
    init_extensions(app)

    # Enable CORS for API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.routes.api_routes import api_bp
    from app.routes.upload_routes_enhanced import upload_enhanced_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(upload_enhanced_bp, url_prefix='/api/upload')

    @app.route('/')
    def index():
        return render_template("index.html")
    
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.svg')
    
    @app.route('/favicon.svg')
    def favicon_svg():
        return app.send_static_file('favicon.svg')

    # Create upload directory if it doesn't exist
    upload_path = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """
    Register application-wide error handlers
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(404)
    def not_found_error(error):
        # Check if this is an API request
        if request.path.startswith('/api/'):
            return {'error': 'Resource not found'}, 404
        # For non-API requests, serve index.html (SPA routing)
        return render_template("index.html"), 200
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return {'error': 'Internal server error'}, 500
        return render_template("index.html"), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return {'error': 'Bad request'}, 400
