from flask import Flask, render_template
from flask_cors import CORS
from flask_talisman import Talisman
from app.config import Config
from app.routes.api import api_bp
from app.utils.logger import logger

def create_app():
    """Application factory pattern for the Flask app."""
    app = Flask(__name__,
                template_folder=Config.TEMPLATE_DIR,
                static_folder=Config.STATIC_DIR)
                
    app.config.from_object(Config)

    # Apply security headers using Flask-Talisman
    # CSP is currently relaxed to allow inline styles/scripts for quick UI prototyping
    csp = {
        'default-src': [
            '\'self\'',
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            'https://cdn.jsdelivr.net'
        ],
        'script-src': ['\'self\'', '\'unsafe-inline\'', 'https://cdn.jsdelivr.net'],
        'style-src': ['\'self\'', '\'unsafe-inline\'', 'https://fonts.googleapis.com'],
    }
    Talisman(app, content_security_policy=csp, force_https=not app.config['DEBUG'])

    # Enable CORS (can be restricted to specific domains in prod)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    @app.route('/')
    def index():
        """Serve the main frontend UI."""
        logger.info("Serving index page.")
        return render_template('index.html')

    # Global error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {"success": False, "error": "Not Found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {"success": False, "error": "Internal Server Error"}, 500

    logger.info("Flask application initialized successfully.")
    return app
