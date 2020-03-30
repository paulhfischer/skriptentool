#!/bin/bash

# input validation
regex_balance='^[0-9]+(\.[0-9]{1,2})?$'

# create key
secretkey_django=$(LC_ALL=C tr -dc "a-zA-Z0-9!#$%&*+-=?^_" </dev/urandom | head -c64)
echo 'Secret-Key..........: ' "${secretkey_django}"

# user input
while [[ -z "${username_django_admin}" ]]; do read -rp 'DjangoAdmin-Username: ' username_django_admin; done
while [[ -z "${password_django_admin}" ]]; do read -rp 'DjangoAdmin-Password: ' password_django_admin; done
read -rp 'Initial Balance.....: ' initial_balance
until [[ $initial_balance =~ $regex_balance ]]; do echo 'Balance has to be a two-digit decimal!'; read -rp 'Initial Balance.....: ' initial_balance; done

# create project venv
python3 -m venv ./venv
source ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# create config
cat <<EOF >./SkriptenTool/config.py
LOCAL = True
SECRET_KEY = '${secretkey_django}'
DEBUG = True
SSL = False
ALLOWED_HOSTS = []
ADMINS = []
SENDER_EMAIL = ''
DATABASE_PASSWORD = ''
EOF

# initialize project
./manage.py migrate
./manage.py create_groups
./manage.py create_admin "${username_django_admin}" "${password_django_admin}"
./manage.py initial_balance "${initial_balance}" "${username_django_admin}"
