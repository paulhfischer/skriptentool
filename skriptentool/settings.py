import os

from django.contrib import messages

from skriptentool import config

###############
# DIRECTORIES #
###############
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
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
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "core:catalogue"
LOGOUT_REDIRECT_URL = "core:catalogue"
LOGIN_REDIRECT_URL_FAILURE = "/login/failed"
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
EMAIL_HOST_PASSWORD = ""  # nosec
DEFAULT_FROM_EMAIL = config.SENDER_EMAIL
SERVER_EMAIL = config.SENDER_EMAIL
FINANCE_EMAILS = config.FINANCE_EMAILS
REFERENT_EMAILS = config.REFERENT_EMAILS

##########
# QPILOT #
##########
QPILOT_USERNAME = config.QPILOT_USERNAME
QPILOT_PASSWORD = config.QPILOT_PASSWORD

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
    "mozilla_django_oidc",
    "django_compref_keycloak",
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
    "mozilla_django_oidc.middleware.SessionRefresh",
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
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "secondary",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
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
    "django_compref_keycloak.backend.CompRefKeycloakAuthenticationBackend"
    "django.contrib.auth.backends.ModelBackend",
]

####################
#     KEYCLOAK     #
####################
# realm is either federated-tum.de or fs.tum.de - provided by CompRef
OIDC_OP_AUTHORIZATION_ENDPOINT = "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/auth"
OIDC_OP_TOKEN_ENDPOINT = "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/token"
OIDC_OP_USER_ENDPOINT = "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/userinfo"
OIDC_OP_JWKS_ENDPOINT = "https://auth.fs.tum.de/auth/realms/federated-tum.de/protocol/openid-connect/certs"

# We have OpenID Connect clients configured for testing.
# It is okay to put their secrets to internal git repositories, but not to public ones!
# These test clients only accept http://localhost:8000 as redirect URL.
OIDC_RP_CLIENT_ID = "..."  # provided by CompRef and overwritten for prod deployment
OIDC_RP_CLIENT_SECRET = "..."  # provided by CompRef and overwritten for prod deployment

OIDC_RP_SIGN_ALGO = "RS256"
OIDC_STORE_ID_TOKEN = True
ALLOW_LOGOUT_GET_METHOD = True
OIDC_USERNAME_ALGO = "django_compref_keycloak.backend.generate_username"
OIDC_OP_LOGOUT_URL_METHOD = "django_compref_keycloak.backend.logout_url"

# Allowed federated identity providers
# fs.tum.de accounts
COMPREF_KEYCLOAK_FEDERATED_IDP = {
   # for fs.tum.de realm
   "fs.tum.de-internal": {
      # allow login with fs.tum.de account?
      "enabled": True,
      # restrict login to LDAP groups (empty = allow everyone)
      "active_groups": [],
      # grant staff privileges for these LDAP groups (empty = is_staff is not touched, also not removed!)
      "staff_groups": ["compref", "skripten"],
      # grant superuser privileges for these LDAP groups (empty = is_superuser is not touched, also not removed!)
      "superuser_groups": ["compref", "skripten-admins"],
      # sync LDAP groups to Django groups
      "sync_groups": True,
   },
   # for federated-tum.de realm
   "fs.tum.de": {
      # allow login with fs.tum.de account?
      "enabled": False,
      # restrict login to LDAP groups (empty = allow everyone)
      "active_groups": [],
      # grant staff privileges for these LDAP groups (empty = is_staff is not touched, also not removed!)
      "staff_groups": [],
      # grant superuser privileges for these LDAP groups (empty = is_superuser is not touched, also not removed!)
      "superuser_groups": [],
      # sync LDAP groups to Django groups
      "sync_groups": False,
   },
   "shibboleth.tum.de": {
      "enabled": False,  # allow login with TUM account?
      "active": {
         # affiliations: student, alum, employee (more values possible - these are the important ones)
         # empty = allow everyone and following settings are ignored!
         "affiliations": [],

         # we can restrict the school for students (empty = allow every student)
         # only checked if "student" is included in affiliations
         "org_student": [],

         # we can restrict the school for employees (empty = allow every employee)
         # only checked if "employee" is included in affiliations
         "org_employee": [],
      }
      # note: is_staff/superuser are not touched (= also not set to False)
   }
}
