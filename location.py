from datetime import datetime
from app import db


class Municipality(db.Model):
    __tablename__ = "municipalities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    name_np = db.Column(db.String(100))  # Nepali name
    type = db.Column(db.String(30), default="Municipality")  # Municipality / Rural Municipality
    district = db.Column(db.String(50), nullable=False, index=True)  # Morang / Jhapa
    province = db.Column(db.String(50), default="Koshi")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    geojson = db.Column(db.JSON)  # optional polygon
    is_serviceable = db.Column(db.Boolean, default=True, index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wards = db.relationship("Ward", back_populates="municipality", lazy="dynamic")
    areas = db.relationship("Area", back_populates="municipality", lazy="dynamic")

    def __repr__(self):
        return f"<Municipality {self.name}>"


class Ward(db.Model):
    __tablename__ = "wards"

    id = db.Column(db.Integer, primary_key=True)
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"), nullable=False)
    number = db.Column(db.Integer)
    name = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_serviceable = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    municipality = db.relationship("Municipality", back_populates="wards")
    areas = db.relationship("Area", back_populates="ward", lazy="dynamic")

    def __repr__(self):
        return f"<Ward {self.number} {self.name}>"


class Area(db.Model):
    """Tole / Village / Local area."""
    __tablename__ = "areas"

    id = db.Column(db.Integer, primary_key=True)
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"), nullable=False)
    ward_id = db.Column(db.Integer, db.ForeignKey("wards.id"))
    name = db.Column(db.String(100), nullable=False, index=True)
    type = db.Column(db.String(30), default="Tole")  # Tole, Village, Chowk, etc.
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_serviceable = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    municipality = db.relationship("Municipality", back_populates="areas")
    ward = db.relationship("Ward", back_populates="areas")

    def __repr__(self):
        return f"<Area {self.name}>"


class SavedLocation(db.Model):
    __tablename__ = "saved_locations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    label = db.Column(db.String(50), nullable=False)  # Home, Work, etc.
    address = db.Column(db.String(255))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"))
    ward_id = db.Column(db.Integer, db.ForeignKey("wards.id"))
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="saved_locations")
    municipality = db.relationship("Municipality")
    ward = db.relationship("Ward")
    area = db.relationship("Area")