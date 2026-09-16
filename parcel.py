from datetime import datetime
from enum import Enum
from app import db


class ParcelType(str, Enum):
    SMALL_PACKAGE = "SMALL_PACKAGE"
    DOCUMENTS = "DOCUMENTS"
    CLOTHING = "CLOTHING"
    ELECTRONICS = "ELECTRONICS"
    GROCERY = "GROCERY"
    GIFTS = "GIFTS"
    LOCAL_PRODUCTS = "LOCAL_PRODUCTS"
    OTHER = "OTHER"


class Parcel(db.Model):
    __tablename__ = "parcels"

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parcel_type = db.Column(db.String(30), default=ParcelType.OTHER.value)
    description = db.Column(db.Text)
    approximate_weight_kg = db.Column(db.Float)
    quantity = db.Column(db.Integer, default=1)
    special_instructions = db.Column(db.Text)
    qr_code = db.Column(db.String(255))  # path to generated QR image

    # Receiver
    receiver_name = db.Column(db.String(100), nullable=False)
    receiver_phone = db.Column(db.String(20), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("User")
    delivery = db.relationship("Delivery", back_populates="parcel", uselist=False)


class DocumentDelivery(db.Model):
    __tablename__ = "document_deliveries"

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    document_type = db.Column(db.String(80))  # Certificates, Forms, Legal, etc.
    description = db.Column(db.Text)
    is_sensitive = db.Column(db.Boolean, default=True)
    special_instructions = db.Column(db.Text)
    require_otp = db.Column(db.Boolean, default=True)
    require_signature = db.Column(db.Boolean, default=True)
    require_photo = db.Column(db.Boolean, default=False)

    sender_name = db.Column(db.String(100))
    sender_phone = db.Column(db.String(20))
    receiver_name = db.Column(db.String(100), nullable=False)
    receiver_phone = db.Column(db.String(20), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("User")
    delivery = db.relationship("Delivery", back_populates="document", uselist=False)