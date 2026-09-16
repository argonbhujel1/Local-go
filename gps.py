from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.system import GPSLocation
from datetime import datetime

gps_api = Blueprint("gps_api", __name__)


@gps_api.route("/update", methods=["POST"])
@login_required
def update():
    if not current_user.partner:
        return jsonify({"ok": False, "error": "Partners only"}), 403
    data = request.get_json() or {}
    lat = data.get("latitude")
    lng = data.get("longitude")
    if lat is None or lng is None:
        return jsonify({"ok": False, "error": "lat/lng required"}), 400

    partner = current_user.partner
    partner.last_location_lat = float(lat)
    partner.last_location_lng = float(lng)
    partner.last_location_at = datetime.utcnow()

    job_id = data.get("job_id")
    if job_id:
        loc = GPSLocation(
            job_id=job_id,
            partner_id=partner.id,
            latitude=float(lat),
            longitude=float(lng),
            accuracy=data.get("accuracy"),
            heading=data.get("heading"),
            speed=data.get("speed"),
        )
        db.session.add(loc)

    db.session.commit()
    return jsonify({"ok": True})