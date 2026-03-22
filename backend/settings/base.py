from dotenv import load_dotenv
import os
from datetime import timedelta
from pathlib import Path
import pytz


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# If settings.py is nested deeper (e.g. backend/settings.py), go one level up again
if (BASE_DIR / "manage.py").exists() is False:
    BASE_DIR = BASE_DIR.parent


TEMPLATE_DIR = BASE_DIR / 'templates'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = ['*']


# Application definition

SYSTEM_DEFINE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    
]


APPLICATION_APPS = [
    'apps.administrator',
    'apps.aso',
    'apps.users'
]


THIRD_PARTIES_APPS = [
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework_simplejwt",
    'drf_yasg',
    'django_filters',
    'health_check',                             # required
    'health_check.db',                          # check database
    'health_check.cache',                       # check cache backend
    'health_check.storage',                     # check media storage
    'health_check.contrib.redis',               # optional, if using Redis
    # 'health_check.contrib.celery', 
]

INSTALLED_APPS = SYSTEM_DEFINE_APPS + APPLICATION_APPS + THIRD_PARTIES_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'utils.Middlewares.log_exceptions.ExceptionLoggingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'utils.Middlewares.threadlocals.CurrentUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'
AUTH_USER_MODEL ='users.User'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'backend.wsgi.application'


DATABASES = {}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_CREDENTIALS = False

# 🔒 CSRF Protection Configuration
# Prevent CSRF attacks while working with CORS
CSRF_TRUSTED_ORIGINS = []  # Explicitly list trusted origins in dev/prod settings
CSRF_COOKIE_SECURE = True  # Only send cookie over HTTPS
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access to read CSRF token (required for forms)
CSRF_COOKIE_SAMESITE = 'Strict'  # Strict same-site policy to prevent cross-site attacks

APPEND_SLASH = False


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    # "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_OBTAIN_SERIALIZER": "authentication.serializers.CustomTokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

REST_FRAMEWORK = {
    "NON_FIELD_ERRORS_KEY": "errors",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 21,
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '20000000/hour',
        'anon': '300000/hour',
        'magic_link': '10000/minute',
        'login': '10000/minute',
        'otp': '5000/minute',
    },
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",

}


SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"',
            'name': 'Authorization',
            'in': 'header',
        },
    },
    'USE_SESSION_AUTH': False,
    'PERSIST_AUTH': True,
}


DRF_STANDARDIZED_ERRORS = {
    "ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True,
    "EXCEPTION_FORMATTER_CLASS": "backend.exception_formatter.ExceptionFormatter",
}

# Common cookie settings
COOKIE_SETTINGS = {
    'path': '/',
    'httponly': False,
    'samesite': 'Lax',  # or 'None' if needed
    'secure': os.getenv('SECURE', 'False').lower() == 'true',
}

# Payment Gateway Keys
PAYSTACK_SECRET_KEY=os.getenv('PAYSTACK_SECRET_KEY')
PAYSTACK_INITIALIZE_URL=os.getenv('PAYSTACK_INITIALIZE_URL')
PAYSTACK_VERIFY_URL=os.getenv('PAYSTACK_VERIFY_URL')

# Flutterwave Gateway Keys
FLUTTERWAVE_SECRET_KEY=os.getenv('FLUTTERWAVE_SECRET_KEY')
FLUTTERWAVE_INITIALIZE_URL=os.getenv('FLUTTERWAVE_INITIALIZE_URL')
FLUTTERWAVE_VERIFY_URL=os.getenv('FLUTTERWAVE_VERIFY_URL')

# Telegram API Configuration
TELEGRAM_API_BASE_URL=os.getenv('TELEGRAM_API_BASE_URL', 'https://api.telegram.org')

# Business Configuration
TERMS_OF_SERVICE_URL=os.getenv('TERMS_OF_SERVICE_URL', 'https://www.google.com/policies/terms/')



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv('REDIS_PORT'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        }
    }
}

CELERY_BROKER_URL = os.getenv('REDIS_PORT')
CELERY_RESULT_BACKEND = os.getenv('REDIS_PORT')
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # Suppress deprecation warning
CELERY_DEFAULT_QUEUE = 'celery'  # Default queue name
CELERY_QUEUES = {
    'celery': {'exchange': 'celery', 'routing_key': 'celery'},
    'default': {'exchange': 'default', 'routing_key': 'default'},
}

# Optional: tune performance
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Lagos'

# Celery Beat Schedule - Daily Tasks
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'send-abandoned-cart-reminders-daily': {
        'task': 'utils.Tasks.scheduled_tasks.send_abandoned_cart_reminders_daily',
        'schedule': crontab(hour=10, minute=0),  # Run daily at 10:00 AM Lagos time
        'options': {'queue': 'celery'}
    },
    'deactivate-expired-feature-flags': {
        'task': 'utils.Tasks.scheduled_tasks.deactivate_expired_feature_flags',
        'schedule': crontab(hour=0, minute=5),  # Run daily at 12:05 AM Lagos time
        'options': {'queue': 'celery'}
    },
}

ADMINS = [
    ('Admin', 'salawulucky08071@gmail.com'),
]
# Log directory
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    # ===== FORMATTERS =====
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d}\n{message}',
            'style': '{',
        },
        'structured': {
            'format': '[{asctime}] [{levelname}] {name}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname}: {message}',
            'style': '{',
        },
    },

    # ===== FILTERS =====
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },

    # ===== HANDLERS =====
    'handlers': {
        'console': {
            'level': 'DEBUG',  # Show everything in console
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'ERROR',  # Only write errors and tracebacks to file
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'app.log'),
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
        },
    },

    # ===== ROOT LOGGER =====
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },

    # ===== DJANGO LOGGER =====
    'loggers': {
        # General Django logs
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },

        # 🔥 Request logger: captures 500s with traceback
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },

        # Silence verbose Celery task registration logs
        'celery.app.utils': {
            'level': 'WARNING',
            'propagate': False,
        },
        'celery.utils.functional': {
            'level': 'WARNING',
            'propagate': False,
        },

        # Optional: your project logger
        'project': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
