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
AD_URL = env("AD_URL")
AD_PORT = env("AD_PORT")
AD_BASE = env("AD_BASE")
AD_SERVICE_USERNAME = env("AD_SERVICE_USERNAME")
AD_SERVICE_PASSWORD = env("AD_SERVICE_PASSWORD")
