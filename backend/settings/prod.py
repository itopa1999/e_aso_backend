from .base import *

DEBUG = False
ALLOWED_HOSTS = ["51.21.127.109"]

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


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_SSL = True
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_USER")


# Secure cookies & HTTPS enforcement
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_REFERRER_POLICY = "same-origin"


PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

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