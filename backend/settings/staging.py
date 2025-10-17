from .base import *

DEBUG = False
ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("STAGING_DB_NAME"),
        "USER": os.environ.get("STAGING_DB_USER"),
        "PASSWORD": os.environ.get("STAGING_DB_PASSWORD"),
        "HOST": os.environ.get("STAGING_DB_HOST", "localhost"),
        "PORT": os.environ.get("STAGING_DB_PORT", "5432"),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_SSL = True
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_PORT")