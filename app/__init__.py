from flask import Flask, render_template

from config import Config

from app.extensions import db, login_manager

# Import models
from app.models import User, Review, GitHubReview, ATSReview

# Blueprints
from app.routes.auth import auth
from app.routes.review import review
from app.routes.github import github
from app.routes.ats import ats
from app.routes.pdf import pdf
from app.routes.profile import profile
from app.routes.search import search


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(review)
    app.register_blueprint(github)
    app.register_blueprint(ats)
    app.register_blueprint(pdf)
    app.register_blueprint(profile)
    app.register_blueprint(search)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return render_template("index.html")

    # ==========================
    # Custom Error Pages
    # ==========================

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    return app