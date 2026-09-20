# KI-News-Monitor

Experimenteller persönlicher KI-News-Monitor für macOS. Sammelt YouTube-Beiträge und optional öffentliche X-Posts, extrahiert einzelne Themen und speichert Quellenbelege sowie unabhängige Markierungen in SQLite. Ausgaben auf Deutsch, Originalstellen mit Zeitmarken in der Quellensprache.

Kundenlösungen, eigene technische Umsetzung und Marketing werden gleich gewichtet. Quellenbehauptungen, eigene Einschätzungen und Werbung bleiben getrennt.

## Voraussetzungen

- macOS und Python 3.10 oder neuer; Python verwendet ausschließlich die Standardbibliothek.
- Für echte Abrufe: `yt-dlp` im PATH.
- Für KI-Auswertungen: eine installierte Codex CLI mit eigener ChatGPT-Anmeldung und einem verfügbaren Modell. Die Auswertung nutzt deren Kontingent; es gibt keine API-Key-Ausweichroute.
- Optional für Beiträge ohne Untertitel: `ffmpeg`, `whisper-cli` und eine kompatible lokale Whisper-Modelldatei. Das Modell wird nicht mitgeliefert.

Die vorhandene Codex-Aufrufintegration setzt unter anderem `--ignore-user-config`, `--ephemeral` und `--output-schema` voraus. CLI-Versionen können abweichen; bei unbekannten Optionen endet die Verarbeitung mit dokumentiertem Fehler. Dieses Repository installiert keine Werkzeuge und richtet keine Anmeldung ein.

## Einrichtung

Im Projektordner:

```sh
python3 scripts/setup.py
```

Danach `config.json` bearbeiten:

- `model`: Platzhalter durch ein in der eigenen Anmeldung verfügbares Modell ersetzen.
- `youtube` und `x`: gewünschte Handles ohne `@`; X ist zunächst deaktiviert.
- `initial_since`: fester Beginn des Erfassungszeitraums, inklusive Zeitzonenoffset. Das Setup setzt ihn auf vor sieben Tagen.
- `tools`: Programmnamen im PATH oder absolute Pfade eintragen.
- `whisper_model`: absoluter Pfad oder Pfad relativ zum Projektordner.

`config.json` ist lokal und wird von Git ausgeschlossen. Alternativ wählt `NEWS_MONITOR_CONFIG` eine andere Konfigurationsdatei. `NEWS_MONITOR_DATA` wählt einen anderen Datenordner; relative Datenpfade beziehen sich auf das Arbeitsverzeichnis.

## Offline ausprobieren

Nach dem Setup ohne externe Werkzeuge, Anmeldung oder Netzwerk:

```sh
python3 scripts/demo.py
NEWS_MONITOR_DATA=data/demo python3 monitor.py list --filter unread
NEWS_MONITOR_DATA=data/demo python3 monitor.py show 1
NEWS_MONITOR_DATA=data/demo python3 monitor.py passage 1
```

Die Demo enthält ausschließlich erfundene Inhalte und verwendet ein separates Archiv. Wiederholtes Ausführen legt keine doppelte Meldung an.

## Eigene Nachrichten abrufen

Nach Anpassung der Konfiguration:

```sh
python3 monitor.py run
python3 monitor.py status
python3 monitor.py list --filter unread --limit 10
python3 monitor.py list --query Telefon
python3 monitor.py show 1
python3 monitor.py passage 1
```

IDs sind Beispiele. `collect` ruft nur ab, `process` setzt die Auswertung fort, `reconcile` gleicht Themen ab. Anzeigen verändert niemals Markierungen.

```sh
python3 monitor.py state 1 --read yes --reason 'Ausdrücklich als gelesen markieren'
python3 monitor.py state 1 --saved yes --reason 'Für später merken'
python3 monitor.py state 1 --testing yes --idea 'Dokumentensuche ausprobieren' --benefit 'Interne Suche vereinfachen' --reason 'Auf Testliste setzen'
```

## Optionale Chatansicht

Die CLI funktioniert eigenständig. `NEWS-WORKFLOW.md` beschreibt zusätzlich eine Codex-Chatansicht, die einen verfügbaren Visualize-Skill und die Host-Integration für Aktionsnachrichten benötigt. Die HTML-Vorlage ist kein eigenständig schreibendes Dashboard. Ohne diese Integration die CLI verwenden.

```sh
NEWS_MONITOR_DATA=data/demo python3 scripts/render_news.py --output exports/demo.html
```

Gerenderte Ansichten enthalten Archivdaten und gehören nicht ins öffentliche Repository.

## Optionaler täglicher Betrieb auf macOS

```sh
python3 scripts/make_launchagent.py
```

Dies erzeugt nur `dist/local.ai-news-monitor.plist` mit den lokalen Pfaden. Es wird kein Dienst installiert oder gestartet. Erst nach erfolgreichem manuellem Lauf und Prüfung der Datei kann sie bewusst installiert werden:

```sh
mkdir -p ~/Library/LaunchAgents
cp dist/local.ai-news-monitor.plist ~/Library/LaunchAgents/local.ai-news-monitor.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.ai-news-monitor.plist
```

Entfernen aus dem laufenden Betrieb:

```sh
launchctl bootout gui/$(id -u)/local.ai-news-monitor
```

Der Zeitplan nutzt die konfigurierte Zeitzone, prüft stündlich auf Nachholbedarf und verhindert überlappende Läufe. Ein eingeschalteter Mac und eine angemeldete Benutzersitzung sind erforderlich. Bei bereits bestehender Monitor-Installation keinen zweiten Dienst mit denselben Quellen aktivieren.

## Grenzen und Daten

- YouTube-Abrufe und Untertitel können fehlen oder blockiert sein. Der vollständige Audio-Fallback ist in dieser Veröffentlichung nicht mit einem echten Video nachgewiesen.
- X verwendet eine öffentliche Einbettungs-Timeline ohne Vollständigkeitsgarantie oder verifizierte Pagination. Medien und verlinkte Artikel werden nicht ausgewertet.
- KI-Extraktion, Bewertung und Zusammenführung können Fehler enthalten. Quelleninhalte sind keine unabhängig bestätigten Fakten.
- SQLite, Originaltexte, Audio, Modelle, Logs und Backups liegen unter `data/`. Sie werden nicht mitgeliefert. Es gibt keine automatische Datenlöschung; lokale Backups ersetzen keine Sicherung auf einem anderen Datenträger.
- Die KI-Auswertung übergibt Quellenabschnitte an die konfigurierte Codex CLI. Das Archiv liegt lokal; die KI-Auswertung ist nicht vollständig offline.
- Standardmäßig bleiben Störungen im Status gespeichert; keine E-Mails oder lokalen Benachrichtigungen.
- Windows wird wegen `fcntl` und des macOS-Zeitplans nicht unterstützt; Linux wurde nicht separat geprüft.

## Entwicklung

```sh
python3 scripts/setup.py  # nur falls config.json noch fehlt
python3 -m unittest discover -s tests -v
```

Die Tests verwenden temporäre Datenbanken und benötigen kein Netzwerk. Sie prüfen unter anderem Persistenz, getrennte Markierungen, Belege, Zusammenführungen und Zeitumstellung. Sie ersetzen keinen echten Abruf-/Modellintegrationstest.

Siehe [VALIDIERUNG.md](VALIDIERUNG.md) für die tatsächlich ausgeführten Prüfungen. MIT-Lizenz: [LICENSE](LICENSE).
