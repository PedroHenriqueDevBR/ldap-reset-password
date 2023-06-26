from ldap_password.settings.base import *
import os

# Sobrescrever as configurações base aqui
SECRET_KEY = os.environ.get("APP_SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": "db",
        "PORT": int(os.environ.get("POSTGRES_port") or "5432"),
    }
}

# App metadata
ENTERPRISE_NAME = os.environ.get("ENTERPRISE_NAME")

# AD Connection details
LDAP_URL = os.environ.get("LDAP_URL")
LDAP_PORT = int(os.environ.get("LDAP_PORT") or "636")
LDAP_BASE = os.environ.get("LDAP_BASE")
LDAP_DOMAIN = os.environ.get("LDAP_DOMAIN")
LDAP_LOGON_DOMAIN_NAME = os.environ.get("LDAP_LOGON_DOMAIN_NAME")
LDAP_SERVICE_BIND_DN = os.environ.get("LDAP_SERVICE_BIND_DN")
LDAP_SERVICE_SAM_ACCOUNT_NAME = os.environ.get("LDAP_SERVICE_SAM_ACCOUNT_NAME")
LDAP_SERVICE_PASSWORD = os.environ.get("LDAP_SERVICE_PASSWORD")

# Mail
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT") or "587")
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_DEFAULT_FROM")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
