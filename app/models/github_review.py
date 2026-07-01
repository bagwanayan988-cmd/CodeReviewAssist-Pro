from app.extensions import db


class GitHubReview(db.Model):
    __tablename__ = "github_reviews"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    repository_url = db.Column(
        db.String(500),
        nullable=False
    )

    repository_name = db.Column(
        db.String(200),
        nullable=False
    )

    review = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):
        return f"<GitHubReview {self.repository_name}>"