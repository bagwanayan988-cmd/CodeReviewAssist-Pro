from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models.github_review import GitHubReview
from app.services.github_service import GitHubService

github = Blueprint("github", __name__)


# ==========================================
# Analyze GitHub Repository
# ==========================================

@github.route("/github", methods=["GET", "POST"])
@login_required
def analyze_github():

    if request.method == "POST":

        repo_url = request.form.get("repo_url", "").strip()

        if not repo_url:
            flash("Please enter a GitHub Repository URL.", "danger")
            return render_template("github.html")

        try:

            result = GitHubService.analyze_repository(repo_url)

            if not result["success"]:
                flash(result["review"], "danger")
                return render_template("github.html")

            repository_name = repo_url.rstrip("/").split("/")[-1]

            github_review = GitHubReview(
                user_id=current_user.id,
                repository_url=repo_url,
                repository_name=repository_name,
                review=result["review"]
            )

            db.session.add(github_review)
            db.session.commit()

            return render_template(
                "github_result.html",
                review_id=github_review.id,
                repo_url=repo_url,
                review=result["review"]
            )

        except Exception as e:

            db.session.rollback()
            flash(str(e), "danger")

    return render_template("github.html")


# ==========================================
# GitHub History
# ==========================================

@github.route("/github/history")
@login_required
def history():

    reviews = (
        GitHubReview.query
        .filter_by(user_id=current_user.id)
        .order_by(GitHubReview.created_at.desc())
        .all()
    )

    return render_template(
        "github_history.html",
        reviews=reviews
    )


# ==========================================
# View Previous Analysis
# ==========================================

@github.route("/github/view/<int:review_id>")
@login_required
def view(review_id):

    review = GitHubReview.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "github_result.html",
        review_id=review.id,
        repo_url=review.repository_url,
        review=review.review
    )


# ==========================================
# Delete Analysis
# ==========================================

@github.route("/github/delete/<int:review_id>")
@login_required
def delete(review_id):

    review = GitHubReview.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(review)
    db.session.commit()

    flash("Repository analysis deleted successfully.", "success")

    return redirect(url_for("github.history"))