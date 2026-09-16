"""Ride booking, matching and lifecycle."""
import secrets
import string
from datetime import datetime
from typing import Optional, List

from app import db, socketio
from app.models.ride import Ride, RideStatus, RideType
from app.models.partner import Partner, PartnerStatus
from app.models.vehicle import Vehicle, VehicleType
from app.services.fare_service import FareService
from app.services.wallet_service import WalletService
from app.services.notification_service import NotificationService


def _generate_job_id(prefix: str = "R") -> str:
    ts = datetime.utcnow().strftime("%y%m%d")
    rand = "".join(secrets.choice(string.digits) for _ in range(6))
    return f"{prefix}{ts}{rand}"


class RideService:
    @staticmethod
    def create_ride(
        *,
        customer_id: int,
        vehicle_type_id: int,
        pickup_lat: float,
        pickup_lng: float,
        destination_lat: float,
        destination_lng: float,
        pickup_address: str = None,
        destination_address: str = None,
        ride_type: str = RideType.INSTANT.value,
        scheduled_at: datetime = None,
        promo_code: str = None,
        distance_km: float = 0,
        duration_minutes: float = 0,
        route_id: int = None,
    ) -> Ride:
        fare = FareService.calculate_ride_fare(
            vehicle_type_id=vehicle_type_id,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            route_id=route_id,
            promo_code=promo_code,
        )

        ride = Ride(
            job_id=_generate_job_id("R"),
            customer_id=customer_id,
            vehicle_type_id=vehicle_type_id,
            route_id=route_id,
            ride_type=ride_type,
            status=RideStatus.REQUESTED.value,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            pickup_address=pickup_address,
            destination_lat=destination_lat,
            destination_lng=destination_lng,
            destination_address=destination_address,
            scheduled_at=scheduled_at,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            base_fare=fare["base_fare"],
            distance_fare=fare["distance_fare"],
            time_fare=fare["time_fare"],
            platform_fee=fare["platform_fee"],
            discount=fare["discount"],
            total_fare=fare["total_fare"],
            promo_code_id=fare.get("promo_id"),
        )
        db.session.add(ride)
        db.session.commit()

        # Notify nearby partners via SocketIO
        socketio.emit(
            "new_ride_request",
            {
                "job_id": ride.job_id,
                "pickup_lat": pickup_lat,
                "pickup_lng": pickup_lng,
                "vehicle_type_id": vehicle_type_id,
                "total_fare": float(ride.total_fare),
            },
            room="partners_online",
        )
        return ride

    @staticmethod
    def accept_ride(ride_id: int, partner_id: int, vehicle_id: int) -> Ride:
        ride = db.session.get(Ride, ride_id)
        if not ride or ride.status not in (RideStatus.REQUESTED.value, RideStatus.SEARCHING.value):
            raise ValueError("Ride not available")

        partner = db.session.get(Partner, partner_id)
        if not partner or partner.status != PartnerStatus.APPROVED.value or not partner.is_online:
            raise ValueError("Partner not eligible")

        if not WalletService.can_accept_jobs(partner_id):
            raise ValueError("Insufficient wallet balance")

        vehicle = db.session.get(Vehicle, vehicle_id)
        if not vehicle or vehicle.partner_id != partner_id:
            raise ValueError("Invalid vehicle")

        ride.partner_id = partner_id
        ride.vehicle_id = vehicle_id
        ride.status = RideStatus.ACCEPTED.value
        ride.accepted_at = datetime.utcnow()
        db.session.commit()

        NotificationService.notify_user(
            ride.customer_id,
            title="Ride Accepted",
            body=f"Your ride {ride.job_id} has been accepted.",
            type="ride_accepted",
            data={"job_id": ride.job_id},
        )
        socketio.emit(
            "ride_accepted",
            {"job_id": ride.job_id, "partner_id": partner_id},
            room=f"ride_{ride.job_id}",
        )
        return ride

    @staticmethod
    def update_status(ride_id: int, new_status: str, actor_id: int = None) -> Ride:
        ride = db.session.get(Ride, ride_id)
        if not ride:
            raise ValueError("Ride not found")

        allowed = {
            RideStatus.ACCEPTED.value: [RideStatus.ARRIVING.value, RideStatus.CANCELLED.value],
            RideStatus.ARRIVING.value: [RideStatus.ARRIVED.value, RideStatus.CANCELLED.value],
            RideStatus.ARRIVED.value: [RideStatus.STARTED.value, RideStatus.CANCELLED.value],
            RideStatus.STARTED.value: [RideStatus.COMPLETED.value, RideStatus.CANCELLED.value],
        }
        current = ride.status
        if new_status not in allowed.get(current, []):
            raise ValueError(f"Cannot transition from {current} to {new_status}")

        ride.status = new_status
        now = datetime.utcnow()
        if new_status == RideStatus.ARRIVED.value:
            ride.arrived_at = now
        elif new_status == RideStatus.STARTED.value:
            ride.started_at = now
        elif new_status == RideStatus.COMPLETED.value:
            ride.completed_at = now
            # Deduct platform fee from partner wallet
            if ride.partner_id and ride.platform_fee:
                WalletService.deduct_platform_fee(
                    ride.partner_id,
                    float(ride.platform_fee),
                    ride.job_id,
                    f"Platform fee for ride {ride.job_id}",
                )
        elif new_status == RideStatus.CANCELLED.value:
            ride.cancelled_at = now

        db.session.commit()
        socketio.emit(
            "ride_status",
            {"job_id": ride.job_id, "status": new_status},
            room=f"ride_{ride.job_id}",
        )
        return ride

    @staticmethod
    def find_nearby_partners(
        lat: float, lng: float, vehicle_type_id: int, radius_km: float = 5.0
    ) -> List[Partner]:
        # Simple bounding-box filter; production should use PostGIS
        delta = radius_km / 111.0  # approx degrees
        partners = (
            Partner.query.filter(
                Partner.status == PartnerStatus.APPROVED.value,
                Partner.is_online.is_(True),
                Partner.last_location_lat.between(lat - delta, lat + delta),
                Partner.last_location_lng.between(lng - delta, lng + delta),
            )
            .all()
        )
        return partners