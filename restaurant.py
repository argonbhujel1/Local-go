from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.food import Restaurant, MenuItem, RestaurantCategory, FoodOrder

restaurant_bp = Blueprint("restaurant", __name__)


@restaurant_bp.route("/dashboard")
@login_required
def dashboard():
    rest = Restaurant.query.filter_by(owner_id=current_user.id).first()
    if not rest:
        flash("No restaurant linked to your account.", "info")
        return redirect(url_for("passenger.dashboard"))
    pending = FoodOrder.query.filter_by(restaurant_id=rest.id, status="PENDING").count()
    return render_template("restaurant/dashboard.html", restaurant=rest, pending=pending)


@restaurant_bp.route("/menu")
@login_required
def menu():
    rest = Restaurant.query.filter_by(owner_id=current_user.id).first()
    if not rest:
        return redirect(url_for("passenger.dashboard"))
    items = MenuItem.query.filter_by(restaurant_id=rest.id).all()
    return render_template("restaurant/menu.html", restaurant=rest, items=items)


@restaurant_bp.route("/orders")
@login_required
def orders():
    rest = Restaurant.query.filter_by(owner_id=current_user.id).first()
    if not rest:
        return redirect(url_for("passenger.dashboard"))
    orders = FoodOrder.query.filter_by(restaurant_id=rest.id).order_by(FoodOrder.created_at.desc()).limit(50).all()
    return render_template("restaurant/orders.html", restaurant=rest, orders=orders)