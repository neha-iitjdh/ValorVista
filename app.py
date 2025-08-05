"""
ValorVista - AI-Powered Real Estate Valuation Platform
Main Flask Application
"""

import os
import logging
from pathlib import Path

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

from config import get_config, STATIC_DIR, TEMPLATES_DIR
from src.api.routes import api_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """
    Application factory for creating Flask app.

    Args:
        config: Optional configuration object.

    Returns:
        Configured Flask application.
    """
    app = Flask(
        __name__,
        static_folder=str(STATIC_DIR),
        template_folder=str(TEMPLATES_DIR)
    )

    # Load configuration
    if config is None:
        config = get_config()

    app.config.from_object(config)

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Register blueprints
    app.register_blueprint(api_bp)

    # Register routes
    register_routes(app)

    logger.info(f"ValorVista application initialized (Debug: {app.debug})")

    return app


def register_routes(app):
    """Register main application routes."""

    @app.route("/")
    def index():
        """Render main application page."""
        return render_template("index.html")

    @app.route("/batch")
    def batch():
        """Render batch processing page."""
        return render_template("batch.html")

    @app.route("/insights")
    def insights():
        """Render market insights page."""
        return render_template("insights.html")

    @app.route("/about")
    def about():
        """Render about page."""
        return render_template("about.html")

    @app.route("/favicon.ico")
    def favicon():
        """Serve favicon."""
        return send_from_directory(
            app.static_folder, "images/favicon.ico",
            mimetype="image/vnd.microsoft.icon"
        )

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors."""
        logger.error(f"Server error: {error}")
        return render_template("500.html"), 500


# Create application instance
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"Starting ValorVista on {host}:{port}")
    app.run(host=host, port=port, debug=True)
