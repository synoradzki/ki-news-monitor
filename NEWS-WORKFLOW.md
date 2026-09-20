# Interaktive News-Übersicht im Chat

## Startauftrag für eine neue Aufgabe im Projekt News-Monitor

> News

Dieser Kurzstart ist in `AGENTS.md` hinterlegt und zeigt den aktuellen Archivstand mit gespeicherten Markierungen, beginnend mit Ungelesen. Voraussetzung: eingerichteter lokaler Projektordner mit `config.json`; für vorhandene Nachrichten auch das zugehörige Archiv.

Die Codex Desktop App übersetzt Chataufträge in Aufrufe der Python-Skripte. `monitor.py` liest und schreibt SQLite; der Chatverlauf ist kein Archiv. Die interaktive Darstellung benötigt zusätzlich den Visualize-Skill und eine Host-Integration für Aktionsnachrichten. Fehlt eine dieser Voraussetzungen, Nachrichten als Text im Chat darstellen und die folgenden Rendering-Schritte überspringen. Normale Chataufträge zum Vertiefen und Markieren bleiben möglich.

## Verbindlicher Ablauf

1. `AGENTS.md` beachten und `python3 monitor.py status` ausführen. Kein Sammellauf allein zum Öffnen der Ansicht.
2. Falls verfügbar, den Skill `visualize:visualize` vollständig lesen. Ohne diesen Skill oder ohne Host-Integration `list --filter unread --limit 10` und bei Bedarf `show ID` aufrufen; Ergebnisse im Chat als Text darstellen. Je Meldung: **News** (Titel und Zusammenfassung), **Kanal** (Quelle mit Beitragslink), **Datum** (Veröffentlichungsdatum DD.MM.YYYY in Europe/Berlin); eigene Einschätzung separat. Dann Schritte 3–4 überspringen. Die bestehende Gestaltung aus `ui/news-lesepult.template.html` wiederverwenden, nicht neu entwerfen.
3. In das ausdrücklich schreibbare Visualisierungsverzeichnis der aktuellen Aufgabe rendern: `python3 scripts/render_news.py --output /ABSOLUTER/PFAD/DER/AKTUELLEN/AUFGABE/news-lesepult.html`. Ist kein solches Verzeichnis vorhanden, einen erlaubten Ausgabeordner im Projekt verwenden. Keine Schreibrechte auf das Verzeichnis einer früheren Aufgabe voraussetzen.
4. Die erzeugte Datei mit der Visualize-Referenz und `mode: wide` im Chat anzeigen. Das ist eine interaktive Ansicht im Chat, kein gehostetes Dashboard. Keine Veröffentlichung und keinen lokalen Server starten.
5. Zustand aus SQLite ist maßgeblich. Das Auswählen oder Lesen einer Meldung verändert keine Markierung. Widget-Zustand speichert nur Ansicht, Auswahl und Eingabeentwürfe.
6. Vom Nutzer ausgelöste Aktionsnachrichten aus der Ansicht bearbeiten: die angegebene ID und Aktion verwenden, nicht eine abweichende Auswahl einer alten Ansicht. `state ID` mit der ausdrücklichen Anweisung als `--reason` ausführen. Andere Markierungen unverändert lassen. Danach die verwendete Darstellung aktualisieren: erneut rendern oder den Zustand als Text bestätigen. Nicht allein wegen einer Widget-Auswahl Änderungen vornehmen.
7. Testliste: Testidee und möglichen Kundennutzen speichern; keine Testergebnisse erfinden. Fragen mit `show ID` und bei Bedarf `passage BELEG_ID` beantworten. Originalstellen mit Zeitmarken erhalten. Quellenbehauptung und eigene Einschätzung trennen.
8. Wenn die Antwort zusätzlich in der Ansicht gewünscht wird, sie bei der betreffenden Meldung ergänzen. Dauerhafte Klärungen außerhalb des Chats im Projekt ablegen und beim erneuten Rendern berücksichtigen. Keine Antwort als Quellenbehauptung ausgeben.

Die Übersicht ist eine Momentaufnahme. Markierungsschaltflächen übergeben einen Auftrag an den Chat; erst dessen erfolgreicher Archivschreibvorgang und erneutes Rendern aktualisieren die Anzeige. Es gibt keine direkte Browserverbindung zur Datenbank.

Alle Daten bleiben in `data/monitor.sqlite3`. Die Vorlage enthält keine Nutzerzustände und keine eingebetteten Archivdaten. `scripts/render_news.py` öffnet die Datenbank ausschließlich lesend und bindet aktuelle Meldungen, Quellen, Markierungen und aktive Probleme ein.

## Mehrere Meldungen als gelesen markieren

Ansichtspräferenz: Werbung einschließlich Eigenwerbung (`ad=ja`) kann ausgeblendet werden. Gespeichert in `ui/news-preferences.json` als `hide_advertising`. Gilt für alle Ansichten, ohne Archivmeldungen oder Markierungen zu verändern. Unklare Werbeeinordnungen bleiben sichtbar. Auf Wunsch durch Ändern dieser Präferenz wieder einblenden.

Checkboxen wählen ungelesene Meldungen aus; „Seite auswählen“ ergänzt die ungelesenen Meldungen der sichtbaren Seite. Die Auswahl bleibt beim Blättern und Filterwechsel erhalten und lässt sich vollständig aufheben. Erst „N als gelesen markieren“ übergibt einen ausdrücklichen Auftrag mit sämtlichen ausgewählten IDs an den Chat. Für jede angegebene ID `state ID --read yes --reason ...` ausführen, andere Markierungen unverändert lassen und anschließend erneut rendern. Die Auswahl allein ändert keinen Archivzustand. Bereits gelesene IDs werden nach dem Aktualisieren aus der Auswahl entfernt.

## Direkter Sprung zur Videostelle

„Im Video ansehen“ öffnet YouTube direkt an der frühesten belegten Zeitmarke des Themas. Bei mehreren Videos gibt es zusätzliche Zeitmarkenlinks unter „Quellen & Belege“. Kein Chatauftrag und keine Markierungsänderung beim Öffnen. Ohne belegte Zeitmarke keinen Zeitsprung erfinden; der normale Quellenlink bleibt verfügbar.
