from flask import Blueprint

from flask_login import login_required, current_user

from app.models.review import Review
from app.models.github_review import GitHubReview
from app.models.ats_review import ATSReview

from app.services.pdf_service import PDFService

pdf = Blueprint("pdf", __name__)


# -------------------------
# AI Review PDF
# -------------------------

@pdf.route("/pdf/review/<int:review_id>")
@login_required
def review_pdf(review_id):

    review = Review.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    return PDFService.generate_report(
        title="AI Code Review Report",
        filename=f"AI_Review_{review.id}.pdf",
        content=review.review_result
    )


# -------------------------
# GitHub Review PDF
# -------------------------

@pdf.route("/pdf/github/<int:review_id>")
@login_required
def github_pdf(review_id):

    review = GitHubReview.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    return PDFService.generate_report(
        title="GitHub Repository Analysis",
        filename=f"GitHub_Report_{review.id}.pdf",
        content=review.review
    )


# -------------------------
# ATS PDF
# -------------------------

@pdf.route("/pdf/ats/<int:review_id>")
@login_required
def ats_pdf(review_id):

    review = ATSReview.query.filter_by(
        id=review_id,
        user_id=current_user.id
    ).first_or_404()

    return PDFService.generate_report(
        title="Resume ATS Report",
        filename=f"ATS_Report_{review.id}.pdf",
        content=review.review
    )