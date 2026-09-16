import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-me-in-production-32chars"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///ride_platform.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Uploads
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf"}

    # Session / security
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Redis / SocketIO
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    SOCKETIO_MESSAGE_QUEUE = os.environ.get("REDIS_URL")

    # GPS
    GPS_RETENTION_DAYS = int(os.environ.get("GPS_RETENTION_DAYS", 7))

    # Platform
    DEFAULT_PLATFORM_FEE = float(os.environ.get("DEFAULT_PLATFORM_FEE", 10))
    MIN_WALLET_BALANCE = float(os.environ.get("MIN_WALLET_BALANCE", 0))
    MAX_NEGATIVE_WALLET = float(os.environ.get("MAX_NEGATIVE_WALLET", -100))

    # Pagination
    ITEMS_PER_PAGE = 20

    # Rate limiting (simple in-memory fallback)
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

    # Service area defaults (admin can override)
    DEFAULT_SERVICE_AREA = "Urlabari"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}