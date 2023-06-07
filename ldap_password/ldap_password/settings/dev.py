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

# AD Connection details
LDAP_URL = env("LDAP_URL")
LDAP_PORT = env("LDAP_PORT")
LDAP_BASE = env("LDAP_BASE")
LDAP_DOMAIN = env("LDAP_DOMAIN")
LDAP_LOGON_DOMAIN_NAME = env("LDAP_LOGON_DOMAIN_NAME")
LDAP_SERVICE_USERNAME = env("LDAP_SERVICE_USERNAME")
LDAP_SERVICE_PASSWORD = env("LDAP_SERVICE_PASSWORD")
