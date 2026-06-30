from flask import Flask

from config import Config

from app.extensions import db, login_manager

# Import models so SQLAlchemy creates all tables
from app.models import User, Review

# Blueprints
from app.routes.auth import auth
from app.routes.review import review


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(review)

    # Create Database Tables
    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return "<h1>🚀 Welcome to CodeReview Assist Pro AI</h1>"

    return app