import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("CINEPULSE_SECRET_KEY", "dev-only-change-me-cinepulse")
DEBUG = os.environ.get("CINEPULSE_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("CINEPULSE_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "channels",
    "common",
    "accounts.apps.AccountsConfig",
    "movies",
    "recommendations",
    "community",
    "notifications",
    "analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "analytics.middleware.ActivityMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cinepulse.urls"
ASGI_APPLICATION = "cinepulse.asgi.application"
WSGI_APPLICATION = "cinepulse.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("CINEPULSE_DB_NAME", "cinepulse"),
        "USER": os.environ.get("CINEPULSE_DB_USER", "cinepulse"),
        "PASSWORD": os.environ.get("CINEPULSE_DB_PASSWORD", "cinepulse"),
        "HOST": os.environ.get("CINEPULSE_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("CINEPULSE_DB_PORT", "5432"),
    }
}

AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CINEPULSE_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardPagination",
    "PAGE_SIZE": 24,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"user": "4000/hour", "anon": "200/hour"},
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=45),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [os.environ.get("CINEPULSE_REDIS_URL", "redis://127.0.0.1:6379/0")]},
    }
}

CELERY_BROKER_URL = os.environ.get("CINEPULSE_REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ALWAYS_EAGER = DEBUG
CELERY_BEAT_SCHEDULE = {
    "refresh-trending": {
        "task": "recommendations.tasks.refresh_trending_scores",
        "schedule": 900.0,
    },
    "rebuild-similarities": {
        "task": "recommendations.tasks.rebuild_movie_similarities",
        "schedule": 3600.0,
    },
    "refresh-taste-profiles": {
        "task": "recommendations.tasks.refresh_all_taste_profiles",
        "schedule": 1800.0,
    },
    "rollup-analytics": {
        "task": "analytics.tasks.rollup_daily_metrics",
        "schedule": 3600.0,
    },
    "notify-watchlist-availability": {
        "task": "notifications.tasks.notify_watchlist_availability",
        "schedule": 1800.0,
    },
}

EMAIL_BACKEND = os.environ.get(
    "CINEPULSE_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("CINEPULSE_FROM_EMAIL", "CinePulse <hello@cinepulse.local>")
FRONTEND_URL = os.environ.get("CINEPULSE_FRONTEND_URL", "http://localhost:5173")

RECOMMENDATION_WEIGHTS = {
    "collaborative": float(os.environ.get("CINEPULSE_W_COLLAB", "0.28")),
    "content": float(os.environ.get("CINEPULSE_W_CONTENT", "0.22")),
    "preferences": float(os.environ.get("CINEPULSE_W_PREF", "0.16")),
    "behavior": float(os.environ.get("CINEPULSE_W_BEHAVIOR", "0.14")),
    "ratings": float(os.environ.get("CINEPULSE_W_RATINGS", "0.08")),
    "popularity": float(os.environ.get("CINEPULSE_W_POP", "0.07")),
    "recency": float(os.environ.get("CINEPULSE_W_RECENCY", "0.05")),
}
