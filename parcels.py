from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.parcel import Parcel, DocumentDelivery
from app.models.delivery import Delivery, DeliveryStatus, ServiceType
from app.services.fare_service import FareService
import secrets
from datetime import datetime

parcels_api = Blueprint("parcels_api", __name__)


def _tracking():
    return f"P{datetime.utcnow().strftime('%y%m%d')}{secrets.randbelow(999999):06d}"


@parcels_api.route("/create", methods=["POST"])
@login_required
def create_parcel():
    data = request.get_json() or {}
    tracking = _tracking()
    parcel = Parcel(
        tracking_number=tracking,
        customer_id=current_user.id,
        parcel_type=data.get("parcel_type", "OTHER"),
        description=data.get("description"),
        approximate_weight_kg=data.get("weight"),
        quantity=data.get("quantity", 1),
        special_instructions=data.get("special_instructions"),
        receiver_name=data.get("receiver_name"),
        receiver_phone=data.get("receiver_phone"),
    )
    db.session.add(parcel)
    db.session.flush()

    fee = FareService.calculate_delivery_fee(
        service_type="PARCEL",
        distance_km=float(data.get("distance_km", 3)),
    )
    delivery = Delivery(
        job_id=tracking,
        service_type=ServiceType.PARCEL.value,
        customer_id=current_user.id,
        status=DeliveryStatus.PENDING.value,
        pickup_address=data.get("pickup_address"),
        pickup_lat=data.get("pickup_lat"),
        pickup_lng=data.get("pickup_lng"),
        destination_address=data.get("destination_address"),
        destination_lat=data.get("destination_lat"),
        destination_lng=data.get("destination_lng"),
        destination_contact_name=data.get("receiver_name"),
        destination_contact_phone=data.get("receiver_phone"),
        special_instructions=data.get("special_instructions"),
        delivery_fee=fee["delivery_fee"],
        platform_fee=fee["platform_fee"],
        total_fare=fee["total_fare"],
        parcel_id=parcel.id,
    )
    db.session.add(delivery)
    db.session.commit()
    return jsonify({"ok": True, "tracking_number": tracking, "total_fare": fee["total_fare"]})


@parcels_api.route("/document", methods=["POST"])
@login_required
def create_document():
    data = request.get_json() or {}
    tracking = f"D{datetime.utcnow().strftime('%y%m%d')}{secrets.randbelow(999999):06d}"
    doc = DocumentDelivery(
        tracking_number=tracking,
        customer_id=current_user.id,
        document_type=data.get("document_type"),
        description=data.get("description"),
        is_sensitive=data.get("is_sensitive", True),
        require_otp=data.get("require_otp", True),
        require_signature=data.get("require_signature", True),
        sender_name=data.get("sender_name") or current_user.full_name,
        sender_phone=data.get("sender_phone") or current_user.phone,
        receiver_name=data.get("receiver_name"),
        receiver_phone=data.get("receiver_phone"),
        special_instructions=data.get("special_instructions"),
    )
    db.session.add(doc)
    db.session.flush()

    fee = FareService.calculate_delivery_fee(service_type="DOCUMENT", distance_km=float(data.get("distance_km", 3)))
    delivery = Delivery(
        job_id=tracking,
        service_type=ServiceType.DOCUMENT.value,
        customer_id=current_user.id,
        status=DeliveryStatus.PENDING.value,
        pickup_address=data.get("pickup_address"),
        pickup_lat=data.get("pickup_lat"),
        pickup_lng=data.get("pickup_lng"),
        destination_address=data.get("destination_address"),
        destination_lat=data.get("destination_lat"),
        destination_lng=data.get("destination_lng"),
        destination_contact_name=data.get("receiver_name"),
        destination_contact_phone=data.get("receiver_phone"),
        delivery_fee=fee["delivery_fee"],
        platform_fee=fee["platform_fee"],
        total_fare=fee["total_fare"],
        document_id=doc.id,
        otp_code=f"{secrets.randbelow(9999):04d}" if data.get("require_otp", True) else None,
    )
    db.session.add(delivery)
    db.session.commit()
    return jsonify({"ok": True, "tracking_number": tracking, "total_fare": fee["total_fare"]})