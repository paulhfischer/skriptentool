# Skriptentool der [Fachschaft Mathematik/Physik/Informatik](https://mpi.fs.tum.de) an der [Technischen Universität München](https://www.tum.de)

Django-Tool für die Verwaltung sowie den Verkauf der Skripten.

## Installation
Siehe Debian10-Projekt.

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