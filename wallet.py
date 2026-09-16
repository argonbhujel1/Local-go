from datetime import datetime
from enum import Enum
from app import db


class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    PLATFORM_FEE = "PLATFORM_FEE"
    EARNING = "EARNING"
    REFUND = "REFUND"
    ADJUSTMENT = "ADJUSTMENT"
    WITHDRAWAL = "WITHDRAWAL"
    COMMISSION = "COMMISSION"


class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"), unique=True)
    balance = db.Column(db.Numeric(12, 2), default=0)
    currency = db.Column(db.String(3), default="NPR")
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="wallet")
    partner = db.relationship("Partner", back_populates="wallet")
    transactions = db.relationship("WalletTransaction", back_populates="wallet", lazy="dynamic")

    def can_accept_jobs(self, min_balance: float = 0) -> bool:
        if self.is_blocked:
            return False
        return float(self.balance) >= min_balance


class WalletTransaction(db.Model):
    __tablename__ = "wallet_transactions"

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)  # signed: + credit, - debit
    balance_after = db.Column(db.Numeric(12, 2))
    reference = db.Column(db.String(50))  # job_id etc.
    description = db.Column(db.String(255))
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    wallet = db.relationship("Wallet", back_populates="transactions")
    created_by = db.relationship("User")