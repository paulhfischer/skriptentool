# Skriptentool der [Fachschaft Mathematik/Physik/Informatik](https://mpi.fs.tum.de) an der [Technischen Universität München](https://www.tum.de)

## Funktionen
- Verwaltung der Skripten
    - Inventar
    - Eigenschaften für Druckaufträge
- Verkaufsvorgang
- Kautionsverwaltung
- Kassenbuch inkl. csv-Export
- Verkaufsschichten
    - Backend-Verwaltung für Finanzer & Referenten
    - Verkäufer sieht eigene Schichten und Status
- Deckblattgenerierung
- Druckauftrag-Generierung

## Setup
- SuperUser erstellen
    - Benutzername: admin
    - Passwort: ***
- Dependencies installieren
    - PDFTK
    - LatexMK
    - pdfinfo
- Anfnags-Kassenstand setzen
    - (Benutzer: admin | Kassenstand: *** | Gezählt: ja | Art: Ersteinlage)
- Gruppen erstellen
    - Finanzer
        - core | Kassenstand | Can view Kassenstand
        - core | Kassenbucheintrag | Can view Kassenbucheintrag
        - core | Kaution | Can view Kaution
        - core | Kautionsschein | Can view Kautionsschein
        - core | Skript | Can view Skript
        - core | Druckkontingent | Can view Druckkontingent
        - core | Verkaufsschicht | Can change Verkaufsschicht
        - core | Verkaufsschicht | Can view Verkaufsschicht
    - Referent
        - core | Autor | Can add Autor
        - core | Autor | Can change Autor
        - core | Autor | Can delete Autor
        - core | Autor | Can view Autor
        - core | Artikel | Can view Artikel
        - core | Kaution | Can add Kaution
        - core | Kaution | Can change Kaution
        - core | Kaution | Can delete Kaution
        - core | Kaution | Can view Kaution
        - core | Kautionsschein | Can change Kautionsschein
        - core | Kautionsschein | Can view Kautionsschein
        - core | Skript | Can add Skript
        - core | Skript | Can change Skript
        - core | Skript | Can delete Skript
        - core | Skript | Can view Skript
        - core | Druckkontingent | Can add Druckkontingent
        - core | Druckkontingent | Can change Druckkontingent
        - core | Druckkontingent | Can delete Druckkontingent
        - core | Druckkontingent | Can view Druckkontingent
        - core | Verkaufsschicht | Can change Verkaufsschicht
        - core | Verkaufsschicht | Can delete Verkaufsschicht
        - core | Verkaufsschicht | Can view Verkaufsschicht
    - Verkäufer

## Feature-Requests
- LDAP-Verbindung
- Errorlog per E-Mail