from flask import Flask, jsonify
from flasgger import Swagger
from app.config import Config
from app.extensions import db, migrate, jwt, bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Swagger UI config
    swagger_config = {
        "headers": [],
        "specs": [{"endpoint": "apispec", "route": "/apispec.json", "rule_filter": lambda rule: True}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
    }
    swagger_template = {
        "info": {
            "title": "JobTrackr API",
            "description": "AI-powered job application tracker. Register → Login → Track jobs → Get AI tips.",
            "version": "1.0.0",
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter: Bearer <your_token>",
            }
        },
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.jobs import jobs_bp
    from app.routes.ai import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(ai_bp)

    # Root route
    @app.route("/")
    def index():
        return jsonify({
            "message": "JobTrackr API is running",
            "docs": "/docs",
            "health": "/health",
        }), 200

    # Health check
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "message": "JobTrackr API is running"}), 200

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized(reason):
        return jsonify({"error": "Missing or invalid token. Login first."}), 401

    @jwt.expired_token_loader
    def expired(jwt_header, jwt_payload):
        return jsonify({"error": "Token expired. Please login again."}), 401

    # Create tables on first run
    with app.app_context():
        db.create_all()

    return app
