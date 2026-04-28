from pathlib import Path

import dj_database_url

from src.brazcar.bootstrap.config import load_app_config

BASE_DIR = Path(__file__).resolve().parents[2]
APP_CONFIG = load_app_config()

SECRET_KEY = APP_CONFIG.secret_key
DEBUG = APP_CONFIG.debug
ALLOWED_HOSTS = APP_CONFIG.allowed_hosts
CSRF_TRUSTED_ORIGINS = APP_CONFIG.csrf_trusted_origins

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_vite",
    "braz_car",
    "users",
    "vehicles",
    "locations",
    "rides",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "braz_car.context_processors.mock_rides_data",
            ],
        },
    },
]

ASGI_APPLICATION = "core.asgi.application"
WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": dj_database_url.parse(APP_CONFIG.database_url, conn_max_age=600),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "users.backends.MultiFieldBackend",
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "assets"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

DJANGO_VITE = {"default": {"dev_mode": DEBUG}}
