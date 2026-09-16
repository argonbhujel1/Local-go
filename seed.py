"""Seed initial data for Urlabari hub and surrounding service areas."""
from app import db
from app.models.user import User, Role
from app.models.vehicle import VehicleType
from app.models.location import Municipality
from app.models.route import Route
from app.models.system import SystemSetting
from app.services.wallet_service import WalletService


def run_seed():
    # Roles
    roles = [
        ("superadmin", "Full system access"),
        ("admin", "Admin dashboard"),
        ("passenger", "Customer / passenger"),
        ("partner", "Driver / delivery partner"),
        ("restaurant", "Restaurant owner"),
        ("shop", "Shop owner"),
    ]
    for name, desc in roles:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name, description=desc))
    db.session.commit()

    # Vehicle types – bicycle has relaxed requirements
    vehicles = [
        {
            "name": "Bike Taxi",
            "code": "bike",
            "icon": "🏍",
            "requires_number_plate": True,
            "requires_registration": True,
            "requires_license": True,
            "base_fare": 30,
            "per_km_fare": 15,
            "per_minute_fare": 1,
            "minimum_fare": 50,
            "platform_fee": 10,
        },
        {
            "name": "Car / Taxi",
            "code": "car",
            "icon": "🚗",
            "requires_number_plate": True,
            "requires_registration": True,
            "requires_license": True,
            "base_fare": 80,
            "per_km_fare": 25,
            "per_minute_fare": 2,
            "minimum_fare": 120,
            "platform_fee": 20,
        },
        {
            "name": "Auto Rickshaw",
            "code": "auto",
            "icon": "🛺",
            "requires_number_plate": True,
            "requires_registration": True,
            "requires_license": True,
            "base_fare": 40,
            "per_km_fare": 18,
            "per_minute_fare": 1.5,
            "minimum_fare": 60,
            "platform_fee": 12,
        },
        {
            "name": "Safari",
            "code": "safari",
            "icon": "🚜",
            "requires_number_plate": True,
            "requires_registration": True,
            "requires_license": True,
            "base_fare": 100,
            "per_km_fare": 30,
            "per_minute_fare": 2,
            "minimum_fare": 150,
            "platform_fee": 25,
        },
        {
            "name": "E-Rickshaw",
            "code": "erickshaw",
            "icon": "🛺",
            "requires_number_plate": True,
            "requires_registration": False,
            "requires_license": True,
            "base_fare": 35,
            "per_km_fare": 12,
            "per_minute_fare": 1,
            "minimum_fare": 50,
            "platform_fee": 10,
        },
        {
            "name": "Bicycle",
            "code": "bicycle",
            "icon": "🚲",
            "requires_number_plate": False,
            "requires_registration": False,
            "requires_license": False,
            "requires_photo": True,
            "base_fare": 20,
            "per_km_fare": 8,
            "per_minute_fare": 0.5,
            "minimum_fare": 30,
            "platform_fee": 5,
        },
    ]
    for v in vehicles:
        if not VehicleType.query.filter_by(code=v["code"]).first():
            db.session.add(VehicleType(**v))
    db.session.commit()

    # Municipalities – Morang & Jhapa service area
    munis = [
        {"name": "Urlabari Municipality", "type": "Municipality", "district": "Morang", "latitude": 26.6635, "longitude": 87.6025},
        {"name": "Pathari-Shanishchare Municipality", "type": "Municipality", "district": "Morang", "latitude": 26.6500, "longitude": 87.5500},
        {"name": "Ratuwamai Municipality", "type": "Municipality", "district": "Morang", "latitude": 26.5800, "longitude": 87.6200},
        {"name": "Kanepokhari Rural Municipality", "type": "Rural Municipality", "district": "Morang", "latitude": 26.7000, "longitude": 87.5800},
        {"name": "Miklajung Rural Municipality", "type": "Rural Municipality", "district": "Morang", "latitude": 26.7200, "longitude": 87.6500},
        {"name": "Damak Municipality", "type": "Municipality", "district": "Jhapa", "latitude": 26.6615, "longitude": 87.6975},
    ]
    for m in munis:
        if not Municipality.query.filter_by(name=m["name"]).first():
            db.session.add(Municipality(**m, province="Koshi", is_serviceable=True))
    db.session.commit()

    # Sample routes from Urlabari
    urlabari = Municipality.query.filter(Municipality.name.like("%Urlabari%")).first()
    if urlabari:
        others = Municipality.query.filter(Municipality.id != urlabari.id).all()
        for o in others:
            name = f"Urlabari ↔ {o.name.split()[0]}"
            if not Route.query.filter_by(name=name).first():
                db.session.add(Route(
                    name=name,
                    start_municipality_id=urlabari.id,
                    end_municipality_id=o.id,
                    distance_km=12,
                    estimated_minutes=25,
                    base_fare=50,
                    per_km_fare=15,
                    platform_fee=15,
                    is_active=True,
                ))
        # Local
        if not Route.query.filter_by(name="Urlabari Local").first():
            db.session.add(Route(
                name="Urlabari Local",
                start_municipality_id=urlabari.id,
                end_municipality_id=urlabari.id,
                distance_km=3,
                estimated_minutes=10,
                is_local=True,
                base_fare=30,
                per_km_fare=12,
                platform_fee=10,
            ))
    db.session.commit()

    # Admin user
    if not User.query.filter_by(phone="9800000000").first():
        admin = User(phone="9800000000", full_name="System Admin", email="admin@localgo.np")
        admin.set_password("admin123")
        admin.is_verified = True
        admin.generate_referral_code()
        role = Role.query.filter_by(name="superadmin").first()
        if role:
            admin.roles.append(role)
        db.session.add(admin)
        db.session.commit()
        WalletService.get_or_create_user_wallet(admin.id)

    # System settings
    defaults = [
        ("app_name", "LocalGo Nepal", "string"),
        ("hub_name", "Urlabari", "string"),
        ("default_platform_fee", "10", "float"),
        ("min_wallet_balance", "0", "float"),
        ("gps_retention_days", "7", "int"),
        ("support_phone", "9800000001", "string"),
    ]
    for key, val, vtype in defaults:
        if not SystemSetting.query.filter_by(key=key).first():
            db.session.add(SystemSetting(key=key, value=val, value_type=vtype))
    db.session.commit()