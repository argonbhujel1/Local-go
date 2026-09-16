from datetime import datetime
from app import db


class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default="string")  # string, int, float, bool, json
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.String(50))
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User")


class PlatformFee(db.Model):
    __tablename__ = "platform_fees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    service_type = db.Column(db.String(30))
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey("vehicle_types.id"))
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"))
    fee_type = db.Column(db.String(20), default="FIXED")  # FIXED / PERCENT
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicle_type = db.relationship("VehicleType")
    route = db.relationship("Route")


class Commission(db.Model):
    __tablename__ = "commissions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    entity_type = db.Column(db.String(30))  # RESTAURANT / SHOP
    entity_id = db.Column(db.Integer)
    percent = db.Column(db.Float, default=10.0)
    fixed_fee = db.Column(db.Numeric(10, 2), default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"), nullable=False)
    plan_name = db.Column(db.String(50))
    amount = db.Column(db.Numeric(10, 2))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="ACTIVE")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    partner = db.relationship("Partner")


class GPSLocation(db.Model):
    """Temporary GPS trail – purged after retention period."""
    __tablename__ = "gps_locations"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(30), nullable=False, index=True)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)
    heading = db.Column(db.Float)
    speed = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    partner = db.relationship("Partner")