from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_login import login_required, current_user

from app.extensions import db
from app.models.review import Review
from app.services.ai_service import AIService

review = Blueprint("review", __name__)


@review.route("/review", methods=["GET", "POST"])
@login_required
def review_code():
    """
    Display the code review form and process submissions.
    """

    if request.method == "POST":

        language = request.form.get("language", "").strip().lower()
        source_code = request.form.get("source_code", "").strip()

        # -------------------------
        # Validation
        # -------------------------
        if not language:
            flash("Please select a programming language.", "warning")
            return redirect(url_for("review.review_code"))

        if not source_code:
            flash("Please paste your source code.", "warning")
            return redirect(url_for("review.review_code"))

        if len(source_code) < 10:
            flash("Source code is too short to review.", "warning")
            return redirect(url_for("review.review_code"))

        # -------------------------
        # AI Review
        # -------------------------
        try:
            ai_service = AIService()
            response = ai_service.review_code(
                code=source_code,
                language=language,
            )

        except Exception as e:
            flash(f"AI Service Error: {str(e)}", "danger")
            return redirect(url_for("review.review_code"))

        if not response.get("success"):

            flash(response.get("review"), "danger")

            return redirect(url_for("review.review_code"))

        review_text = response.get("review")

        # -------------------------
        # Save Review
        # -------------------------
        new_review = Review(
            user_id=current_user.id,
            language=language,
            source_code=source_code,
            review_result=review_text,
        )

        db.session.add(new_review)
        db.session.commit()

        # -------------------------
        # Show Result
        # -------------------------
        return render_template(
            "result.html",
            review=new_review,
        )

    return render_template("review.html")


@review.route("/history")
@login_required
def history():
    """
    Display review history of the logged-in user.
    """

    reviews = (
        Review.query.filter_by(user_id=current_user.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return render_template(
        "history.html",
        reviews=reviews,
    )


@review.route("/review/<int:review_id>")
@login_required
def view_review(review_id):
    """
    Display a previously generated review.
    """

    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id,
    ).first_or_404()

    return render_template(
        "result.html",
        review=review,
    )