# Interaktive News-Übersicht im Chat

## Startauftrag für eine neue Aufgabe im Projekt News-Monitor

> News

Dieser Kurzstart ist in `AGENTS.md` hinterlegt und öffnet die bestehende Ansicht mit aktuellem Archivstand und gespeicherten Markierungen, beginnend mit Ungelesen.

## Verbindlicher Ablauf

1. `AGENTS.md` beachten und `python3 monitor.py status` ausführen. Kein Sammellauf allein zum Öffnen der Ansicht.
2. Falls verfügbar, den Skill `visualize:visualize` vollständig lesen. Ohne diesen Skill die CLI-Textansicht verwenden. Die bestehende Gestaltung aus `ui/news-lesepult.template.html` wiederverwenden, nicht neu entwerfen.
3. In das ausdrücklich schreibbare Visualisierungsverzeichnis der aktuellen Aufgabe rendern: `python3 scripts/render_news.py --output /ABSOLUTER/PFAD/DER/AKTUELLEN/AUFGABE/news-lesepult.html`. Ist kein solches Verzeichnis vorhanden, einen erlaubten Ausgabeordner im Projekt verwenden. Keine Schreibrechte auf das Verzeichnis einer früheren Aufgabe voraussetzen.
4. Die erzeugte Datei mit der Visualize-Referenz und `mode: wide` im Chat anzeigen. Das ist eine interaktive Ansicht im Chat, kein gehostetes Dashboard. Keine Veröffentlichung und keinen lokalen Server starten.
5. Zustand aus SQLite ist maßgeblich. Das Auswählen oder Lesen einer Meldung verändert keine Markierung. Widget-Zustand speichert nur Ansicht, Auswahl und Eingabeentwürfe.
6. Vom Nutzer ausgelöste Aktionsnachrichten aus der Ansicht bearbeiten: die angegebene ID und Aktion verwenden, nicht eine abweichende Auswahl einer alten Ansicht. `state ID` mit der ausdrücklichen Anweisung als `--reason` ausführen. Andere Markierungen unverändert lassen. Danach erneut rendern und die Visualize-Referenz ausgeben. Nicht allein wegen einer Widget-Auswahl Änderungen vornehmen.
7. Testliste: Testidee und möglichen Kundennutzen speichern; keine Testergebnisse erfinden. Fragen mit `show ID` und bei Bedarf `passage BELEG_ID` beantworten. Originalstellen mit Zeitmarken erhalten. Quellenbehauptung und eigene Einschätzung trennen.
8. Wenn die Antwort zusätzlich in der Ansicht gewünscht wird, sie bei der betreffenden Meldung ergänzen. Dauerhafte Klärungen außerhalb des Chats im Projekt ablegen und beim erneuten Rendern berücksichtigen. Keine Antwort als Quellenbehauptung ausgeben.

Die Übersicht ist eine Momentaufnahme. Markierungsschaltflächen übergeben einen Auftrag an den Chat; erst dessen erfolgreicher Archivschreibvorgang und erneutes Rendern aktualisieren die Anzeige. Es gibt keine direkte Browserverbindung zur Datenbank.

Alle Daten bleiben in `data/monitor.sqlite3`. Die Vorlage enthält keine Nutzerzustände und keine eingebetteten Archivdaten. `scripts/render_news.py` öffnet die Datenbank ausschließlich lesend und bindet aktuelle Meldungen, Quellen, Markierungen und aktive Probleme ein.

## Mehrere Meldungen als gelesen markieren

Ansichtspräferenz: Werbung einschließlich Eigenwerbung (`ad=ja`) kann ausgeblendet werden. Gespeichert in `ui/news-preferences.json` als `hide_advertising`. Gilt für alle Ansichten, ohne Archivmeldungen oder Markierungen zu verändern. Unklare Werbeeinordnungen bleiben sichtbar. Auf Wunsch durch Ändern dieser Präferenz wieder einblenden.

Checkboxen wählen ungelesene Meldungen aus; „Seite auswählen“ ergänzt die ungelesenen Meldungen der sichtbaren Seite. Die Auswahl bleibt beim Blättern und Filterwechsel erhalten und lässt sich vollständig aufheben. Erst „N als gelesen markieren“ übergibt einen ausdrücklichen Auftrag mit sämtlichen ausgewählten IDs an den Chat. Für jede angegebene ID `state ID --read yes --reason ...` ausführen, andere Markierungen unverändert lassen und anschließend erneut rendern. Die Auswahl allein ändert keinen Archivzustand. Bereits gelesene IDs werden nach dem Aktualisieren aus der Auswahl entfernt.

## Direkter Sprung zur Videostelle

„Im Video ansehen“ öffnet YouTube direkt an der frühesten belegten Zeitmarke des Themas. Bei mehreren Videos gibt es zusätzliche Zeitmarkenlinks unter „Quellen & Belege“. Kein Chatauftrag und keine Markierungsänderung beim Öffnen. Ohne belegte Zeitmarke keinen Zeitsprung erfinden; der normale Quellenlink bleibt verfügbar.
