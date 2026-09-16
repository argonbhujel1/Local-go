from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, Role
from app.models.wallet import Wallet
from app.services.wallet_service import WalletService
import secrets
import string

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("passenger.dashboard"))

    if request.method == "POST":
        phone = (request.form.get("phone") or "").strip()
        full_name = (request.form.get("full_name") or "").strip()
        password = request.form.get("password") or ""
        email = (request.form.get("email") or "").strip() or None

        if not phone or not full_name or len(password) < 6:
            flash("Please fill all required fields (password min 6 chars).", "error")
            return render_template("auth/register.html")

        if User.query.filter_by(phone=phone).first():
            flash("Phone number already registered.", "error")
            return render_template("auth/register.html")

        user = User(phone=phone, full_name=full_name, email=email)
        user.set_password(password)
        user.generate_referral_code()

        # Default passenger role
        role = Role.query.filter_by(name="passenger").first()
        if role:
            user.roles.append(role)

        db.session.add(user)
        db.session.commit()
        WalletService.get_or_create_user_wallet(user.id)

        login_user(user)
        flash("Welcome to LocalGo! Account created.", "success")
        return redirect(url_for("passenger.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("passenger.dashboard"))

    if request.method == "POST":
        phone = (request.form.get("phone") or "").strip()
        password = request.form.get("password") or ""
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(phone=phone).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = __import__("datetime").datetime.utcnow()
            db.session.commit()
            next_url = request.args.get("next")
            if user.is_admin:
                return redirect(next_url or url_for("admin.dashboard"))
            if user.is_partner:
                return redirect(next_url or url_for("partner.dashboard"))
            return redirect(next_url or url_for("passenger.dashboard"))

        flash("Invalid phone or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("public.index"))