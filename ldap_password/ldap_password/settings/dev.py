from ldap_password.settings.base import *
from decouple import config

# Envoiroments load

# General settings
SECRET_KEY = config("APP_SECRET_KEY")
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
ENTERPRISE_NAME = config("ENTERPRISE_NAME")
SUCCESS_REDIRECT_URL = config("SUCCESS_REDIRECT_URL")

# AD Connection details
LDAP_URL = config("LDAP_URL")
LDAP_PORT = int(config("LDAP_PORT"))
LDAP_BASE = config("LDAP_BASE")
LDAP_DOMAIN = config("LDAP_DOMAIN")
LDAP_LOGON_DOMAIN_NAME = config("LDAP_LOGON_DOMAIN_NAME")
LDAP_SERVICE_BIND_DN = config("LDAP_SERVICE_BIND_DN")
LDAP_SERVICE_SAM_ACCOUNT_NAME = config("LDAP_SERVICE_SAM_ACCOUNT_NAME")
LDAP_SERVICE_PASSWORD = config("LDAP_SERVICE_PASSWORD")

# Mail
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = int(config("EMAIL_PORT"))
DEFAULT_FROM_EMAIL = config("EMAIL_DEFAULT_FROM")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
