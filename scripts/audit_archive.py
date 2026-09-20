#!/usr/bin/env python3
"""Lesende Konsistenzprüfung; verändert weder Meldungen noch Nutzerzustände."""
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import monitor as m
c=m.db(); errors=[]; checked=0
for r in c.execute('PRAGMA integrity_check'):
 if r[0]!='ok': errors.append(r[0])
errors += [str(tuple(r)) for r in c.execute('PRAGMA foreign_key_check')]
for row in c.execute('SELECT e.id,e.segment_ids,i.transcript FROM evidence e JOIN items i ON e.item_id=i.id'):
 try:
  segments=json.loads(Path(row['transcript']).read_text()); ids={r['id'] for r in segments}
  if not set(json.loads(row['segment_ids']))<=ids: errors.append(f"Beleg {row['id']}: ungültige Segment-ID")
  checked+=1
 except Exception as e: errors.append(f"Beleg {row['id']}: {e}")
for row in c.execute("SELECT * FROM items WHERE status='complete'"):
 try:
  plan=m.DATA/'raw'/row['id']/'chunk-plan.json'
  size=json.loads(plan.read_text())['size'] if plan.exists() else 12000
  sections=m.chunks(json.loads(Path(row['transcript']).read_text()),size)
  for idx,section in enumerate(sections):
   digest=m.hashlib.sha256(json.dumps(section,sort_keys=True).encode()).hexdigest()
   if not c.execute('SELECT 1 FROM chunks WHERE item_id=? AND idx=? AND digest=?',(row['id'],idx,digest)).fetchone(): errors.append(f"{row['id']}: Abschnitt {idx} nicht fertig")
 except Exception as e: errors.append(f"{row['id']}: {e}")
for row in c.execute('SELECT id FROM topics WHERE id NOT IN (SELECT old_id FROM aliases) AND id NOT IN (SELECT topic_id FROM evidence)'):
 errors.append(f'Thema {row[0]} ohne Beleg')
report={'checked_at':m.now(),'passed':not errors,'evidence_checked':checked,'errors':errors,'item_statuses':{r[0]:r[1] for r in c.execute('SELECT status,COUNT(*) FROM items GROUP BY status')},'user_states':dict(c.execute('SELECT COALESCE(SUM(read),0) AS read,COALESCE(SUM(saved),0) AS saved,COALESCE(SUM(testing),0) AS testing FROM states').fetchone())}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
