from datetime import datetime
from app import db


class Shop(db.Model):
    __tablename__ = "shops"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False, index=True)
    slug = db.Column(db.String(140), unique=True)
    category = db.Column(db.String(50))  # Grocery, Pharmacy, Clothing, etc.
    description = db.Column(db.Text)
    logo = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"))
    is_approved = db.Column(db.Boolean, default=False)
    is_open = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    commission_percent = db.Column(db.Float, default=8.0)
    fixed_order_fee = db.Column(db.Numeric(10, 2), default=0)
    average_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship("User")
    municipality = db.relationship("Municipality")
    products = db.relationship("Product", back_populates="shop", lazy="dynamic")
    orders = db.relationship("ShopOrder", back_populates="shop", lazy="dynamic")


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_price = db.Column(db.Numeric(10, 2))
    image = db.Column(db.String(255))
    stock = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20), default="pcs")
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    shop = db.relationship("Shop", back_populates="products")


class ShopOrder(db.Model):
    __tablename__ = "shop_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=False)
    status = db.Column(db.String(30), default="PENDING", index=True)

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
    payment_status = db.Column(db.String(20), default="PENDING")
    payment_method = db.Column(db.String(30))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship("User")
    shop = db.relationship("Shop", back_populates="orders")
    items = db.relationship("ShopOrderItem", back_populates="order", lazy="dynamic", cascade="all, delete-orphan")
    delivery = db.relationship("Delivery", back_populates="shop_order", uselist=False)


class ShopOrderItem(db.Model):
    __tablename__ = "shop_order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("shop_orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship("ShopOrder", back_populates="items")
    product = db.relationship("Product")