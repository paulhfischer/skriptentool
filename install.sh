#!/bin/bash

regex='^[0-9]+(\.[0-9]{1,2})?$'
key=$(LC_ALL=C tr -dc "a-z0-9%^&*(-=+)" </dev/urandom | head -c50)

die() {
  echo "$*" >&2
  exit 1
}

install() {
  if [[ $1 =~ $regex ]]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install Django
    git init
    git remote add origin https://gitlab.lrz.de/fischerp/skriptentool.git
    git fetch
    get reset --hard origin/master
    git clean -d -f
    sed -i "" "s|SECRET_KEY.*|SECRET_KEY = '${key}'|" SkriptenTool/config.py
    python3 manage.py migrate
    python3 manage.py createsuperuser
    python3 manage.py create_groups
    python3 manage.py initial_balance "$1"
  else
    die "balance not set or not a decimal"
  fi
}

if update; then
  cat <<EOF
  _____ _         _       _          _______          _
 / ____| |       (_)     | |        |__   __|        | |
| (___ | | ___ __ _ _ __ | |_ ___ _ __ | | ___   ___ | |
 \___ \| |/ / '__| | '_ \| __/ _ \ '_ \| |/ _ \ / _ \| |
 ____) |   <| |  | | |_) | ||  __/ | | | | (_) | (_) | |
|_____/|_|\_\_|  |_| .__/ \__\___|_| |_|_|\___/ \___/|_|
                   | |
                   |_|

         Installation erfolgreich durchgeführt!
EOF
fi
