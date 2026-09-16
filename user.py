from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    permissions = db.Column(db.JSON, default=list)

    users = db.relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    profile_photo = db.Column(db.String(255))
    address = db.Column(db.String(255))
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"))
    ward_id = db.Column(db.Integer, db.ForeignKey("wards.id"))
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    referral_code = db.Column(db.String(20), unique=True, index=True)
    referred_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = db.relationship("Role", secondary=user_roles, back_populates="users")
    municipality = db.relationship("Municipality", backref="users")
    ward = db.relationship("Ward", backref="users")
    referred_by = db.relationship("User", remote_side=[id], backref="referrals")
    partner = db.relationship("Partner", back_populates="user", uselist=False)
    wallet = db.relationship("Wallet", back_populates="user", uselist=False)
    saved_locations = db.relationship("SavedLocation", back_populates="user", lazy="dynamic")
    emergency_contacts = db.relationship("EmergencyContact", back_populates="user", lazy="dynamic")
    ratings_given = db.relationship("Rating", foreign_keys="Rating.rater_id", back_populates="rater", lazy="dynamic")
    ratings_received = db.relationship("Rating", foreign_keys="Rating.ratee_id", back_populates="ratee", lazy="dynamic")
    notifications = db.relationship("Notification", back_populates="user", lazy="dynamic")
    support_tickets = db.relationship("SupportTicket", back_populates="user", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name: str) -> bool:
        return any(r.name == role_name for r in self.roles)

    def has_any_role(self, *role_names) -> bool:
        return any(r.name in role_names for r in self.roles)

    @property
    def is_admin(self):
        return self.has_role("admin") or self.has_role("superadmin")

    @property
    def is_partner(self):
        return self.partner is not None and self.partner.status == "APPROVED"

    def generate_referral_code(self):
        import secrets
        import string
        alphabet = string.ascii_uppercase + string.digits
        self.referral_code = "".join(secrets.choice(alphabet) for _ in range(8))

    def __repr__(self):
        return f"<User {self.phone} {self.full_name}>"