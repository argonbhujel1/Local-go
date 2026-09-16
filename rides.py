from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.ride import Ride, RideStatus
from app.services.ride_service import RideService
from app.services.fare_service import FareService

rides_api = Blueprint("rides_api", __name__)


@rides_api.route("/estimate", methods=["POST"])
@login_required
def estimate():
    data = request.get_json() or {}
    try:
        fare = FareService.calculate_ride_fare(
            vehicle_type_id=int(data["vehicle_type_id"]),
            distance_km=float(data.get("distance_km", 0)),
            duration_minutes=float(data.get("duration_minutes", 0)),
            route_id=data.get("route_id"),
            promo_code=data.get("promo_code"),
        )
        return jsonify({"ok": True, "fare": fare})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@rides_api.route("/book", methods=["POST"])
@login_required
def book():
    data = request.get_json() or {}
    try:
        ride = RideService.create_ride(
            customer_id=current_user.id,
            vehicle_type_id=int(data["vehicle_type_id"]),
            pickup_lat=float(data["pickup_lat"]),
            pickup_lng=float(data["pickup_lng"]),
            destination_lat=float(data["destination_lat"]),
            destination_lng=float(data["destination_lng"]),
            pickup_address=data.get("pickup_address"),
            destination_address=data.get("destination_address"),
            ride_type=data.get("ride_type", "INSTANT"),
            distance_km=float(data.get("distance_km", 0)),
            duration_minutes=float(data.get("duration_minutes", 0)),
            route_id=data.get("route_id"),
            promo_code=data.get("promo_code"),
        )
        return jsonify({"ok": True, "job_id": ride.job_id, "ride_id": ride.id, "total_fare": float(ride.total_fare)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@rides_api.route("/<int:ride_id>/accept", methods=["POST"])
@login_required
def accept(ride_id):
    if not current_user.partner:
        return jsonify({"ok": False, "error": "Not a partner"}), 403
    data = request.get_json() or {}
    try:
        ride = RideService.accept_ride(
            ride_id=ride_id,
            partner_id=current_user.partner.id,
            vehicle_id=int(data["vehicle_id"]),
        )
        return jsonify({"ok": True, "job_id": ride.job_id, "status": ride.status})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@rides_api.route("/<int:ride_id>/status", methods=["POST"])
@login_required
def update_status(ride_id):
    data = request.get_json() or {}
    try:
        ride = RideService.update_status(ride_id, data.get("status"), current_user.id)
        return jsonify({"ok": True, "status": ride.status})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@rides_api.route("/<job_id>")
@login_required
def get_ride(job_id):
    ride = Ride.query.filter_by(job_id=job_id).first()
    if not ride:
        return jsonify({"ok": False, "error": "Not found"}), 404
    # Privacy: only customer or assigned partner
    if ride.customer_id != current_user.id and (
        not current_user.partner or ride.partner_id != current_user.partner.id
    ):
        if not current_user.is_admin:
            return jsonify({"ok": False, "error": "Forbidden"}), 403
    return jsonify({
        "ok": True,
        "ride": {
            "job_id": ride.job_id,
            "status": ride.status,
            "pickup_lat": ride.pickup_lat,
            "pickup_lng": ride.pickup_lng,
            "destination_lat": ride.destination_lat,
            "destination_lng": ride.destination_lng,
            "total_fare": float(ride.total_fare) if ride.total_fare else 0,
            "partner_id": ride.partner_id,
        },
    })