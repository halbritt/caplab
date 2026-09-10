"""Run the original harvester against real controlled HTTPS responses."""
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import ssl
import subprocess
import sys
import threading
import time

ROOT = Path('/capture')
condition = sys.argv[1]
criteria = json.loads(Path('/witness/criteria.json').read_text())
scenario = criteria['conditions'][condition]
if datetime.now(timezone.utc).date().isoformat() != '2026-09-10':
    raise ValueError('frozen publication window expired')
events = []
lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        host = self.headers.get('Host')
        status, body, content_type = 404, b'unexpected request', 'text/plain'
        for name in criteria['names']:
            if host == 'old.reddit.com' and self.path == f'/r/{name}/hot/?limit=25':
                if name in scenario['blocked']:
                    status, body = 403, b'controlled listing unavailable'
                else:
                    status = 200
                    body = Path('/witness/' + ('empty.html' if scenario['empty'] else name + '.html')).read_bytes()
                    content_type = 'text/html; charset=utf-8'
            elif host == 'www.reddit.com' and self.path == f'/r/{name}/hot.json?limit=25&raw_json=1':
                if name in scenario['blocked']:
                    status, body = 403, b'controlled listing unavailable'
        names = '+'.join(scenario['blocked'])
        if names and host == 'www.reddit.com' and self.path == f'/r/{names}/hot/.rss?limit={25 * len(scenario["blocked"])}':
            status = 200 if scenario['rss_success'] else 403
            body = Path('/witness/feed.xml').read_bytes() if status == 200 else b'controlled RSS unavailable'
            content_type = 'application/atom+xml' if status == 200 else 'text/plain'
        with lock:
            events.append({'path': self.path, 'host': host, 'status': status,
                           'body_sha256': hashlib.sha256(body).hexdigest(),
                           'body_bytes': len(body), 'monotonic': time.monotonic()})
        self.send_response(status)
        self.send_header('Content-Type', content_type)
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
try:
    command = ['/usr/bin/python3', '-B', '-m', 'newsroom', 'harvest', '--source', 'reddit']
    started = time.monotonic()
    result = subprocess.run(command, capture_output=True, timeout=45,
        env=os.environ | {'NEWSROOM_DATA_DIR': '/capture/data', 'PYTHONPATH': '/source',
                          'PYTHONDONTWRITEBYTECODE': '1'})
    elapsed = time.monotonic() - started
    (ROOT / 'harvest.stdout').write_bytes(result.stdout)
    (ROOT / 'harvest.stderr').write_bytes(result.stderr)
    database = ROOT / 'data/reddit-provider/rss.db'
    with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as db:
        state = dict(db.execute('SELECT key, value FROM state'))
        candidates = [{'url': url, 'article': json.loads(article)} for url, article in db.execute('SELECT url, article FROM candidates ORDER BY url')]
        feeds = [{'url': url, 'fetched_at': when, 'body_sha256': hashlib.sha256(body).hexdigest()}
                 for url, when, body in db.execute('SELECT url, fetched_at, body FROM feeds ORDER BY url')]
    (ROOT / 'observation.json').write_text(json.dumps({'condition': condition,
        'command': command, 'returncode': result.returncode, 'elapsed_seconds': elapsed,
        'database': {'state': state, 'candidates': candidates, 'feeds': feeds}}, indent=2, sort_keys=True) + '\n')
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
    (ROOT / 'requests.json').write_text(json.dumps(events, indent=2, sort_keys=True) + '\n')
