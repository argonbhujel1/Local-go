from datetime import datetime
from app import db


class Advertisement(db.Model):
    __tablename__ = "advertisements"

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(120), nullable=False)
    logo = db.Column(db.String(255))
    banner = db.Column(db.String(255))
    description = db.Column(db.Text)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(120))
    website = db.Column(db.String(255))
    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    placement = db.Column(db.String(50))  # homepage, passenger, driver, food, etc.
    status = db.Column(db.String(20), default="PENDING")  # PENDING, ACTIVE, EXPIRED, REJECTED
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    municipality = db.relationship("Municipality")