from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from app import db
from app.models.vehicle import VehicleType
from app.models.ride import Ride
from app.models.food import Restaurant, FoodOrder
from app.models.parcel import Parcel
from app.models.location import Municipality, SavedLocation
from app.services.ride_service import RideService
from app.services.fare_service import FareService

passenger_bp = Blueprint("passenger", __name__)


@passenger_bp.route("/dashboard")
@login_required
def dashboard():
    recent_rides = (
        Ride.query.filter_by(customer_id=current_user.id)
        .order_by(Ride.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template("passenger/dashboard.html", recent_rides=recent_rides)


@passenger_bp.route("/book-ride")
@login_required
def book_ride():
    vehicle_types = VehicleType.query.filter_by(is_active=True).all()
    municipalities = Municipality.query.filter_by(is_serviceable=True).all()
    saved = SavedLocation.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "passenger/book_ride.html",
        vehicle_types=vehicle_types,
        municipalities=municipalities,
        saved_locations=saved,
    )


@passenger_bp.route("/food")
@login_required
def food():
    restaurants = Restaurant.query.filter_by(is_approved=True, is_active=True, is_open=True).all()
    return render_template("passenger/food.html", restaurants=restaurants)


@passenger_bp.route("/send-parcel")
@login_required
def send_parcel():
    municipalities = Municipality.query.filter_by(is_serviceable=True).all()
    return render_template("passenger/send_parcel.html", municipalities=municipalities)


@passenger_bp.route("/send-document")
@login_required
def send_document():
    municipalities = Municipality.query.filter_by(is_serviceable=True).all()
    return render_template("passenger/send_document.html", municipalities=municipalities)


@passenger_bp.route("/orders")
@login_required
def orders():
    rides = Ride.query.filter_by(customer_id=current_user.id).order_by(Ride.created_at.desc()).limit(20).all()
    food_orders = FoodOrder.query.filter_by(customer_id=current_user.id).order_by(FoodOrder.created_at.desc()).limit(20).all()
    return render_template("passenger/orders.html", rides=rides, food_orders=food_orders)


@passenger_bp.route("/profile")
@login_required
def profile():
    return render_template("passenger/profile.html")


@passenger_bp.route("/messages")
@login_required
def messages():
    return render_template("passenger/messages.html")