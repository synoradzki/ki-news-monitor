import datetime as dt, tempfile, unittest
from pathlib import Path
import monitor as m
from scripts.daily import due

class SchedulerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=m.DATA;m.DATA=Path(self.tmp.name);self.c=m.db()
 def tearDown(self):self.c.close();m.DATA=self.old;self.tmp.cleanup()
 def at(self,time):return dt.datetime.fromisoformat(time).astimezone(m.TZ)
 def add(self,status='success',mode='run'):
  self.c.execute('INSERT INTO runs(started,finished,status,mode) VALUES(?,?,?,?)',('2026-09-20T08:16:00+02:00','2026-09-20T08:30:00+02:00',status,mode));self.c.commit()
 def test_before_time_and_catchup(self):
  self.assertFalse(due(self.c,self.at('2026-09-20T08:14:59+02:00')))
  self.assertTrue(due(self.c,self.at('2026-09-20T08:15:00+02:00')))
  self.assertTrue(due(self.c,self.at('2026-09-20T17:00:00+02:00')))
 def test_once_per_day_and_tomorrow(self):
  self.add('partial')
  self.assertFalse(due(self.c,self.at('2026-09-20T17:00:00+02:00')))
  self.assertTrue(due(self.c,self.at('2026-09-21T08:15:00+02:00')))
 def test_failed_and_collect_do_not_suppress_run(self):
  self.add('failed'); self.add('success','collect')
  self.assertTrue(due(self.c,self.at('2026-09-20T17:00:00+02:00')))
 def test_dst_uses_berlin_time(self):
  self.assertTrue(due(self.c,self.at('2026-10-25T07:15:00+00:00')))
  self.assertFalse(due(self.c,self.at('2026-10-25T06:15:00+00:00')))
if __name__=='__main__':unittest.main()
