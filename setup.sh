#!/bin/bash

# create key and password
secret_key=$(LC_ALL=C tr -dc "a-zA-Z0-9;#$%&()*+,-./:;<=>?[]^_´{|}~" </dev/urandom | head -c50)
echo 'Secret-Key..........: ' "${secret_key}"

# set config
cat <<EOF >./SkriptenTool/config.py
LOCAL = True
SECRET_KEY = '${secret_key}'
DEBUG = True
SSL = False
ALLOWED_HOSTS = []
ADMINS = []
SENDER_EMAIL = ''
DATABASE_PASSWORD = ''

EOF
