from pathlib import Path

from dotenv import load_dotenv
import os
from datetime import timedelta

from corsheaders.defaults import default_headers


# =========================================================
# BASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# =========================================================
# ZARINPAL
# =========================================================

ZARINPAL_MERCHANT_ID = os.getenv(
    "ZARINPAL_MERCHANT_ID",
    ""
)

ZARINPAL_REQUEST_URL = os.getenv(
    "ZARINPAL_REQUEST_URL",
    ""
)

ZARINPAL_VERIFY_URL = os.getenv(
    "ZARINPAL_VERIFY_URL",
    ""
)

ZARINPAL_STARTPAY_URL = os.getenv(
    "ZARINPAL_STARTPAY_URL",
    ""
)

ZARINPAL_CALLBACK_URL = os.getenv(
    "ZARINPAL_CALLBACK_URL",
    ""
)

ZARINPAL_SANDBOX = (
    os.getenv(
        "ZARINPAL_SANDBOX",
        "True"
    ).lower()
    == "true"
)


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY"
)

if not SECRET_KEY:
    raise RuntimeError(
        "DJANGO_SECRET_KEY is not configured."
    )


DEBUG = (
    os.getenv(
        "DJANGO_DEBUG",
        "False"
    ).lower()
    == "true"
)


ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]


# =========================================================
# PRODUCTION SECURITY
# =========================================================

SECURE_SSL_REDIRECT = not DEBUG

SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_SECURE = not DEBUG

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

SECURE_REFERRER_POLICY = "same-origin"


if not DEBUG:
    SECURE_HSTS_SECONDS = int(
        os.getenv(
            "DJANGO_SECURE_HSTS_SECONDS",
            "31536000"
        )
    )

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True


# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",

    # Marketplace apps
    "accounts",
    "customers",
    "addresses",
    "cart",
    "categories",
    "inventory",
    "locations",
    "numerology_app",
    "order_history",
    "orders",
    "payments",
    "products",
    "sellers",
    "shipping",
    "shops",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# CORS
# =========================================================

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        (
            "http://localhost:5173,"
            "http://127.0.0.1:5173,"
            "http://localhost:5174,"
            "http://127.0.0.1:5174"
        )
    ).split(",")
    if origin.strip()
]

CORS_ALLOW_HEADERS = [
    *default_headers,
    "idempotency-key",
]


# =========================================================
# CSRF
# =========================================================

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        ""
    ).split(",")
    if origin.strip()
]


# =========================================================
# FRONTEND
# =========================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)


# =========================================================
# URLS / WSGI
# =========================================================

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django."
            "DjangoTemplates"
        ),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# =========================================================
# DATABASE
# =========================================================

# Development database: SQLite
# PostgreSQL will be configured for production later.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC / MEDIA
# =========================================================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"

MEDIA_ROOT = BASE_DIR / "media"


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# DJANGO REST FRAMEWORK
# =========================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication."
        "JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}


# =========================================================
# SIMPLE JWT
# =========================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,

    "AUTH_HEADER_TYPES": ("Bearer",),
}


# =========================================================
# SMS
# =========================================================

SMS_PROVIDER = (
    "customers.sms.development.DevelopmentSMSProvider"
)

SMS_SHOW_DEVELOPMENT_CODE = DEBUG


# =========================================================
# PAYMENT
# =========================================================

PAYMENT_EXPIRATION_MINUTES = 15