import sys, unittest, tempfile, json, subprocess, os
from pathlib import Path
import monitor as m

class MonitorTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.prev=m.DATA; m.DATA=Path(self.tmp.name); self.c=m.db()
  self.c.execute("INSERT INTO items(id,title) VALUES('v','Test')"); self.c.commit()
 def tearDown(self): self.c.close(); m.DATA=self.prev; self.tmp.cleanup()
 def topic(self,**kw):
  t=dict(existing_id=None,event_key='produkt-version-ereignis',title='Thema',claim='Quelle berichtet A',assessment='Einschätzung',customer=5,coding=3,marketing=1,ad='nein',is_update=False,segment_ids=[1,2]); t.update(kw); return t
 def test_merge_update_keeps_user_state(self):
  with self.c: m.save_topic(self.c,'v',self.topic())
  self.c.execute("UPDATE states SET read=1,saved=1,testing=1,idea='Versuch',benefit='Nutzen',result='Ergebnis'"); self.c.commit()
  with self.c:
   self.c.execute("INSERT INTO items(id,title) VALUES('v2','Weitere Quelle')")
   m.save_topic(self.c,'v2',self.topic(existing_id=1,is_update=True,segment_ids=[3],claim='Ergänzung'))
  self.assertEqual(self.c.execute('SELECT COUNT(*) FROM topics').fetchone()[0],1)
  self.assertEqual(tuple(self.c.execute('SELECT read,saved,testing,idea,benefit,result FROM states').fetchone()),(1,1,1,'Versuch','Nutzen','Ergebnis'))
  self.assertEqual(self.c.execute('SELECT SUM(is_update) FROM evidence').fetchone()[0],1)
 def test_idempotence_all_evidence(self):
  with self.c:
   m.save_topic(self.c,'v',self.topic()); m.save_topic(self.c,'v',self.topic())
   self.c.execute("INSERT INTO items(id,title) VALUES('v2','Quelle 2')")
   m.save_topic(self.c,'v2',self.topic())
  self.assertEqual(self.c.execute('SELECT COUNT(*) FROM topics').fetchone()[0],1)
  self.assertEqual(self.c.execute('SELECT COUNT(*) FROM evidence').fetchone()[0],2)
 def test_chunk_coverage(self):
  rows=[dict(id=i,start=i,end=i+1,text='ä'*200) for i in range(100)]
  parts=m.chunks(rows,1000)
  self.assertEqual({r['id'] for p in parts for r in p},set(range(100)))
 def test_original_and_time(self):
  rows=m.normalize_json3({'events':[{'tStartMs':1234,'dDurationMs':2000,'segs':[{'utf8':'Original English'}]}]})
  self.assertEqual(rows[0],dict(id=0,start=1.234,end=3.234,text='Original English'))
 def test_timezone(self):
  d,p=m.published({'timestamp':1789336800})
  self.assertEqual(d.isoformat(),'2026-09-14T00:00:00+02:00')
 def test_failed_source_keeps_success(self):
  m.source_result(self.c,'test'); success=self.c.execute('SELECT success FROM sources').fetchone()[0]
  m.source_result(self.c,'test','Ausfall')
  self.assertEqual(self.c.execute('SELECT success FROM sources').fetchone()[0],success)
 def test_list_never_marks_read(self):
  with self.c: m.save_topic(self.c,'v',self.topic())
  env=dict(os.environ,NEWS_MONITOR_DATA=str(m.DATA))
  subprocess.run([sys.executable,str(m.ROOT/'monitor.py'),'list'],env=env,check=True,capture_output=True)
  self.assertEqual(self.c.execute('SELECT read FROM states').fetchone()[0],0)
 def test_merge_preserves_original_evidence(self):
  with self.c:
   m.save_topic(self.c,'v',self.topic())
   m.save_topic(self.c,'v',self.topic(event_key='gleiches-ereignis',segment_ids=[8]))
  self.assertEqual(m.merge_topics(self.c,1,2,True,'Ergänzung'),'zusammengeführt')
  self.assertEqual(self.c.execute('SELECT COUNT(*) FROM evidence WHERE topic_id=1').fetchone()[0],2)
  with self.c: m.save_topic(self.c,'v',self.topic(event_key='gleiches-ereignis',segment_ids=[9]))
  self.assertEqual(self.c.execute('SELECT COUNT(*) FROM evidence WHERE topic_id=1').fetchone()[0],3)
  self.assertEqual(self.c.execute('SELECT SUM(read) FROM states').fetchone()[0],0)
 def test_merge_does_not_override_explicit_decisions(self):
  with self.c:
   m.save_topic(self.c,'v',self.topic())
   m.save_topic(self.c,'v',self.topic(event_key='anderer-key',segment_ids=[8]))
   self.c.execute("INSERT INTO audit(topic_id,action,reason) VALUES(2,'read','Nutzer')")
  self.assertIn('Nutzerzustand',m.merge_topics(self.c,1,2,False,'Doppelt'))
 def test_x_edits_preserve_original(self):
  def body(text):
   t={'id_str':'123','user':{'screen_name':'OpenAI'},'created_at':'Thu Sep 17 20:15:15 +0000 2026','full_text':text,'lang':'en'}
   return '<script id="__NEXT_DATA__">'+json.dumps({'props':{'pageProps':{'timeline':{'entries':[{'content':{'tweet':t}}]}}}})+'</script>'
  m.import_x(self.c,'OpenAI',body('Original'))
  m.import_x(self.c,'OpenAI',body('Bearbeitet'))
  m.import_x(self.c,'OpenAI',body('Bearbeitet'))
  rows=self.c.execute("SELECT transcript FROM items WHERE source='x:OpenAI'").fetchall()
  self.assertEqual(len(rows),2)
  self.assertEqual({json.loads(Path(r[0]).read_text())[0]['text'] for r in rows},{'Original','Bearbeitet'})
 def test_x_invalid_not_silent_success(self):
  with self.assertRaises(ValueError): m.parse_x('<html>login</html>','OpenAI')
 def test_states_independent_and_durable(self):
  with self.c: m.save_topic(self.c,'v',self.topic())
  env=dict(os.environ,NEWS_MONITOR_DATA=str(m.DATA))
  for opts in (['--saved','yes'],['--testing','yes','--idea','Pilot','--benefit','Zeitgewinn']):
   subprocess.run([sys.executable,str(m.ROOT/'monitor.py'),'state','1','--reason','Testanweisung']+opts,env=env,check=True,capture_output=True)
  self.assertEqual(tuple(self.c.execute('SELECT read,saved,testing FROM states').fetchone()),(0,1,1))
 def test_status_only_does_not_send_notifications(self):
  from unittest.mock import patch
  old=m.CFG.get('notifications');m.CFG['notifications']='status_only'
  try:
   m.source_result(self.c,'x:Test','Abruf fehlgeschlagen')
   with patch.object(m,'command',side_effect=AssertionError('Keine Mitteilung erlaubt')):
    self.assertIn('x:Test',m.notify_problems(self.c))
   self.assertEqual(self.c.execute('SELECT active FROM alerts').fetchone()[0],1)
   m.source_result(self.c,'x:Test')
   m.notify_problems(self.c)
   self.assertEqual(self.c.execute('SELECT active FROM alerts').fetchone()[0],0)
  finally:m.CFG['notifications']=old
 def test_sections_of_first_video_are_not_news_updates(self):
  with self.c:
   m.save_topic(self.c,'v',self.topic())
   m.save_topic(self.c,'v',self.topic(existing_id=1,segment_ids=[3],is_update=True))
  self.assertEqual(self.c.execute('SELECT SUM(is_update) FROM evidence').fetchone()[0],0)
if __name__=='__main__': unittest.main()
