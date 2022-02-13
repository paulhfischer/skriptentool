# [Skriptentool](https://skripten.mpi.fs.tum.de/) der [Fachschaft Mathematik/Physik/Informatik](https://mpi.fs.tum.de)

## Konfiguration

Die Datei `config.py` muss im Ordner `skriptentool` angelegt werden:

```python
LOCAL = # Boolean, die angibt, ob das Tool lokal genutzt werden soll
SECRET_KEY = # Secret Key (https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key)
DEBUG = # Boolean, die Angibt, ob sich das Tool im Debug-Modus befinden soll (https://docs.djangoproject.com/en/2.2/ref/settings/#debug)
SSL = # Boolean, die angibt, ob das Tool über SSL erreicht werden soll (andere Verbindungen werden blockiert)
ALLOWED_HOSTS = # Liste der FQDNs, über die das Tool erreicht werden soll (https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts)
ADMINS = # Liste mit Personen, die E-Mail Benachrichtigungen bei Fehlern erhalten sollen (https://docs.djangoproject.com/en/2.2/ref/settings/#admins)
SENDER_EMAIL = # E-Mail Adresse, über die das Tool Benachrichtigungen versendet (https://docs.djangoproject.com/en/2.2/ref/settings/#default-from-email)
FINANCE_EMAILS = # Liste mit E-Mail Adressen, die Benachrichtigungen erhalten sollen, die Finanzer betreffen
REFERENT_EMAILS = # Liste mit E-Mail Adressen, die Benachrichtigungen erhalten sollen, die Referenten betreffen
DATABASE_PASSWORD = # Datenbankpasswort (Benutzername: skriptentool) (https://docs.djangoproject.com/en/2.2/ref/settings/#password)
QPILOT_USERNAME = # Benutzername des Druckkontingent-Accounts
QPILOT_PASSWORD = # Passwort des Druckkontingent-Accounts
```

## Bedienungsanleitung

### Verkäufer

-   Zu Beginn und am Ende eines Verkaufs muss man den Kassenstand mit seiner Zählung abgleichen,
    evtl. korrigieren und bestätigen.
-   Artikel können mithilfe des Scanners zum Warenkorb hinzugefügt werden, sollte man sich vertan
    haben können diese nach Auswahl des `-`-Feldes durch erneutes Scannen aus dem Warenkorb entfernt
    werden.
-   Beim Einscannen von Protokollen erscheint eine Warnung, dass ein Kautionsschein benötigt wird,
    den man dann direkt hinzufügen kann. Die zugehörige Kautionsscheinnummer wird über dem
    "Kassenzettel" angezeigt.
-   Zum Erstatten von Kautionen muss der zugehörige Barcode (unter den Druckkontingenten) nach
    Auswahl des `-`-Feldes gescannt werden und die Kautionsscheinnummer im Pop-up eingegeben werden.
    **Sollte das Tool den Kautionsschein nicht akzeptieren, bitte an einen Skriptenreferenten
    wenden.**
-   Unter `Verkaufsschichten` kann eingesehen werden, wann man verkauft hat, ob ein Verkauf von den
    Referenten bestätigt wurde und ob das Getränkeguthaben gebucht wurde. Üblicherweise geschieht
    dies erst nach Ende eines Semesters. Sollte etwas nicht passen, bitte an einen
    Skriptenreferenten wenden.

### Referent

-   Zusätzlich zu den Funktionen eines normalen Verkäufers hat man als Referent noch Zugriff auf
    `Verwaltung` und die Möglichkeit, Kautionsscheine zurückzunehmen, deren Kautionsscheinnummer
    nicht im System hinterlegt ist.
-   In der `Verwaltung` gibt es unterschiedliche Objekte, die bearbeitet oder angesehen werden
    können:

**Autoren**

-   Hier findet sich eine Auflistung aller Autoren inkulsive ihrer E-Mail-Adressen.
-   Es können neue Autoren hinzugefügt werden und alte bearbeitet bzw. gelöscht werden.

**Druckkontingente**

-   Hier können die einzelnen Druckkontingente mit jeweils EAN, Seitenzahl und Preis
    bearbeitet/hinzugefügt/gelöscht werden.

**Kautionen**

-   Hier können die einzelnen Kautions**arten** mit jeweils EAN, Name und Preis
    geändert/erstellt/gelöscht werden.
-   Es gibt auch die Möglichkeit, bei der Erstellung eines Skripts direkt eine neue Kautionsart
    hinzuzufügen.

**Kautionsscheine**

-   Hier findet sich eine Auflistung aller verkauften und zurückgenommenen Kautionsscheine mit
    Kautionsscheinnummer, Verkaufszeitpunkt, Rückgabezeitpunkt und dem Attribut `erstattbar`. Bei
    Auswahl eines Kautionsscheins kann zusätzlich eingesehen werden, welcher Benutzer diesen
    verkauft bzw. erstattet hat.
-   Es kann nur das Attribut `erstattbar` bearbeitet werden, der Rest geschieht automatisch während
    des Verkaufs. Diese Eigenschaft sollte nur von dem Referenten geändert werden, der auch das
    Protokoll bestätigt.
-   Wenn ein Referent einen Kautionsschein zurücknimmt, dessen Kautionsscheinnummer nicht im System
    hinterlegt war, so erscheint dieser nur mit Rückgabezeitpunkt in der Liste.

**Skripten**

-   Die meisten Eigenschaften sind selbsterklärend, daher wird hier nur auf Besonderheiten
    eingegangen.
-   Bei den Eigenschaften `Autor` und `Kaution` können bereits vorhandene Optionen ausgewählt bzw.
    bearbeitet werden und neue hinzugefügt werden.
-   Gilt ein Skript für nur ein Semester, so muss das Feld `Semester (bis)` leer gelassen werden.
-   Das Feld `Kommentar für Druck` dient dazu, Druckeinstellungen zu dokumentieren, wenn Skripte
    beispielsweise mit Versatz oder skaliert gedruckt werden müssen. Ein einfaches "passt so" ist
    auch hilfreich, da sich so das Probeexemplar gespart werden kann.
-   Deckblätter (`/group/skripten/deckblätter`) werden automatisch generiert und vor das
    hochgeladene Skript angefügt. Das finale Druckprodukt wird automatisch in den Druckordner gelegt
    (`/group/druck/eingang/skripten`).
-   Skriptenaufträge (`/group/skripten/aufträge`), bei denen alle Daten aus den Druckeinstellungen
    übernommen werden, werden autmatisch generiert. **In diesen muss bei einer Bestellung noch die
    Anzahl der Skripte sowie der Auftraggeber nachgetragen werden!**

**Verkaufsschichten**

-   Hier findet sich eine Auflistung aller Verkaufsschichten mit Verkäufer, Startzeitpunkt,
    Endzeitpunkt und den Attributen `überprüft` sowie `bezahlt`.
-   Die Eigenschaft `bezahlt` wird von dem Finanzreferat verwaltet.
-   Skriptenreferenten müssen entscheiden, ob sie Verkaufsschichten als `überprüft` markieren oder
    löschen. Beispiele für zu löschende Verkäufe sind z. B. solche, die zu merkwürdigen Zeiten
    stattfinden oder solche, die nur wenige Minuten dauern. Die Entscheidung liegt im Ermessen der
    Skriptenreferenten.
