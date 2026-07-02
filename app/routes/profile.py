from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.review import Review
from app.models.github_review import GitHubReview
from app.models.ats_review import ATSReview

profile = Blueprint("profile", __name__)


@profile.route("/profile")
@login_required
def user_profile():

    ai_reviews = Review.query.filter_by(
        user_id=current_user.id
    ).count()

    github_reviews = GitHubReview.query.filter_by(
        user_id=current_user.id
    ).count()

    ats_reviews = ATSReview.query.filter_by(
        user_id=current_user.id
    ).count()

    total_reviews = (
        ai_reviews +
        github_reviews +
        ats_reviews
    )

    return render_template(
        "profile.html",
        ai_reviews=ai_reviews,
        github_reviews=github_reviews,
        ats_reviews=ats_reviews,
        total_reviews=total_reviews
    )