from datetime import datetime
from app import db


class Route(db.Model):
    __tablename__ = "routes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    start_municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"), nullable=False)
    end_municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"), nullable=False)
    distance_km = db.Column(db.Float)
    estimated_minutes = db.Column(db.Integer)
    is_local = db.Column(db.Boolean, default=False)  # same municipality
    is_active = db.Column(db.Boolean, default=True, index=True)
    vehicle_types = db.Column(db.JSON, default=list)  # list of vehicle_type codes allowed
    base_fare = db.Column(db.Numeric(10, 2), default=0)
    per_km_fare = db.Column(db.Numeric(10, 2), default=0)
    per_minute_fare = db.Column(db.Numeric(10, 2), default=0)
    minimum_fare = db.Column(db.Numeric(10, 2), default=0)
    platform_fee = db.Column(db.Numeric(10, 2), default=10)
    delivery_fee = db.Column(db.Numeric(10, 2), default=0)
    peak_multiplier = db.Column(db.Float, default=1.0)
    waiting_fee_per_min = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    start_municipality = db.relationship("Municipality", foreign_keys=[start_municipality_id])
    end_municipality = db.relationship("Municipality", foreign_keys=[end_municipality_id])
    fare_rules = db.relationship("FareRule", back_populates="route", lazy="dynamic")

    def __repr__(self):
        return f"<Route {self.name}>"


class FareRule(db.Model):
    """Fine-grained fare rules per vehicle type / service / time."""
    __tablename__ = "fare_rules"

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"))
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey("vehicle_types.id"))
    service_type = db.Column(db.String(30))  # RIDE, FOOD, PARCEL, DOCUMENT, SHOP_DELIVERY
    name = db.Column(db.String(100))
    base_fare = db.Column(db.Numeric(10, 2), default=0)
    per_km_fare = db.Column(db.Numeric(10, 2), default=0)
    per_minute_fare = db.Column(db.Numeric(10, 2), default=0)
    minimum_fare = db.Column(db.Numeric(10, 2), default=0)
    platform_fee = db.Column(db.Numeric(10, 2), default=10)
    delivery_fee = db.Column(db.Numeric(10, 2), default=0)
    peak_start = db.Column(db.Time)
    peak_end = db.Column(db.Time)
    peak_multiplier = db.Column(db.Float, default=1.0)
    waiting_fee_per_min = db.Column(db.Numeric(10, 2), default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    route = db.relationship("Route", back_populates="fare_rules")
    vehicle_type = db.relationship("VehicleType")