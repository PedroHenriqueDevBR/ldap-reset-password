from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = ""
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    # Django libs
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3° libs
    "crispy_forms",
    # Apps
    "apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ldap_password.urls"

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

WSGI_APPLICATION = "ldap_password.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# App metadata
ENTERPRISE_NAME = ""

# AD Connection details
LDAP_URL = ""
LDAP_PORT = 0
LDAP_BASE = ""
LDAP_DOMAIN = ""
LDAP_LOGON_DOMAIN_NAME = ""
LDAP_SERVICE_BIND_DN = ""
LDAP_SERVICE_SAM_ACCOUNT_NAME = ""
LDAP_SERVICE_PASSWORD = ""

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 5  # 5 minutes
SESSION_SAVE_EVERY_REQUEST = True


# Mail
EMAIL_HOST = ""
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Password validation
n1 = "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
n2 = "django.contrib.auth.password_validation.MinimumLengthValidator"
n3 = "django.contrib.auth.password_validation.CommonPasswordValidator"
n4 = "django.contrib.auth.password_validation.NumericPasswordValidator"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": n1},
    {"NAME": n2},
    {"NAME": n3},
    {"NAME": n4},
]

# Meta settings
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Fortaleza"
USE_I18N = True
USE_TZ = True

# Static and Media settings
STATIC_URL = "static/"
STATIC_ROOT = os.path.join("staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join("mediafiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s; %(asctime)s; %(module)s; %(process)d; \
                %(thread)d; %(message)s"
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django_auth_ldap": {"level": "ERROR", "handlers": ["console"]},
    },
}
