from datetime import datetime
from enum import Enum
from app import db


class FoodOrderStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY = "READY"
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False, index=True)
    slug = db.Column(db.String(140), unique=True)
    description = db.Column(db.Text)
    logo = db.Column(db.String(255))
    cover_image = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"))
    is_approved = db.Column(db.Boolean, default=False)
    is_open = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    preparation_time_min = db.Column(db.Integer, default=30)
    min_order_amount = db.Column(db.Numeric(10, 2), default=0)
    commission_percent = db.Column(db.Float, default=10.0)
    fixed_order_fee = db.Column(db.Numeric(10, 2), default=0)
    average_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship("User")
    municipality = db.relationship("Municipality")
    categories = db.relationship("RestaurantCategory", back_populates="restaurant", lazy="dynamic")
    menu_items = db.relationship("MenuItem", back_populates="restaurant", lazy="dynamic")
    orders = db.relationship("FoodOrder", back_populates="restaurant", lazy="dynamic")


class RestaurantCategory(db.Model):
    __tablename__ = "restaurant_categories"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    restaurant = db.relationship("Restaurant", back_populates="categories")
    items = db.relationship("MenuItem", back_populates="category", lazy="dynamic")


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("restaurant_categories.id"))
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_price = db.Column(db.Numeric(10, 2))
    image = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    is_veg = db.Column(db.Boolean, default=True)
    preparation_time_min = db.Column(db.Integer)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    restaurant = db.relationship("Restaurant", back_populates="menu_items")
    category = db.relationship("RestaurantCategory", back_populates="items")


class FoodOrder(db.Model):
    __tablename__ = "food_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    status = db.Column(db.String(30), default=FoodOrderStatus.PENDING.value, index=True)

    delivery_address = db.Column(db.String(255))
    delivery_lat = db.Column(db.Float)
    delivery_lng = db.Column(db.Float)
    delivery_phone = db.Column(db.String(20))
    special_instructions = db.Column(db.Text)

    subtotal = db.Column(db.Numeric(10, 2), default=0)
    delivery_fee = db.Column(db.Numeric(10, 2), default=0)
    platform_fee = db.Column(db.Numeric(10, 2), default=0)
    discount = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), default=0)
    promo_code_id = db.Column(db.Integer, db.ForeignKey("promo_codes.id"))
    payment_status = db.Column(db.String(20), default="PENDING")
    payment_method = db.Column(db.String(30))

    accepted_at = db.Column(db.DateTime)
    preparing_at = db.Column(db.DateTime)
    ready_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship("User")
    restaurant = db.relationship("Restaurant", back_populates="orders")
    items = db.relationship("FoodOrderItem", back_populates="order", lazy="dynamic", cascade="all, delete-orphan")
    delivery = db.relationship("Delivery", back_populates="food_order", uselist=False)
    promo_code = db.relationship("PromoCode")


class FoodOrderItem(db.Model):
    __tablename__ = "food_order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("food_orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.String(255))

    order = db.relationship("FoodOrder", back_populates="items")
    menu_item = db.relationship("MenuItem")