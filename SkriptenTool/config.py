import os

from SkriptenTool import settings

# DIRECTORIES #
COVERS_DIR = os.path.join(settings.MEDIA_ROOT, "deckblätter")
COVER_TEMPLATE_FILE = os.path.join(COVERS_DIR, "vorlage/deckblatt.tex")

LECTURE_NOTES_DIR = os.path.join(settings.MEDIA_ROOT, "skripten")

ORDERS_DIR = os.path.join(settings.MEDIA_ROOT, "skriptenaufträge")
ORDER_TEMPLATE_CONTENT_FILE = os.path.join(ORDERS_DIR, "vorlage/skriptenauftrag.xfdf")
ORDER_TEMPLATE_FORM_FILE = os.path.join(ORDERS_DIR, "vorlage/skriptenauftrag.pdf")

OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, "druck")

# SETTINGS #
LOCAL = True
SECRET_KEY = ''
DEBUG = True
SSL = True
ALLOWED_HOSTS = ['localhost', ]
ADMINS = [('Paul Fischer', 'paul.fischer@fs.tum.de')]
if LOCAL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(settings.BASE_DIR, 'db.sqlite3'),
        }}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'skriptentool',
            'USER': 'django',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }}
