from flask import Blueprint, jsonify, request
from app.models.location import Municipality, Area
from app.models.partner import Partner, PartnerStatus

maps_api = Blueprint("maps_api", __name__)


@maps_api.route("/municipalities")
def municipalities():
    items = Municipality.query.filter_by(is_serviceable=True, is_active=True).all()
    return jsonify({
        "ok": True,
        "municipalities": [
            {
                "id": m.id,
                "name": m.name,
                "district": m.district,
                "lat": m.latitude,
                "lng": m.longitude,
            }
            for m in items
        ],
    })


@maps_api.route("/nearby-partners")
def nearby_partners():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    if lat is None or lng is None:
        return jsonify({"ok": False, "error": "lat/lng required"}), 400
    # Bounding box ~5km
    delta = 0.045
    partners = Partner.query.filter(
        Partner.status == PartnerStatus.APPROVED.value,
        Partner.is_online.is_(True),
        Partner.last_location_lat.between(lat - delta, lat + delta),
        Partner.last_location_lng.between(lng - delta, lng + delta),
    ).limit(20).all()
    return jsonify({
        "ok": True,
        "partners": [
            {
                "id": p.id,
                "lat": p.last_location_lat,
                "lng": p.last_location_lng,
                "rating": p.average_rating,
            }
            for p in partners
        ],
    })