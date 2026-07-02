import os

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for
)

from flask_login import login_required, current_user
from pypdf import PdfReader

from app.extensions import db
from app.models.ats_review import ATSReview
from app.services.ats_service import ATSService

ats = Blueprint("ats", __name__)


# =====================================
# Upload & Analyze Resume
# =====================================

@ats.route("/resume", methods=["GET", "POST"])
@login_required
def resume():

    if request.method == "POST":

        if "resume" not in request.files:
            flash("Please select a resume.", "danger")
            return render_template("resume.html")

        file = request.files["resume"]

        if file.filename == "":
            flash("Please select a resume.", "danger")
            return render_template("resume.html")

        if not file.filename.lower().endswith(".pdf"):
            flash("Only PDF resumes are supported.", "danger")
            return render_template("resume.html")

        os.makedirs("uploads", exist_ok=True)

        filepath = os.path.join("uploads", file.filename)

        file.save(filepath)

        reader = PdfReader(filepath)

        resume_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:
                resume_text += text + "\n"

        service = ATSService()

        result = service.analyze_resume(resume_text)

        ats_review = ATSReview(
            user_id=current_user.id,
            filename=file.filename,
            ats_score=result["score"],
            review=result["review"]
        )

        db.session.add(ats_review)
        db.session.commit()

        return render_template(
            "ats_result.html",
            review_id=ats_review.id,
            filename=file.filename,
            score=result["score"],
            review=result["review"]
        )

    return render_template("resume.html")


# =====================================
# ATS History
# =====================================

@ats.route("/resume/history")
@login_required
def history():

    reviews = (
        ATSReview.query
        .filter_by(user_id=current_user.id)
        .order_by(ATSReview.created_at.desc())
        .all()
    )

    return render_template(
        "ats_history.html",
        reviews=reviews
    )


# =====================================
# View Previous Report
# =====================================

@ats.route("/resume/view/<int:review_id>")
@login_required
def view(review_id):

    review = ATSReview.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "ats_result.html",
        review_id=review.id,
        filename=review.filename,
        score=review.ats_score,
        review=review.review
    )


# =====================================
# Delete Report
# =====================================

@ats.route("/resume/delete/<int:review_id>")
@login_required
def delete(review_id):

    review = ATSReview.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(review)
    db.session.commit()

    flash("ATS report deleted successfully.", "success")

    return redirect(url_for("ats.history"))