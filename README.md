# Skriptentool der [Fachschaft Mathematik/Physik/Informatik](https://mpi.fs.tum.de) an der [Technischen Universität München](https://www.tum.de)

## Funktionen
- Verwaltung der Skripten
    - Inventar
    - Eigenschaften für Druckaufträge
- Verkaufsvorgang
- Kautionsverwaltung
- Kassenbuch inkl. csv-Export

## Feature-Requests
- Deckblattgenerierung
- LDAP-Verbindung
- Druckauftrag erstellen
- Mails an [skripten-owner@fs.tum.de](mailto:skripten-owner@fs.tum.de) bei Fehlern
- Kautionsscheine
    - add boolean refundable to model
    - on_refund:
        - if exists:
            - if refundable: pass
            - else: abort & "kann nicht zurückgegeben werden"
        - else:
            - if referent: popup mit warnung -> falls akzeptiert wird erstattet
- Verkaufsschichten anzeigen
    - Übersicht für Referenten -> Hier dann manuell verkäufe verfizieren bzw. löschen
    - Finanz sieht alle verifizierten Verkäufe und kann diese verbuchen -> checkmark
    - evtl.: verkäufer sieht seine verifizierten verkäufe