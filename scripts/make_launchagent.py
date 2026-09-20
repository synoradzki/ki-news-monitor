"""Erzeugt eine LaunchAgent-Datei; installiert oder aktiviert keinen Dienst."""
import os
from pathlib import Path
import plistlib
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import monitor as m
output = ROOT / 'dist/local.ai-news-monitor.plist'
output.parent.mkdir(exist_ok=True)
(m.DATA / 'logs').mkdir(parents=True, exist_ok=True)
config = {'Label': 'local.ai-news-monitor', 'ProgramArguments': [sys.executable, str(ROOT / 'scripts/daily.py')], 'WorkingDirectory': str(ROOT), 'RunAtLoad': True, 'StartInterval': 3600, 'StartCalendarInterval': {'Hour': m.CFG['daily_hour'], 'Minute': m.CFG['daily_minute']}, 'EnvironmentVariables': {'HOME': str(Path.home()), 'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'NEWS_MONITOR_CONFIG': str(m.CONFIG_PATH.resolve()), 'NEWS_MONITOR_DATA': str(m.DATA.resolve())}, 'StandardOutPath': str(m.DATA.resolve() / 'logs/launchd.stdout.log'), 'StandardErrorPath': str(m.DATA.resolve() / 'logs/launchd.stderr.log')}
with output.open('wb') as stream:
    plistlib.dump(config, stream)
print(output)
