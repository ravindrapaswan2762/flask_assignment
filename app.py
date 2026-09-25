"""
Flask application factory.
"""

from flask import Flask, jsonify
from config.settings import get_config
from config.database import init_db
from routes.user_routes import users_bp
from routes.auth_routes import auth_bp


def create_app(config_class=None):
    """
    Application factory.

    Args:
        config_class: Optional config object. Defaults to environment-based config.
    """
    app = Flask(__name__)

    # Load configuration
    cfg = config_class or get_config()
    app.config.from_object(cfg)

    # Initialize database (create DB + table if needed)
    with app.app_context():
        try:
            init_db()
        except Exception as exc:
            print(f"[WARNING] Could not initialize DB: {exc}")
            print("[WARNING] Make sure MySQL is running and credentials are correct.")

    # Register blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)

    # ------------------------------------------------------------------ #
    #  Global error handlers                                              #
    # ------------------------------------------------------------------ #

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"success": False, "error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"success": False, "error": "Internal server error."}), 500

    # Health-check endpoint
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"success": True, "message": "API is running."}), 200

    return app
