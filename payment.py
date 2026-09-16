from datetime import datetime
from enum import Enum
from app import db


class PaymentMethod(str, Enum):
    CASH = "CASH"
    ESEWA_QR = "ESEWA_QR"
    KHALTI_QR = "KHALTI_QR"
    BANK_QR = "BANK_QR"
    OTHER_QR = "OTHER_QR"
    WALLET = "WALLET"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    CUSTOMER_CONFIRMED = "CUSTOMER_CONFIRMED"
    PARTNER_CONFIRMED = "PARTNER_CONFIRMED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(30), index=True)  # ride/delivery job_id
    job_type = db.Column(db.String(30))  # RIDE, FOOD, PARCEL, etc.
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    platform_fee = db.Column(db.Numeric(10, 2), default=0)
    method = db.Column(db.String(30), default=PaymentMethod.CASH.value)
    status = db.Column(db.String(30), default=PaymentStatus.PENDING.value, index=True)

    qr_reference = db.Column(db.String(100))  # customer entered ref or screenshot note
    customer_confirmed = db.Column(db.Boolean, default=False)
    customer_confirmed_at = db.Column(db.DateTime)
    partner_confirmed = db.Column(db.Boolean, default=False)
    partner_confirmed_at = db.Column(db.DateTime)
    admin_verified = db.Column(db.Boolean, default=False)
    admin_verified_at = db.Column(db.DateTime)
    admin_verified_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship("User", foreign_keys=[customer_id])
    partner = db.relationship("Partner")
    admin_verified_by = db.relationship("User", foreign_keys=[admin_verified_by_id])