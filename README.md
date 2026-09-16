# LocalGo Nepal – Local Mobility, Ride, Food, Parcel & Document Delivery

Production-oriented multi-service platform focused on **Urlabari** (hub) and surrounding municipalities in **Morang** and **Jhapa**, Nepal.

## Features

- **Rides**: Bike Taxi, Car, Auto, Safari, E-Rickshaw, Bicycle (configurable document rules)
- **Food delivery** with restaurant dashboard & order lifecycle
- **Parcel & Document** delivery with tracking
- **Local shop** delivery
- **Partner system** (multi-service drivers) with verification & wallet
- **Live GPS** via browser Geolocation + Flask-SocketIO
- **Server-side fare engine**, platform fees, partner wallet
- **Direct QR payment** recording (eSewa / Khalti / Bank QR) – gateways pluggable later
- **Admin**: municipalities, routes, vehicle types, partners, rides, settings
- **PWA**: installable without Play Store / App Store
- **Stack**: Flask, SQLAlchemy, PostgreSQL/SQLite, Jinja2, Leaflet, Vanilla JS

## Quick start (development)

```bash
cd ride-platform
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env – for local demo you can leave DATABASE_URL unset (uses SQLite)

export FLASK_APP=run.py
flask db init          # first time only
flask db migrate -m "initial"
flask db upgrade
flask seed             # municipalities, vehicle types, admin user

python run.py
```

Open http://127.0.0.1:5000

**Default admin**

- Phone: `9800000000`
- Password: `admin123`

## Service area (seeded)

| Municipality | District |
|---|---|
| Urlabari Municipality | Morang |
| Pathari-Shanishchare Municipality | Morang |
| Ratuwamai Municipality | Morang |
| Kanepokhari Rural Municipality | Morang |
| Miklajung Rural Municipality | Morang |
| Damak Municipality | Jhapa |

Admin can add unlimited municipalities, wards, areas, and routes.

## Project layout

See `app/` for models, routes, api, services, templates, static.

## Production notes

- Set strong `SECRET_KEY` and `DATABASE_URL` (Neon PostgreSQL recommended).
- Use `gunicorn` + `eventlet` or `gevent` for SocketIO.
- Configure HTTPS for secure cookies and PWA.
- Vehicle document requirements are **admin-configurable** per vehicle type (bicycle defaults: no plate/registration/license).
- All fares, fees, wallet mutations are **server-side**.

## License

Proprietary – for the LocalGo project.