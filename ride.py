from datetime import datetime
from enum import Enum
from app import db


class RideStatus(str, Enum):
    REQUESTED = "REQUESTED"
    SEARCHING = "SEARCHING"
    ACCEPTED = "ACCEPTED"
    ARRIVING = "ARRIVING"
    ARRIVED = "ARRIVED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class RideType(str, Enum):
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"
    SCHEDULED = "SCHEDULED"
    INSTANT = "INSTANT"


class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"))
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"))
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey("vehicle_types.id"), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"))
    ride_type = db.Column(db.String(20), default=RideType.INSTANT.value)
    status = db.Column(db.String(20), default=RideStatus.REQUESTED.value, index=True)

    # Locations
    pickup_address = db.Column(db.String(255))
    pickup_lat = db.Column(db.Float, nullable=False)
    pickup_lng = db.Column(db.Float, nullable=False)
    pickup_municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"))
    destination_address = db.Column(db.String(255))
    destination_lat = db.Column(db.Float, nullable=False)
    destination_lng = db.Column(db.Float, nullable=False)
    destination_municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"))

    # Scheduling
    scheduled_at = db.Column(db.DateTime)

    # Fare (server-calculated)
    distance_km = db.Column(db.Float)
    duration_minutes = db.Column(db.Float)
    base_fare = db.Column(db.Numeric(10, 2), default=0)
    distance_fare = db.Column(db.Numeric(10, 2), default=0)
    time_fare = db.Column(db.Numeric(10, 2), default=0)
    waiting_fare = db.Column(db.Numeric(10, 2), default=0)
    peak_fare = db.Column(db.Numeric(10, 2), default=0)
    discount = db.Column(db.Numeric(10, 2), default=0)
    platform_fee = db.Column(db.Numeric(10, 2), default=0)
    total_fare = db.Column(db.Numeric(10, 2), default=0)
    promo_code_id = db.Column(db.Integer, db.ForeignKey("promo_codes.id"))

    # Payment
    payment_status = db.Column(db.String(20), default="PENDING")
    payment_method = db.Column(db.String(30))

    # Timestamps
    accepted_at = db.Column(db.DateTime)
    arrived_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancelled_by = db.Column(db.String(20))  # customer / partner / system
    cancellation_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = db.relationship("User", foreign_keys=[customer_id])
    partner = db.relationship("Partner")
    vehicle = db.relationship("Vehicle")
    vehicle_type = db.relationship("VehicleType")
    route = db.relationship("Route")
    pickup_municipality = db.relationship("Municipality", foreign_keys=[pickup_municipality_id])
    destination_municipality = db.relationship("Municipality", foreign_keys=[destination_municipality_id])
    participants = db.relationship("RideParticipant", back_populates="ride", lazy="dynamic")
    promo_code = db.relationship("PromoCode")

    def __repr__(self):
        return f"<Ride {self.job_id} {self.status}>"


class RideParticipant(db.Model):
    """For shared rides."""
    __tablename__ = "ride_participants"

    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seats = db.Column(db.Integer, default=1)
    fare_share = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), default="JOINED")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ride = db.relationship("Ride", back_populates="participants")
    user = db.relationship("User")