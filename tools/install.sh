#!/bin/bash

regex='^[0-9]+(\.[0-9]{1,2})?$'
key=$(LC_ALL=C tr -dc "a-z0-9%^&*(-=+)" </dev/urandom | head -c50)

die() {
  echo "$*" >&2
  exit 1
}

install() {
  echo "Anfangskassenstand eingeben (z.B. 420.00):"
  read -r balance
  if [[ $balance =~ $regex ]]; then
    python3 -m venv venv ||
      die "venv creation failed"

    source venv/bin/activate ||
      die "venv actvation failed"

    pip install --upgrade pip ||
      die "pip upgrade failed"

    pip install Django ||
      die "django installation failed"

    git init ||
      die "git initialisation failed"

    git remote add origin https://gitlab.lrz.de/fischerp/skriptentool.git ||
      die "git add repository failed"

    git fetch ||
      die "git fetch failed"

    get reset --hard origin/master ||
      die "git reset failed"

    git clean -d -f ||
      die "git cleanup failed"

    sed -i "" "s|SECRET_KEY.*|SECRET_KEY = '${key}'|" SkriptenTool/config.py ||
      die "secret-key write failed"

    python3 manage.py migrate ||
      die "migration failed"

    python3 manage.py createsuperuser ||
      die "superuser creation failed"

    python3 manage.py create_groups ||
      die "group creation failed"

    python3 manage.py initial_balance "$balance" ||
      die "setting initial balance failed"
  else
    die "balance not set or not a decimal"
  fi
}

if install; then
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
