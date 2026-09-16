from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.partner import Partner, PartnerStatus, PartnerService
from app.models.vehicle import Vehicle, VehicleType
from app.models.ride import Ride, RideStatus
from app.models.wallet import Wallet
from app.services.wallet_service import WalletService

partner_bp = Blueprint("partner", __name__)


def partner_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.partner:
            flash("Please complete partner registration first.", "info")
            return redirect(url_for("partner.register"))
        return f(*args, **kwargs)
    return decorated


@partner_bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if current_user.partner:
        return redirect(url_for("partner.dashboard"))

    vehicle_types = VehicleType.query.filter_by(is_active=True).all()

    if request.method == "POST":
        partner = Partner(
            user_id=current_user.id,
            status=PartnerStatus.PENDING.value,
            citizenship_number=request.form.get("citizenship_number"),
            emergency_contact_name=request.form.get("emergency_contact_name"),
            emergency_contact_phone=request.form.get("emergency_contact_phone"),
        )
        db.session.add(partner)
        db.session.flush()

        vt_id = request.form.get("vehicle_type_id", type=int)
        if vt_id:
            vt = db.session.get(VehicleType, vt_id)
            vehicle = Vehicle(
                partner_id=partner.id,
                vehicle_type_id=vt_id,
                number_plate=request.form.get("number_plate") if vt and vt.requires_number_plate else None,
                registration_number=request.form.get("registration_number") if vt and vt.requires_registration else None,
                license_number=request.form.get("license_number") if vt and vt.requires_license else None,
                color=request.form.get("color"),
                model=request.form.get("model"),
            )
            db.session.add(vehicle)

            services = request.form.getlist("services")
            for s in services:
                ps = PartnerService(partner_id=partner.id, service_type=s, vehicle_type_id=vt_id)
                db.session.add(ps)

        db.session.commit()
        WalletService.get_or_create_partner_wallet(partner.id)
        flash("Partner registration submitted. Awaiting admin approval.", "success")
        return redirect(url_for("partner.dashboard"))

    return render_template("partner/register.html", vehicle_types=vehicle_types)


@partner_bp.route("/dashboard")
@partner_required
def dashboard():
    partner = current_user.partner
    wallet = WalletService.get_or_create_partner_wallet(partner.id)
    active_jobs = Ride.query.filter(
        Ride.partner_id == partner.id,
        Ride.status.in_([
            RideStatus.ACCEPTED.value,
            RideStatus.ARRIVING.value,
            RideStatus.ARRIVED.value,
            RideStatus.STARTED.value,
        ]),
    ).all()
    return render_template(
        "partner/dashboard.html",
        partner=partner,
        wallet=wallet,
        active_jobs=active_jobs,
    )


@partner_bp.route("/jobs")
@partner_required
def jobs():
    partner = current_user.partner
    rides = (
        Ride.query.filter_by(partner_id=partner.id)
        .order_by(Ride.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template("partner/jobs.html", rides=rides)


@partner_bp.route("/earnings")
@partner_required
def earnings():
    partner = current_user.partner
    wallet = WalletService.get_or_create_partner_wallet(partner.id)
    txs = wallet.transactions.order_by(db.desc("created_at")).limit(50).all()
    return render_template("partner/earnings.html", wallet=wallet, transactions=txs)


@partner_bp.route("/toggle-online", methods=["POST"])
@partner_required
def toggle_online():
    partner = current_user.partner
    if partner.status != PartnerStatus.APPROVED.value:
        return jsonify({"ok": False, "error": "Not approved"}), 403
    if not partner.can_go_online():
        return jsonify({"ok": False, "error": "Wallet balance too low"}), 400
    partner.is_online = not partner.is_online
    db.session.commit()
    return jsonify({"ok": True, "is_online": partner.is_online})


@partner_bp.route("/profile")
@partner_required
def profile():
    return render_template("partner/profile.html", partner=current_user.partner)


@partner_bp.route("/messages")
@partner_required
def messages():
    return render_template("partner/messages.html")