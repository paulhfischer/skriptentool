import os

from skriptentool import config

###############
# DIRECTORIES #
###############
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

COVERS_DIR = os.path.join(MEDIA_ROOT, "deckblätter")
COVER_TEMPLATE_FILE = os.path.join(COVERS_DIR, "vorlage/deckblatt.tex")

LECTURE_NOTES_DIR = os.path.join(MEDIA_ROOT, "skripten")

ORDERS_DIR = os.path.join(MEDIA_ROOT, "skriptenaufträge")
ORDER_TEMPLATE_CONTENT_FILE = os.path.join(ORDERS_DIR, "vorlage/skriptenauftrag.xfdf")
ORDER_TEMPLATE_FORM_FILE = os.path.join(ORDERS_DIR, "vorlage/skriptenauftrag.pdf")

OUTPUT_DIR = os.path.join(MEDIA_ROOT, "druck")

########
# URLS #
########
ROOT_URLCONF = "skriptentool.urls"
STATIC_URL = "/static/"
LOGIN_REDIRECT_URL = "core:catalogue"
LOGOUT_REDIRECT_URL = "core:catalogue"
MEDIA_URL = "/media/"

########
# MAIL #
########
if config.LOCAL:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = config.SENDER_EMAIL
SERVER_EMAIL = config.SENDER_EMAIL

############
# SETTINGS #
############
SECRET_KEY = config.SECRET_KEY
DEBUG = config.DEBUG
ALLOWED_HOSTS = ["localhost"] + config.ALLOWED_HOSTS
ADMINS = config.ADMINS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
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
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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
WSGI_APPLICATION = "skriptentool.wsgi.application"
if config.LOCAL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "skriptentool",
            "USER": "skriptentool",
            "PASSWORD": config.DATABASE_PASSWORD,
            "HOST": "localhost",
            "PORT": "",
        },
    }
SECURE_REFERRER_POLICY = "origin"
if config.SSL:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

###############
# TRANSLATION #
###############
LANGUAGE_CODE = "de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ("de", "German"),
    ("en", "English"),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale/")]
MIDDLEWARE += ["django.middleware.locale.LocaleMiddleware"]

####################
# AUTHENTIFICATION #
####################
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "core.User"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
