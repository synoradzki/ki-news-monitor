"""Render the chat overview from the archive, without changing any state."""
import argparse
import datetime as dt
import html
import json
from pathlib import Path
import sqlite3
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import monitor as m


def render(output):
    preferences_path = ROOT / 'ui/news-preferences.json'
    preferences = json.loads(preferences_path.read_text()) if preferences_path.exists() else {}
    clarifications_path = m.DATA / 'news-clarifications.json'
    clarifications = json.loads(clarifications_path.read_text()) if clarifications_path.exists() else {}
    hidden_ads = 0
    transcripts = {}
    with sqlite3.connect((m.DATA / 'monitor.sqlite3').resolve().as_uri() + '?mode=ro', uri=True) as c:
        c.row_factory = sqlite3.Row
        items = []
        for row in c.execute('''SELECT t.id,t.title,t.claim,t.assessment,t.ad,
            s.read,s.saved,s.testing,s.idea,s.benefit,s.result,
            (t.customer+t.coding+t.marketing) AS relevance
            FROM topics t JOIN states s ON s.topic_id=t.id
            WHERE t.id NOT IN (SELECT old_id FROM aliases)'''):
            item = dict(row)
            item['clarifications'] = clarifications.get(str(item['id']), [])
            if preferences.get('hide_advertising') and item['ad'] == 'ja':
                hidden_ads += 1
                continue
            item['sources'] = [dict(r) for r in c.execute('''SELECT DISTINCT
                i.source,i.url,i.title,i.published FROM evidence e
                JOIN items i ON i.id=e.item_id WHERE e.topic_id=?
                ORDER BY i.published DESC,i.id''', (item['id'],))]
            for source in item['sources']:
                if not source['source'].startswith('youtube:'):
                    continue
                starts = []
                for evidence in c.execute('''SELECT e.segment_ids,i.transcript FROM evidence e
                        JOIN items i ON i.id=e.item_id WHERE e.topic_id=? AND i.url=?''',
                        (item['id'], source['url'])):
                    path = evidence['transcript']
                    if not path:
                        continue
                    if path not in transcripts:
                        try:
                            transcripts[path] = {s['id']: s.get('start') for s in json.loads(Path(path).read_text())}
                        except (OSError, ValueError):
                            transcripts[path] = {}
                    starts.extend(transcripts[path][sid] for sid in json.loads(evidence['segment_ids'])
                                  if isinstance(transcripts[path].get(sid), (int, float))
                                  and transcripts[path][sid] >= 0)
                if starts:
                    source['start'] = int(min(starts))
                    parts = urlsplit(source['url'])
                    query = [(k, v) for k, v in parse_qsl(parts.query) if k not in ('t', 'start')]
                    source['passage_url'] = urlunsplit(parts._replace(query=urlencode(query + [('t', source['start'])])))
            items.append(item)
        items.sort(key=lambda d: ((d['sources'][0]['published'] or '')
                   if d['sources'] else '', d['relevance']), reverse=True)
        alerts = [dict(r) for r in c.execute('SELECT key,message FROM alerts WHERE active=1')]
        run = c.execute('SELECT finished FROM runs WHERE finished IS NOT NULL ORDER BY id DESC LIMIT 1').fetchone()
    timestamp = (dt.datetime.fromisoformat(run['finished']).astimezone(ZoneInfo('Europe/Berlin'))
                 .strftime('%d.%m.%Y, %H:%M Uhr') if run else 'noch kein abgeschlossener Lauf')
    status = f'{len(alerts)} aktive Quellenprobleme · letzter abgeschlossener Lauf: {timestamp}'
    status_html = ('<details><summary class="cursor-interaction">' + html.escape(status)
                   + '</summary><ul>' + ''.join('<li>' + html.escape(a['key'] + ': ' + a['message'])
                   + '</li>' for a in alerts) + '</ul></details>') if alerts else html.escape(status)
    if preferences.get('hide_advertising'):
        status_html = f'<div>{hidden_ads} Meldungen mit Werbung / Eigenwerbung ausgeblendet</div>' + status_html
    template = (ROOT / 'ui/news-lesepult.template.html').read_text()
    result = template.replace('__NEWS_DATA__', json.dumps(items, ensure_ascii=False).replace('<', '\\u003c'))
    result = result.replace('__STATUS_HTML__', status_html)
    if len(result.encode()) >= 1_000_000:
        raise SystemExit('Ansicht überschreitet 1 MB; Datenumfang vor Ausgabe reduzieren.')
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result)
    print(json.dumps({'path': str(output), 'topics': len(items),
                      'unread': sum(not i['read'] for i in items), 'hidden_ads': hidden_ads,
                      'alerts': len(alerts)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    render(parser.parse_args().output)
