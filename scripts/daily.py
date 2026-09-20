#!/usr/bin/env python3
"""Kalendertäglicher Start und Nachholen in Europe/Berlin."""
import datetime as dt
import fcntl
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import monitor as m

def due(c,current):
 current=current.astimezone(m.TZ)
 scheduled=current.replace(hour=m.CFG['daily_hour'],minute=m.CFG['daily_minute'],second=0,microsecond=0)
 last=c.execute("SELECT started FROM runs WHERE mode='run' AND finished IS NOT NULL AND status IN ('success','partial') ORDER BY id DESC LIMIT 1").fetchone()
 return current>=scheduled and not (last and dt.datetime.fromisoformat(last['started'])>=scheduled)

def main():
 m.DATA.mkdir(parents=True,exist_ok=True)
 with (m.DATA/'scheduler.lock').open('w') as lock:
  try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError: return
  c=m.db()
  try:
   if due(c,dt.datetime.now(m.TZ)): m.run(c,'run')
  finally: c.close()

if __name__=='__main__': main()
