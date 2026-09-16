from datetime import datetime
from app import db


class VehicleType(db.Model):
    """Configurable vehicle types with document requirements."""
    __tablename__ = "vehicle_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # Bike, Car, Auto, Safari, E-Rickshaw, Bicycle
    code = db.Column(db.String(20), unique=True, nullable=False)  # bike, car, auto, safari, erickshaw, bicycle
    icon = db.Column(db.String(50))
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

    # Configurable requirements (admin controlled)
    requires_number_plate = db.Column(db.Boolean, default=True)
    requires_registration = db.Column(db.Boolean, default=True)
    requires_license = db.Column(db.Boolean, default=True)
    requires_insurance = db.Column(db.Boolean, default=False)
    requires_photo = db.Column(db.Boolean, default=True)
    requires_admin_approval = db.Column(db.Boolean, default=True)

    # Fare defaults (can be overridden by route/fare rules)
    base_fare = db.Column(db.Numeric(10, 2), default=0)
    per_km_fare = db.Column(db.Numeric(10, 2), default=0)
    per_minute_fare = db.Column(db.Numeric(10, 2), default=0)
    minimum_fare = db.Column(db.Numeric(10, 2), default=0)
    platform_fee = db.Column(db.Numeric(10, 2), default=10)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicles = db.relationship("Vehicle", back_populates="vehicle_type", lazy="dynamic")

    def __repr__(self):
        return f"<VehicleType {self.code}>"


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"), nullable=False)
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey("vehicle_types.id"), nullable=False)

    # Conditional fields – only required based on VehicleType config
    number_plate = db.Column(db.String(30))
    registration_number = db.Column(db.String(50))
    license_number = db.Column(db.String(50))
    insurance_number = db.Column(db.String(50))
    vehicle_photo = db.Column(db.String(255))
    registration_photo = db.Column(db.String(255))
    license_photo = db.Column(db.String(255))
    insurance_photo = db.Column(db.String(255))
    color = db.Column(db.String(30))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)

    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    verification_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    partner = db.relationship("Partner", back_populates="vehicles")
    vehicle_type = db.relationship("VehicleType", back_populates="vehicles")

    def validate_requirements(self) -> list:
        """Return list of missing required fields based on vehicle type config."""
        missing = []
        vt = self.vehicle_type
        if not vt:
            return ["vehicle_type"]
        if vt.requires_number_plate and not self.number_plate:
            missing.append("number_plate")
        if vt.requires_registration and not self.registration_number:
            missing.append("registration_number")
        if vt.requires_license and not self.license_number:
            missing.append("license_number")
        if vt.requires_insurance and not self.insurance_number:
            missing.append("insurance_number")
        if vt.requires_photo and not self.vehicle_photo:
            missing.append("vehicle_photo")
        return missing

    def __repr__(self):
        return f"<Vehicle {self.id} {self.vehicle_type.code if self.vehicle_type else '?'}>"