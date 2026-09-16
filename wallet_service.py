"""Partner wallet operations – all mutations server-side."""
from decimal import Decimal
from typing import Optional

from app import db
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from flask import current_app


class WalletService:
    @staticmethod
    def get_or_create_partner_wallet(partner_id: int) -> Wallet:
        wallet = Wallet.query.filter_by(partner_id=partner_id).first()
        if not wallet:
            wallet = Wallet(partner_id=partner_id, balance=Decimal("0"))
            db.session.add(wallet)
            db.session.commit()
        return wallet

    @staticmethod
    def get_or_create_user_wallet(user_id: int) -> Wallet:
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=Decimal("0"))
            db.session.add(wallet)
            db.session.commit()
        return wallet

    @staticmethod
    def deduct_platform_fee(partner_id: int, amount: float, job_id: str, description: str = None) -> bool:
        wallet = WalletService.get_or_create_partner_wallet(partner_id)
        amt = Decimal(str(amount))
        if amt <= 0:
            return True

        new_balance = Decimal(str(wallet.balance)) - amt
        max_neg = Decimal(str(current_app.config.get("MAX_NEGATIVE_WALLET", -100)))
        if new_balance < max_neg:
            return False

        wallet.balance = new_balance
        tx = WalletTransaction(
            wallet_id=wallet.id,
            type=TransactionType.PLATFORM_FEE.value,
            amount=-amt,
            balance_after=new_balance,
            reference=job_id,
            description=description or f"Platform fee for {job_id}",
        )
        db.session.add(tx)
        db.session.commit()
        return True

    @staticmethod
    def credit(partner_id: int, amount: float, tx_type: str, job_id: str = None, description: str = None) -> WalletTransaction:
        wallet = WalletService.get_or_create_partner_wallet(partner_id)
        amt = Decimal(str(amount))
        wallet.balance = Decimal(str(wallet.balance)) + amt
        tx = WalletTransaction(
            wallet_id=wallet.id,
            type=tx_type,
            amount=amt,
            balance_after=wallet.balance,
            reference=job_id,
            description=description,
        )
        db.session.add(tx)
        db.session.commit()
        return tx

    @staticmethod
    def can_accept_jobs(partner_id: int) -> bool:
        wallet = WalletService.get_or_create_partner_wallet(partner_id)
        min_bal = float(current_app.config.get("MIN_WALLET_BALANCE", 0))
        return wallet.can_accept_jobs(min_bal)