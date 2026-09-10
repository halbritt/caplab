"""Observe original public adapter and CLI paths through real local HTTPS."""
import dataclasses
from datetime import datetime, timezone
import fcntl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sqlite3
import ssl
import subprocess
import sys
import threading
import time

sys.path.insert(0, '/source')
from newsroom.sources.reddit import RedditAdapter

ROOT = Path('/capture')
condition = sys.argv[1]
NAMES = ['MachineLearning', 'LocalLLaMA', 'OpenAI']
if datetime.now(timezone.utc).date().isoformat() != '2026-09-10':
    raise ValueError('frozen publication window expired')
events = []
event_lock = threading.Lock()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + '\n')


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        with event_lock:
            events.append({'path': self.path, 'monotonic': time.monotonic(), 'headers': dict(self.headers)})
        expected = {f'/r/{name}/hot/?limit=25': name for name in NAMES}
        if self.path not in expected:
            self.send_error(404)
            return
        body = Path('/witness/' + expected[self.path] + '.html').read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 443), Handler)
tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
tls.load_cert_chain('/witness/cert.pem', '/witness/key.pem')
server.socket = tls.wrap_socket(server.socket, server_side=True)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
configuration = {'rss_fallback': True, 'use_harvested': True, 'provider_state_dir': '/capture/data/reddit-provider',
                 'max_workers': 3, 'subreddits': [{'name': name, 'limit': 25, 'ai_focused': True, 'min_score': 0} for name in NAMES]}
results = {}


def invoke(label, operation):
    before = len(events)
    started = time.monotonic()
    try:
        articles = operation()
        results[label] = {'articles': [dataclasses.asdict(a) for a in articles], 'error': None}
    except Exception as exc:
        results[label] = {'articles': [], 'error': {'type': type(exc).__name__, 'message': str(exc)}}
    results[label].update(elapsed_seconds=time.monotonic() - started, requests_before=before, requests_after=len(events))


try:
    if condition == 'base-listing':
        invoke('listing', lambda: RedditAdapter(configuration).fetch(24))
    elif condition == 'change-pool':
        invoke('harvest', lambda: RedditAdapter(configuration).harvest(24))
        invoke('pool', lambda: RedditAdapter(configuration).fetch(24))
        disabled = configuration | {'rss_fallback': False}
        invoke('disabled-harvest', lambda: RedditAdapter(disabled).harvest(24))
        invoke('disabled-pool', lambda: RedditAdapter(disabled).fetch(24))
    elif condition == 'change-cli-lock':
        data = ROOT / 'data'
        data.mkdir()
        lock = (data / 'run.lock').open('a')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for command in ('harvest', 'run', 'fetch'):
            args = ['/usr/bin/python3', '-B', '-m', 'newsroom', command, '--source', 'reddit']
            before = len(events)
            result = subprocess.run(args, capture_output=True, timeout=15, env=os.environ | {
                'NEWSROOM_DATA_DIR': str(data), 'PYTHONPATH': '/source', 'PYTHONDONTWRITEBYTECODE': '1'})
            (ROOT / (command + '.stdout')).write_bytes(result.stdout)
            (ROOT / (command + '.stderr')).write_bytes(result.stderr)
            results[command] = {'command': args, 'returncode': result.returncode,
                                'requests_before': before, 'requests_after': len(events)}
        # A different descriptor cannot acquire the still-held exclusive lock.
        with (data / 'run.lock').open('a') as contender:
            try:
                fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                results['lock_remains_held'] = True
            else:
                results['lock_remains_held'] = False
        lock.close()
    else:
        raise ValueError('unexpected condition')
    database = ROOT / 'data/reddit-provider/rss.db'
    if database.exists():
        with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as db:
            results['database'] = {'state': dict(db.execute('SELECT key, value FROM state')),
                'candidates': [{'url': url, 'article': json.loads(article)} for url, article in db.execute('SELECT url, article FROM candidates ORDER BY url')],
                'feeds': db.execute('SELECT url, fetched_at FROM feeds ORDER BY url').fetchall()}
    write(ROOT / 'observation.json', {'condition': condition, 'results': results})
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
    write(ROOT / 'requests.json', events)
