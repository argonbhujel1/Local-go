from datetime import datetime
from enum import Enum
from app import db


class ServiceType(str, Enum):
    RIDE = "RIDE"
    FOOD = "FOOD"
    PARCEL = "PARCEL"
    DOCUMENT = "DOCUMENT"
    SHOP_DELIVERY = "SHOP_DELIVERY"


class DeliveryStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class Delivery(db.Model):
    """Unified delivery job for Parcel / Document / Shop / Food (last-mile)."""
    __tablename__ = "deliveries"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    service_type = db.Column(db.String(30), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"))
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"))
    status = db.Column(db.String(30), default=DeliveryStatus.PENDING.value, index=True)

    # Pickup
    pickup_address = db.Column(db.String(255))
    pickup_lat = db.Column(db.Float)
    pickup_lng = db.Column(db.Float)
    pickup_contact_name = db.Column(db.String(100))
    pickup_contact_phone = db.Column(db.String(20))
    pickup_municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"))

    # Destination
    destination_address = db.Column(db.String(255))
    destination_lat = db.Column(db.Float)
    destination_lng = db.Column(db.Float)
    destination_contact_name = db.Column(db.String(100))
    destination_contact_phone = db.Column(db.String(20))
    destination_municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"))

    # Fare
    distance_km = db.Column(db.Float)
    delivery_fee = db.Column(db.Numeric(10, 2), default=0)
    platform_fee = db.Column(db.Numeric(10, 2), default=0)
    total_fare = db.Column(db.Numeric(10, 2), default=0)
    payment_status = db.Column(db.String(20), default="PENDING")
    payment_method = db.Column(db.String(30))

    special_instructions = db.Column(db.Text)
    otp_code = db.Column(db.String(10))  # optional receiver OTP
    delivery_photo = db.Column(db.String(255))
    signature = db.Column(db.String(255))

    # Related entities (polymorphic-ish)
    food_order_id = db.Column(db.Integer, db.ForeignKey("food_orders.id"))
    parcel_id = db.Column(db.Integer, db.ForeignKey("parcels.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("document_deliveries.id"))
    shop_order_id = db.Column(db.Integer, db.ForeignKey("shop_orders.id"))

    accepted_at = db.Column(db.DateTime)
    picked_up_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship("User", foreign_keys=[customer_id])
    partner = db.relationship("Partner")
    vehicle = db.relationship("Vehicle")
    food_order = db.relationship("FoodOrder", back_populates="delivery")
    parcel = db.relationship("Parcel", back_populates="delivery")
    document = db.relationship("DocumentDelivery", back_populates="delivery")
    shop_order = db.relationship("ShopOrder", back_populates="delivery")

    def __repr__(self):
        return f"<Delivery {self.job_id} {self.service_type}>"