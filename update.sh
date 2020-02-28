#!/bin/bash

die() {
  echo "$*" >&2
  exit 1
}

update() {
  git pull --rebase --autostash --stat origin master ||
    die "git pull failed"

  python3 manage.py migrate ||
    die "migration failed"
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

            Update erfolgreich durchgeführt!
EOF
fi
