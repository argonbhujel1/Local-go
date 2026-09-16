from datetime import datetime
from app import db


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.String(30))
    category = db.Column(db.String(50))
    subject = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    screenshot = db.Column(db.String(255))
    priority = db.Column(db.String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    status = db.Column(db.String(20), default="OPEN", index=True)  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    assigned_admin_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    resolution = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    user = db.relationship("User", foreign_keys=[user_id], back_populates="support_tickets")
    assigned_admin = db.relationship("User", foreign_keys=[assigned_admin_id])


class EmergencyContact(db.Model):
    __tablename__ = "emergency_contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    relation = db.Column(db.String(50))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="emergency_contacts")