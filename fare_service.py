"""Server-side fare calculation engine. Never trust client values."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, time
from typing import Optional, Dict, Any

from app import db
from app.models.route import Route, FareRule
from app.models.vehicle import VehicleType
from app.models.promo import PromoCode


def _d(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _round(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class FareService:
    @staticmethod
    def calculate_ride_fare(
        *,
        vehicle_type_id: int,
        distance_km: float,
        duration_minutes: float = 0,
        waiting_minutes: float = 0,
        route_id: Optional[int] = None,
        promo_code: Optional[str] = None,
        is_peak: bool = False,
    ) -> Dict[str, Any]:
        vt = db.session.get(VehicleType, vehicle_type_id)
        if not vt:
            raise ValueError("Invalid vehicle type")

        base = _d(vt.base_fare)
        per_km = _d(vt.per_km_fare)
        per_min = _d(vt.per_minute_fare)
        minimum = _d(vt.minimum_fare)
        platform_fee = _d(vt.platform_fee)
        peak_mult = Decimal("1.0")
        waiting_rate = Decimal("0")

        # Override from route if present
        if route_id:
            route = db.session.get(Route, route_id)
            if route and route.is_active:
                if route.base_fare:
                    base = _d(route.base_fare)
                if route.per_km_fare:
                    per_km = _d(route.per_km_fare)
                if route.per_minute_fare:
                    per_min = _d(route.per_minute_fare)
                if route.minimum_fare:
                    minimum = _d(route.minimum_fare)
                if route.platform_fee:
                    platform_fee = _d(route.platform_fee)
                if route.peak_multiplier:
                    peak_mult = _d(route.peak_multiplier)
                if route.waiting_fee_per_min:
                    waiting_rate = _d(route.waiting_fee_per_min)

                # Fine-grained fare rule
                rule = (
                    FareRule.query.filter_by(
                        route_id=route_id,
                        vehicle_type_id=vehicle_type_id,
                        is_active=True,
                    )
                    .first()
                )
                if rule:
                    if rule.base_fare is not None:
                        base = _d(rule.base_fare)
                    if rule.per_km_fare is not None:
                        per_km = _d(rule.per_km_fare)
                    if rule.per_minute_fare is not None:
                        per_min = _d(rule.per_minute_fare)
                    if rule.minimum_fare is not None:
                        minimum = _d(rule.minimum_fare)
                    if rule.platform_fee is not None:
                        platform_fee = _d(rule.platform_fee)
                    if rule.peak_multiplier:
                        peak_mult = _d(rule.peak_multiplier)
                    if rule.waiting_fee_per_min is not None:
                        waiting_rate = _d(rule.waiting_fee_per_min)

        distance_fare = per_km * _d(distance_km)
        time_fare = per_min * _d(duration_minutes)
        waiting_fare = waiting_rate * _d(waiting_minutes)
        subtotal = base + distance_fare + time_fare + waiting_fare

        peak_fare = Decimal("0")
        if is_peak and peak_mult > 1:
            peak_fare = _round(subtotal * (peak_mult - 1))
            subtotal += peak_fare

        if subtotal < minimum:
            subtotal = minimum

        discount = Decimal("0")
        promo = None
        if promo_code:
            promo = PromoCode.query.filter_by(code=promo_code.upper(), is_active=True).first()
            if promo and FareService._promo_valid(promo, service_type="RIDE", amount=subtotal):
                if promo.discount_type == "PERCENT":
                    discount = _round(subtotal * _d(promo.discount_value) / 100)
                    if promo.max_discount:
                        discount = min(discount, _d(promo.max_discount))
                else:
                    discount = min(_d(promo.discount_value), subtotal)

        total = _round(subtotal - discount + platform_fee)

        return {
            "base_fare": float(_round(base)),
            "distance_fare": float(_round(distance_fare)),
            "time_fare": float(_round(time_fare)),
            "waiting_fare": float(_round(waiting_fare)),
            "peak_fare": float(_round(peak_fare)),
            "discount": float(_round(discount)),
            "platform_fee": float(_round(platform_fee)),
            "total_fare": float(total),
            "promo_id": promo.id if promo else None,
        }

    @staticmethod
    def calculate_delivery_fee(
        *,
        service_type: str,
        distance_km: float = 0,
        route_id: Optional[int] = None,
        vehicle_type_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        # Simple defaults; admin-configurable via PlatformFee / Route
        base = Decimal("20")
        per_km = Decimal("10")
        platform_fee = Decimal("5")

        if route_id:
            route = db.session.get(Route, route_id)
            if route:
                if route.delivery_fee:
                    base = _d(route.delivery_fee)
                if route.platform_fee:
                    platform_fee = _d(route.platform_fee)

        delivery_fee = _round(base + per_km * _d(distance_km))
        total = _round(delivery_fee + platform_fee)

        return {
            "delivery_fee": float(delivery_fee),
            "platform_fee": float(_round(platform_fee)),
            "total_fare": float(total),
        }

    @staticmethod
    def _promo_valid(promo: PromoCode, service_type: str, amount: Decimal) -> bool:
        now = datetime.utcnow()
        if promo.start_date and now < promo.start_date:
            return False
        if promo.end_date and now > promo.end_date:
            return False
        if promo.usage_limit and promo.used_count >= promo.usage_limit:
            return False
        if promo.min_order_amount and amount < _d(promo.min_order_amount):
            return False
        if promo.service_types and service_type not in promo.service_types:
            return False
        return True