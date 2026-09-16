from datetime import datetime
from enum import Enum
from app import db


class PartnerStatus(str, Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class Partner(db.Model):
    __tablename__ = "partners"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    status = db.Column(db.String(20), default=PartnerStatus.PENDING.value, index=True)
    is_online = db.Column(db.Boolean, default=False, index=True)
    last_location_lat = db.Column(db.Float)
    last_location_lng = db.Column(db.Float)
    last_location_at = db.Column(db.DateTime)
    citizenship_number = db.Column(db.String(50))
    citizenship_photo = db.Column(db.String(255))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    total_jobs = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Numeric(12, 2), default=0)
    average_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    rejection_reason = db.Column(db.Text)
    approved_at = db.Column(db.DateTime)
    approved_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", foreign_keys=[user_id], back_populates="partner")
    approved_by = db.relationship("User", foreign_keys=[approved_by_id])
    vehicles = db.relationship("Vehicle", back_populates="partner", lazy="dynamic")
    services = db.relationship("PartnerService", back_populates="partner", lazy="dynamic")
    wallet = db.relationship("Wallet", back_populates="partner", uselist=False)

    def can_go_online(self) -> bool:
        if self.status != PartnerStatus.APPROVED.value:
            return False
        if self.wallet and self.wallet.balance < 0:
            from flask import current_app
            min_bal = current_app.config.get("MIN_WALLET_BALANCE", 0)
            if float(self.wallet.balance) < min_bal:
                return False
        return True

    def __repr__(self):
        return f"<Partner {self.id} status={self.status}>"


class PartnerService(db.Model):
    """Services a partner has opted into (Ride, Food, Parcel, Document, Shop)."""
    __tablename__ = "partner_services"

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"), nullable=False)
    service_type = db.Column(db.String(30), nullable=False)  # RIDE, FOOD, PARCEL, DOCUMENT, SHOP_DELIVERY
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey("vehicle_types.id"))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    partner = db.relationship("Partner", back_populates="services")
    vehicle_type = db.relationship("VehicleType")

    __table_args__ = (
        db.UniqueConstraint("partner_id", "service_type", "vehicle_type_id", name="uq_partner_service"),
    )