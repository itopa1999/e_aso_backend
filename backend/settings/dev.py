from .base import *


DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = ["*"]

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         'NAME': BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}


EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND")
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_FROM = os.environ.get("EMAIL_FROM")

# ✅ CORS Configuration - Explicit whitelist for development only
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5501",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://localhost:5501",
    'http://192.168.0.199:5501',
]

CORS_ALLOW_CREDENTIALS = True  # Allow cookies in development
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# 🔒 CSRF Trusted Origins for development - must match CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:5501",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://localhost:5501",
    "http://192.168.0.199:5501",
]

# Allow local development without HTTPS
CSRF_COOKIE_SECURE = False

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN is not set in environment variables. "
    )

TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
if not TELEGRAM_CHANNEL_ID:
    raise ValueError(
        "TELEGRAM_CHANNEL_ID is not set in environment variables. "
    )

ASO_URL = os.environ.get("ASO_URL")
ADMIN_URL = os.environ.get("ADMIN_URL")
USER_URL = os.environ.get("USER_URL")
BASE_URL =os.getenv('BASE_URL')
BACKEND_BASE_URL =os.getenv('BACKEND_BASE_URL')