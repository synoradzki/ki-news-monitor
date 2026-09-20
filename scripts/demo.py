"""Erzeugt ausschließlich erfundene Nachrichten in einem separaten Demoarchiv."""
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
os.environ['NEWS_MONITOR_DATA'] = str(ROOT / 'data/demo')
sys.path.insert(0, str(ROOT))
import monitor as m
c = m.db()
path = m.DATA / 'raw/demo/segments.json'
m.dump(path, [{'id': 0, 'start': None, 'end': None, 'text': 'Fiktive Demo: BeispielBot kann Dokumente durchsuchen.'}])
c.execute("INSERT OR IGNORE INTO items(id,source,url,title,published,precision,status,transcript,language,method) VALUES(?,?,?,?,?,?,'complete',?,'de','synthetic')", ('demo', 'demo:Erfundener Kanal', 'https://example.com/demo', 'Fiktive Produktmeldung', m.now(), 'second', str(path)))
with c:
    m.save_topic(c, 'demo', dict(existing_id=None,event_key='demo-beispielbot',title='Demo: BeispielBot durchsucht Dokumente',claim='Die erfundene Demoquelle beschreibt eine Dokumentensuche.',assessment='Eigene Einschätzung: Als Beispiel für eine interne Wissenssuche geeignet; kein getestetes Produkt.',customer=4,coding=4,marketing=4,ad='nein',is_update=False,segment_ids=[0]))
c.close()
print('Demo erstellt. Anzeigen: NEWS_MONITOR_DATA=data/demo python3 monitor.py list --filter unread')
