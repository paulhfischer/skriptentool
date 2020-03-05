# Skriptentool der [Fachschaft Mathematik/Physik/Informatik](https://mpi.fs.tum.de) an der [Technischen Universität München](https://www.tum.de)

Django-Tool für die Verwaltung sowie den Verkauf der Skripten.

## Installation
Siehe Debian10-Projekt.
### Debian Buster
- `python3.7-venv`
- `nginx`
- `postgresql`
- `pdftk`
- `texlive-full`
- `poppler-utils`
- `latexmk`
- `curl`

### Datenbank
Die Bearbeitung der Datenbank wird mit `sudo -u postgres psql` gestartet und mit `\q` beendet.
```postgresql
CREATE DATABASE skriptentool;
CREATE USER django WITH PASSWORD '<password>';
ALTER ROLE django SET client_encoding TO 'utf8';
ALTER ROLE django SET default_transaction_isolation TO 'read committed';
ALTER ROLE django SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE skriptentool TO django;
```

### Dateien und Umgebung
Der `<private-token>` lässt sich in den [Einstellungen](https://gitlab.lrz.de/profile/personal_access_tokens) erstellen und benötigt die Berechtigung
`read_repository`.
```shell script
adduser django
mkdir /home/django/skriptentool
cd /home/django/skriptentool
sh -c "$(curl -fsSL https://gitlab.lrz.de/api/v4/projects/50647/repository/files/tools%2Finstall%2Esh/raw?ref=master&private_token=<private-token>)"
```

### Gunicorn
#### `/etc/systemd/system/gunicorn.socket`:
```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

#### `/etc/systemd/system/gunicorn.service`:
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/skriptentool
ExecStart=/home/django/skriptentool/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          SkriptenTool.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### Starten
```shell script
systemctl enable gunicorn
systemctl start gunicorn
```

### Nginx
#### `/etc/nginx/sites-available/skriptentool.fischerp.net`:
```
server {
        listen 80;
        server_name skriptentool.fischerp.net;
        return 301 https://$host$request_uri;
}

server{
        listen 443 ssl;
        server_name skriptentool.fischerp.net;

        ssl_certificate /etc/letsencrypt/live/fischerp.net/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/fischerp.net/privkey.pem;
        include /etc/letsencrypt/options-ssl-nginx.conf;
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

         location = /favicon.ico { access_log off; log_not_found off; }
         location /static/ {
                 root /home/django/skriptentool;
         }
         location /media/ {
                 root /home/django/skriptentool;
         }
         location / {
                 include proxy_params;
                 proxy_pass http://unix:/run/gunicorn.sock;
         }
}
```

#### Aktivieren
```shell script
ln -s /etc/nginx/sites-available/skriptentool.fischerp.net /etc/nginx/sites-enabled
```

#### Starten
```shell script
systemctl daemon-reload
systemctl restart nginx
```

## Logs
```shell script
journalctl -u gunicorn
```
```shell script
journalctl -u nginx
```

## Update
Der `<private-token>` lässt sich in den [Einstellungen](https://gitlab.lrz.de/profile/personal_access_tokens) erstellen und benötigt die Berechtigung
`read_repository`.
```shell script
sh -c "$(curl -fsSL https://gitlab.lrz.de/api/v4/projects/50647/repository/files/tools%2Fupdate%2Esh/raw?ref=master&private_token=<private-token>)"
```

## Bedienungsanleitung
Wird noch von den Skriptenreferenten erstellt.