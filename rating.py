from datetime import datetime
from app import db


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(30), nullable=False, index=True)
    job_type = db.Column(db.String(30), nullable=False)  # RIDE, FOOD, PARCEL...
    rater_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ratee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)

    # Optional dimension scores
    behaviour = db.Column(db.Integer)
    safety = db.Column(db.Integer)
    cleanliness = db.Column(db.Integer)
    communication = db.Column(db.Integer)
    delivery_handling = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rater = db.relationship("User", foreign_keys=[rater_id], back_populates="ratings_given")
    ratee = db.relationship("User", foreign_keys=[ratee_id], back_populates="ratings_received")

    __table_args__ = (
        db.UniqueConstraint("job_id", "rater_id", "ratee_id", name="uq_rating_once"),
        db.CheckConstraint("score >= 1 AND score <= 5", name="ck_rating_score"),
    )