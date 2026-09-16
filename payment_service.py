"""Payment abstraction – direct QR confirmation for now; gateways later."""
from datetime import datetime
from decimal import Decimal

from app import db
from app.models.payment import Payment, PaymentStatus, PaymentMethod


class PaymentService:
    @staticmethod
    def create_payment(
        *,
        job_id: str,
        job_type: str,
        customer_id: int,
        partner_id: int = None,
        amount: float,
        platform_fee: float = 0,
        method: str = PaymentMethod.CASH.value,
    ) -> Payment:
        p = Payment(
            job_id=job_id,
            job_type=job_type,
            customer_id=customer_id,
            partner_id=partner_id,
            amount=Decimal(str(amount)),
            platform_fee=Decimal(str(platform_fee)),
            method=method,
            status=PaymentStatus.PENDING.value,
        )
        db.session.add(p)
        db.session.commit()
        return p

    @staticmethod
    def customer_confirm(payment_id: int, user_id: int, qr_reference: str = None) -> Payment:
        p = db.session.get(Payment, payment_id)
        if not p or p.customer_id != user_id:
            raise ValueError("Payment not found")
        p.customer_confirmed = True
        p.customer_confirmed_at = datetime.utcnow()
        p.qr_reference = qr_reference
        p.status = PaymentStatus.CUSTOMER_CONFIRMED.value
        db.session.commit()
        return p

    @staticmethod
    def partner_confirm(payment_id: int, partner_id: int) -> Payment:
        p = db.session.get(Payment, payment_id)
        if not p or p.partner_id != partner_id:
            raise ValueError("Payment not found")
        p.partner_confirmed = True
        p.partner_confirmed_at = datetime.utcnow()
        if p.customer_confirmed:
            p.status = PaymentStatus.COMPLETED.value
        else:
            p.status = PaymentStatus.PARTNER_CONFIRMED.value
        db.session.commit()
        return p

    # Future: integrate official eSewa / Khalti / bank gateways here
    @staticmethod
    def initiate_gateway(payment_id: int, gateway: str):
        raise NotImplementedError("Official payment gateways will be integrated later")