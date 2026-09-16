from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User, Role
from app.models.partner import Partner, PartnerStatus
from app.models.vehicle import VehicleType, Vehicle
from app.models.location import Municipality, Ward, Area
from app.models.route import Route
from app.models.ride import Ride
from app.models.food import Restaurant, FoodOrder
from app.models.wallet import Wallet
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    today = datetime.utcnow().date()
    stats = {
        "users": User.query.count(),
        "partners": Partner.query.count(),
        "online_partners": Partner.query.filter_by(is_online=True).count(),
        "pending_partners": Partner.query.filter_by(status=PartnerStatus.PENDING.value).count(),
        "active_rides": Ride.query.filter(
            Ride.status.in_(["REQUESTED", "ACCEPTED", "ARRIVING", "ARRIVED", "STARTED"])
        ).count(),
        "restaurants": Restaurant.query.count(),
        "today_rides": Ride.query.filter(db.func.date(Ride.created_at) == today).count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/partners")
@login_required
@admin_required
def partners():
    status = request.args.get("status")
    q = Partner.query
    if status:
        q = q.filter_by(status=status)
    partners = q.order_by(Partner.created_at.desc()).all()
    return render_template("admin/partners.html", partners=partners)


@admin_bp.route("/partners/<int:pid>/approve", methods=["POST"])
@login_required
@admin_required
def approve_partner(pid):
    partner = db.session.get(Partner, pid)
    if partner:
        partner.status = PartnerStatus.APPROVED.value
        partner.approved_at = datetime.utcnow()
        partner.approved_by_id = current_user.id
        db.session.commit()
        flash(f"Partner {partner.user.full_name} approved.", "success")
    return redirect(url_for("admin.partners"))


@admin_bp.route("/partners/<int:pid>/reject", methods=["POST"])
@login_required
@admin_required
def reject_partner(pid):
    partner = db.session.get(Partner, pid)
    if partner:
        partner.status = PartnerStatus.REJECTED.value
        partner.rejection_reason = request.form.get("reason", "")
        db.session.commit()
        flash("Partner rejected.", "info")
    return redirect(url_for("admin.partners"))


@admin_bp.route("/municipalities")
@login_required
@admin_required
def municipalities():
    items = Municipality.query.order_by(Municipality.district, Municipality.name).all()
    return render_template("admin/municipalities.html", municipalities=items)


@admin_bp.route("/municipalities/add", methods=["POST"])
@login_required
@admin_required
def add_municipality():
    m = Municipality(
        name=request.form.get("name"),
        type=request.form.get("type", "Municipality"),
        district=request.form.get("district"),
        province=request.form.get("province", "Koshi"),
        latitude=request.form.get("latitude", type=float),
        longitude=request.form.get("longitude", type=float),
        is_serviceable=True,
    )
    db.session.add(m)
    db.session.commit()
    flash("Municipality added.", "success")
    return redirect(url_for("admin.municipalities"))


@admin_bp.route("/routes")
@login_required
@admin_required
def routes():
    routes = Route.query.all()
    municipalities = Municipality.query.filter_by(is_active=True).all()
    return render_template("admin/routes.html", routes=routes, municipalities=municipalities)


@admin_bp.route("/vehicle-types")
@login_required
@admin_required
def vehicle_types():
    types = VehicleType.query.all()
    return render_template("admin/vehicle_types.html", vehicle_types=types)


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).limit(100).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/rides")
@login_required
@admin_required
def rides():
    rides = Ride.query.order_by(Ride.created_at.desc()).limit(100).all()
    return render_template("admin/rides.html", rides=rides)


@admin_bp.route("/settings")
@login_required
@admin_required
def settings():
    return render_template("admin/settings.html")