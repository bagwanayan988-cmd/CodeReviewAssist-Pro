from app.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    language = db.Column(
        db.String(50),
        nullable=False
    )

    source_code = db.Column(
        db.Text,
        nullable=False
    )

    review_result = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "reviews",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        return f"<Review {self.id} - User {self.user_id}>"