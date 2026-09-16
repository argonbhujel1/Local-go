from datetime import datetime
from app import db


class PromoCode(db.Model):
    __tablename__ = "promo_codes"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    discount_type = db.Column(db.String(20), default="PERCENT")  # PERCENT / FIXED
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    max_discount = db.Column(db.Numeric(10, 2))
    min_order_amount = db.Column(db.Numeric(10, 2), default=0)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    usage_limit = db.Column(db.Integer)
    per_user_limit = db.Column(db.Integer, default=1)
    used_count = db.Column(db.Integer, default=0)
    service_types = db.Column(db.JSON, default=list)  # ["RIDE", "FOOD"] etc.
    vehicle_type_ids = db.Column(db.JSON, default=list)
    route_ids = db.Column(db.JSON, default=list)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Referral(db.Model):
    __tablename__ = "referrals"

    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reward_amount = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default="PENDING")  # PENDING, COMPLETED, PAID
    reward_transaction_id = db.Column(db.Integer, db.ForeignKey("wallet_transactions.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    referrer = db.relationship("User", foreign_keys=[referrer_id])
    referred = db.relationship("User", foreign_keys=[referred_id])