import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

from app.config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()
csrf = CSRFProtect()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.get(config_name, config["default"]))

    # Ensure instance & upload folders exist
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "vehicles"), exist_ok=True)
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "profiles"), exist_ok=True)
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "food"), exist_ok=True)
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "documents"), exist_ok=True)
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "ads"), exist_ok=True)
    except OSError:
        pass

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # SocketIO – use threading for simplicity in dev; switch to eventlet/redis in prod
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        logger=False,
        engineio_logger=False,
    )

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.passenger import passenger_bp
    from app.routes.partner import partner_bp
    from app.routes.restaurant import restaurant_bp
    from app.routes.shop import shop_bp
    from app.routes.admin import admin_bp
    from app.api.rides import rides_api
    from app.api.deliveries import deliveries_api
    from app.api.food import food_api
    from app.api.parcels import parcels_api
    from app.api.maps import maps_api
    from app.api.payments import payments_api
    from app.api.gps import gps_api

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(passenger_bp, url_prefix="/passenger")
    app.register_blueprint(partner_bp, url_prefix="/partner")
    app.register_blueprint(restaurant_bp, url_prefix="/restaurant")
    app.register_blueprint(shop_bp, url_prefix="/shop")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(rides_api, url_prefix="/api/rides")
    app.register_blueprint(deliveries_api, url_prefix="/api/deliveries")
    app.register_blueprint(food_api, url_prefix="/api/food")
    app.register_blueprint(parcels_api, url_prefix="/api/parcels")
    app.register_blueprint(maps_api, url_prefix="/api/maps")
    app.register_blueprint(payments_api, url_prefix="/api/payments")
    app.register_blueprint(gps_api, url_prefix="/api/gps")

    # SocketIO events
    from app import socket_events  # noqa: F401

    # Context processors
    @app.context_processor
    def inject_globals():
        return {
            "app_name": "LocalGo Nepal",
            "hub_name": "Urlabari",
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("public/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template("public/500.html"), 500

    # CLI helpers
    @app.cli.command("seed")
    def seed_db():
        """Seed initial municipalities, vehicle types, admin user."""
        from app.seed import run_seed
        run_seed()
        print("Database seeded successfully.")

    return app