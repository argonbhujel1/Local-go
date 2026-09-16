from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.shop import Shop, Product, ShopOrder

shop_bp = Blueprint("shop", __name__)


@shop_bp.route("/dashboard")
@login_required
def dashboard():
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    if not shop:
        flash("No shop linked.", "info")
        return redirect(url_for("passenger.dashboard"))
    return render_template("shop/dashboard.html", shop=shop)


@shop_bp.route("/products")
@login_required
def products():
    shop = Shop.query.filter_by(owner_id=current_user.id).first()
    if not shop:
        return redirect(url_for("passenger.dashboard"))
    products = Product.query.filter_by(shop_id=shop.id).all()
    return render_template("shop/products.html", shop=shop, products=products)