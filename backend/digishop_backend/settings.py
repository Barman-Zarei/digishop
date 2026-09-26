from datetime import timedelta
from pathlib import Path
import os

ZARINPAL_MERCHANT_ID = os.environ.get("ZARINPAL_MERCHANT_ID", "")
BACKEND_PUBLIC_URL = os.environ.get("BACKEND_PUBLIC_URL", "https://digishop-grwo.onrender.com")
CURRENCY_IS_TOMAN = True  # prices in DB are Toman; Zarinpal needs Rials (x10)
INTERNAL_CRON_SECRET = os.environ.get("INTERNAL_CRON_SECRET", "")

try:
    from . import config
except ImportError:
    class _EnvConfig:
        SECRET_KEY = os.environ.get("SECRET_KEY")
        DEBUG = os.environ.get("DEBUG", "False") == "True"
        ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
        DB_NAME = os.environ.get("DB_NAME")
        DB_USER = os.environ.get("DB_USER")
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        DB_HOST = os.environ.get("DB_HOST")
        DB_PORT = os.environ.get("DB_PORT", "5432")

    config = _EnvConfig()

BASE_DIR = Path(__file__).resolve().parent.parent


try:
    from . import config
except ImportError:
    config = None


def get_setting(name, default=None):
    if config is not None and hasattr(config, name):
        return getattr(config, name)
    return os.environ.get(name, default)


def get_list_setting(name, default=""):
    value = get_setting(name, default)
    if isinstance(value, list):
        return value
    return [item.strip() for item in str(value).split(",") if item.strip()]


def get_bool_setting(name, default=False):
    value = get_setting(name, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes")


SECRET_KEY = get_setting("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY environment variable is required")

DEBUG = get_bool_setting("DEBUG", False)
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG

ALLOWED_HOSTS = get_list_setting("ALLOWED_HOSTS")

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

if DEBUG:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
else:
    STORAGES = {
        "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": get_setting("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": get_setting("CLOUDINARY_API_KEY"),
    "API_SECRET": get_setting("CLOUDINARY_API_SECRET"),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "EXCEPTION_HANDLER": "digishop_backend.exceptions.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_RATES": {
        "login": "10/hour",
        "register": "5/hour",
    },
}

CORS_ALLOWED_ORIGINS = get_list_setting("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_ALL_ORIGINS = DEBUG
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary_storage",
    "django.contrib.staticfiles",
    "cloudinary",

    "rest_framework",
    "corsheaders",

    "accounts",
    "products",
    "cart",
    "orders",
]

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": get_setting("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": get_setting("CLOUDINARY_API_KEY"),
    "API_SECRET": get_setting("CLOUDINARY_API_SECRET"),
}


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

ROOT_URLCONF = "digishop_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "digishop_backend.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.DB_NAME,
        "USER": config.DB_USER,
        "PASSWORD": config.DB_PASSWORD,
        "HOST": config.DB_HOST,
        "PORT": config.DB_PORT,
        "OPTIONS": {
            "sslmode": "require",
            "sslcert": "",
            "sslkey": "",
            "sslrootcert": "",
        },
    }
}

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

CORS_ALLOW_ALL_ORIGINS = True

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
