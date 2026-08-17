from flask import Flask
from pathlib import Path
import os
from .routes import bp

BASE_DIR = Path(__file__).resolve().parent.parent

def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates")
    )
    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY",
        "dev-only-change-this-secret-key"
    )
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    app.register_blueprint(bp)
    (BASE_DIR / "data").mkdir(exist_ok=True)
    (BASE_DIR / "assets").mkdir(exist_ok=True)
    return app
