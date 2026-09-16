from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.food import Restaurant, MenuItem, FoodOrder, FoodOrderItem, FoodOrderStatus
from app.services.fare_service import FareService
import secrets
from datetime import datetime

food_api = Blueprint("food_api", __name__)


@food_api.route("/restaurants")
def restaurants():
    items = Restaurant.query.filter_by(is_approved=True, is_active=True).all()
    return jsonify({
        "ok": True,
        "restaurants": [
            {
                "id": r.id,
                "name": r.name,
                "address": r.address,
                "lat": r.latitude,
                "lng": r.longitude,
                "rating": r.average_rating,
                "prep_time": r.preparation_time_min,
            }
            for r in items
        ],
    })


@food_api.route("/restaurants/<int:rid>/menu")
def menu(rid):
    items = MenuItem.query.filter_by(restaurant_id=rid, is_available=True).all()
    return jsonify({
        "ok": True,
        "items": [
            {
                "id": i.id,
                "name": i.name,
                "price": float(i.price),
                "discount_price": float(i.discount_price) if i.discount_price else None,
                "image": i.image,
                "is_veg": i.is_veg,
            }
            for i in items
        ],
    })


@food_api.route("/order", methods=["POST"])
@login_required
def place_order():
    data = request.get_json() or {}
    rest_id = data.get("restaurant_id")
    items = data.get("items", [])
    if not rest_id or not items:
        return jsonify({"ok": False, "error": "Invalid order"}), 400

    rest = db.session.get(Restaurant, rest_id)
    if not rest or not rest.is_approved:
        return jsonify({"ok": False, "error": "Restaurant unavailable"}), 400

    subtotal = 0
    order = FoodOrder(
        order_id=f"F{datetime.utcnow().strftime('%y%m%d')}{secrets.randbelow(999999):06d}",
        customer_id=current_user.id,
        restaurant_id=rest_id,
        delivery_address=data.get("delivery_address"),
        delivery_lat=data.get("delivery_lat"),
        delivery_lng=data.get("delivery_lng"),
        delivery_phone=data.get("delivery_phone") or current_user.phone,
        special_instructions=data.get("special_instructions"),
        status=FoodOrderStatus.PENDING.value,
    )
    db.session.add(order)
    db.session.flush()

    for it in items:
        mi = db.session.get(MenuItem, it["menu_item_id"])
        if not mi or mi.restaurant_id != rest_id:
            continue
        qty = int(it.get("quantity", 1))
        price = float(mi.discount_price or mi.price)
        total = price * qty
        subtotal += total
        db.session.add(FoodOrderItem(
            order_id=order.id,
            menu_item_id=mi.id,
            quantity=qty,
            unit_price=price,
            total_price=total,
        ))

    fee = FareService.calculate_delivery_fee(service_type="FOOD", distance_km=float(data.get("distance_km", 2)))
    order.subtotal = subtotal
    order.delivery_fee = fee["delivery_fee"]
    order.platform_fee = fee["platform_fee"]
    order.total = subtotal + fee["delivery_fee"] + fee["platform_fee"]
    db.session.commit()

    return jsonify({"ok": True, "order_id": order.order_id, "total": float(order.total)})