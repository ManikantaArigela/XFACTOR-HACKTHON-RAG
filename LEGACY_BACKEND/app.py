from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config import Config
from routes.chat import chat_bp
from routes.content import content_bp
from routes.search import search_bp
from routes.upload import upload_bp
from routes.user import user_bp
from services.database import db, init_database
from utils.responses import failure, success


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, origins=app.config["CORS_ORIGINS"])
    init_database(app)

    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(content_bp, url_prefix="/api")
    app.register_blueprint(search_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return success({"database": "ok"}, "Service is healthy")
        except SQLAlchemyError:
            return failure("Database is unavailable", 503)

    @app.errorhandler(400)
    def bad_request(error):
        return failure(str(error.description), 400)

    @app.errorhandler(404)
    def not_found(_error):
        return failure("Resource not found", 404)

    @app.errorhandler(413)
    def too_large(_error):
        return failure("Uploaded file is too large", 413)

    @app.errorhandler(Exception)
    def internal_error(_error):
        db.session.rollback()
        return failure("Internal server error", 500)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("FLASK_ENV") == "development")
