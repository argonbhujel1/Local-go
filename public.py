from flask import Blueprint, render_template, jsonify
from app.models.location import Municipality
from app.models.vehicle import VehicleType
from app.models.advertisement import Advertisement
from datetime import date

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    municipalities = Municipality.query.filter_by(is_serviceable=True, is_active=True).all()
    vehicle_types = VehicleType.query.filter_by(is_active=True).all()
    ads = (
        Advertisement.query.filter(
            Advertisement.status == "ACTIVE",
            Advertisement.placement == "homepage",
            Advertisement.start_date <= date.today(),
            Advertisement.end_date >= date.today(),
        )
        .limit(5)
        .all()
    )
    return render_template(
        "public/index.html",
        municipalities=municipalities,
        vehicle_types=vehicle_types,
        ads=ads,
    )


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/manifest.json")
def manifest():
    return jsonify({
        "name": "LocalGo Nepal – Ride & Delivery",
        "short_name": "LocalGo",
        "description": "Local ride, food, parcel & document delivery for Urlabari, Kanepokhari, Pathari, Damak & surrounding areas",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#16a34a",
        "orientation": "portrait-primary",
        "icons": [
            {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    })