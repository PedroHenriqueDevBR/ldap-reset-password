from ldap_password.settings.base import *
import environ

# Envoiroments load
env = environ.Env()
environ.Env.read_env(".env")

# General settings
SECRET_KEY = env("APP_SECRET_KEY")
DEBUG = True

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "../db.sqlite3"),
        "TEST": {
            "NAME": os.path.join(BASE_DIR, "test_database.sqlite3"),
        },
    }
}

# App metadata
ENTERPRISE_NAME = env("ENTERPRISE_NAME")

# AD Connection details
LDAP_URL = env("LDAP_URL")
LDAP_PORT = int(env("LDAP_PORT"))
LDAP_BASE = env("LDAP_BASE")
LDAP_DOMAIN = env("LDAP_DOMAIN")
LDAP_LOGON_DOMAIN_NAME = env("LDAP_LOGON_DOMAIN_NAME")
LDAP_SERVICE_BIND_DN = env("LDAP_SERVICE_BIND_DN")
LDAP_SERVICE_SAM_ACCOUNT_NAME = env("LDAP_SERVICE_SAM_ACCOUNT_NAME")
LDAP_SERVICE_PASSWORD = env("LDAP_SERVICE_PASSWORD")

# Mail
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = int(env("EMAIL_PORT"))
DEFAULT_FROM_EMAIL = env("EMAIL_DEFAULT_FROM")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
