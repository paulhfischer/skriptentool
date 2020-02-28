import os

# DIRECTORIES #
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COVERS_DIR = os.path.join(BASE_DIR, "media/deckblätter")
COVER_TEMPLATE_FILE = os.path.join(COVERS_DIR, "vorlage/deckblatt.tex")

LECTURE_NOTES_DIR = os.path.join(BASE_DIR, "media/skripten")

ORDERS_DIR = os.path.join(BASE_DIR, "media/skriptenaufträge")
ORDER_TEMPLATE_CONTENT_FILE = os.path.join(ORDERS_DIR, "vorlage/skriptenauftrag.xfdf")
ORDER_TEMPLATE_FORM_FILE = os.path.join(ORDERS_DIR, "vorlage/skriptenauftrag.pdf")

OUTPUT_DIR = os.path.join(BASE_DIR, "media/druck")

# SETTINGS #
SECRET_KEY = 'lul'
DEBUG = True
ALLOWED_HOSTS = ['localhost',
                 '127.0.0.1', ]
ADMINS = [('Paul Fischer', 'paul.fischer@fs.tum.de')]
