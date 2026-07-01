from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app.extensions import db
from app.models.user import User
from app.models.review import Review
from app.models.github_review import GitHubReview

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already exists!", "danger")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful! Please Login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            flash(
                f"Welcome back, {user.username}!",
                "success"
            )

            return redirect(url_for("auth.dashboard"))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")


@auth.route("/dashboard")
@login_required
def dashboard():

    # AI Reviews
    ai_reviews = (
        Review.query
        .filter_by(user_id=current_user.id)
        .all()
    )

    # GitHub Reviews
    github_reviews = (
        GitHubReview.query
        .filter_by(user_id=current_user.id)
        .all()
    )

    total_reviews = len(ai_reviews) + len(github_reviews)

    github_projects = len(github_reviews)

    average_score = "--"

    return render_template(
        "dashboard.html",
        total_reviews=total_reviews,
        ai_reviews=len(ai_reviews),
        github_projects=github_projects,
        average_score=average_score,
        recent_reviews=ai_reviews[:5]
    )


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("auth.login"))