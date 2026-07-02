from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.models.review import Review
from app.models.github_review import GitHubReview
from app.models.ats_review import ATSReview

search = Blueprint("search", __name__)


@search.route("/search")
@login_required
def search_page():

    query = request.args.get("q", "").strip()

    ai_reviews = []
    github_reviews = []
    ats_reviews = []

    if query:

        ai_reviews = (
            Review.query.filter(
                Review.user_id == current_user.id,
                or_(
                    Review.language.ilike(f"%{query}%"),
                    Review.review_result.ilike(f"%{query}%")
                )
            )
            .order_by(Review.created_at.desc())
            .all()
        )

        github_reviews = (
            GitHubReview.query.filter(
                GitHubReview.user_id == current_user.id,
                or_(
                    GitHubReview.repository_name.ilike(f"%{query}%"),
                    GitHubReview.repository_url.ilike(f"%{query}%"),
                    GitHubReview.review.ilike(f"%{query}%")
                )
            )
            .order_by(GitHubReview.created_at.desc())
            .all()
        )

        ats_reviews = (
            ATSReview.query.filter(
                ATSReview.user_id == current_user.id,
                or_(
                    ATSReview.filename.ilike(f"%{query}%"),
                    ATSReview.review.ilike(f"%{query}%")
                )
            )
            .order_by(ATSReview.created_at.desc())
            .all()
        )

    return render_template(
        "search.html",
        query=query,
        ai_reviews=ai_reviews,
        github_reviews=github_reviews,
        ats_reviews=ats_reviews
    )