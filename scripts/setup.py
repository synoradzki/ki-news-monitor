"""Erstellt eine lokale Konfiguration, ohne vorhandene Dateien zu überschreiben."""
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT / 'config.example.json').read_text())
start = dt.datetime.now(ZoneInfo(config['timezone'])).replace(hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=7)
config['initial_since'] = start.isoformat()
try:
    with (ROOT / 'config.json').open('x') as output:
        json.dump(config, output, ensure_ascii=False, indent=2)
        output.write('\n')
except FileExistsError:
    raise SystemExit('config.json existiert bereits und bleibt unverändert.')
print('config.json erstellt. Modell, Quellen und Werkzeugpfade vor einem Sammellauf anpassen.')
