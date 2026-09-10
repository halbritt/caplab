"""Measure the unchanged recovery budget through original harvest and HTTPS."""
import dataclasses
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import ssl
import sys
import threading
import time
from xml.etree import ElementTree as ET

sys.path.insert(0, '/source')
from newsroom.sources.reddit import RedditAdapter
from newsroom.sources.reddit_state import RECOVERY_SECONDS
from newsroom.sources.feeds import TIMEOUT

ROOT = Path('/capture')
condition = sys.argv[1]
criteria = json.loads(Path('/witness/criteria.json').read_text())
feed = Path('/witness/feed.xml').read_bytes()
assert ET.fromstring(feed).tag == '{http://www.w3.org/2005/Atom}feed'
if datetime.now(timezone.utc).date().isoformat() != '2026-09-10':
    raise ValueError('frozen publication window expired')
if condition not in criteria['conditions'] or RECOVERY_SECONDS != 180 or TIMEOUT != 30:
    raise ValueError('condition or original runtime constants changed')
request_count = 0
stopping = threading.Event()
finished = threading.Event()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + '\n')


def event(value):
    with (ROOT / 'server-events.jsonl').open('a') as stream:
        stream.write(json.dumps({'monotonic': time.monotonic(), **value}) + '\n')


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global request_count
        request_count += 1
        event({'event': 'request', 'path': self.path, 'headers': dict(self.headers)})
        if self.path != '/r/MachineLearning/hot/.rss?limit=25':
            self.send_error(404)
            finished.set()
            return
        prefix = criteria['drip_seconds'] if condition == 'drip' else 0
        payload = b' ' * prefix + feed
        (ROOT / 'response-body.xml').write_bytes(payload)
        sent = 0
        error = None
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/atom+xml')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            event({'event': 'headers', 'content_length': len(payload)})
            for index in range(prefix):
                if stopping.is_set():
                    break
                self.wfile.write(b' ')
                self.wfile.flush()
                sent += 1
                event({'event': 'byte', 'index': index})
                time.sleep(1)
            if not stopping.is_set():
                self.wfile.write(feed)
                self.wfile.flush()
                sent += len(feed)
                event({'event': 'body-complete', 'bytes': sent})
        except (BrokenPipeError, ConnectionResetError, ssl.SSLError) as exc:
            error = type(exc).__name__
            event({'event': 'client-closed', 'error': error})
        finally:
            write(ROOT / 'server-completion.json', {'sent_bytes': sent, 'complete': sent == len(payload), 'error': error})
            finished.set()

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 443), Handler)
tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
tls.load_cert_chain('/witness/cert.pem', '/witness/key.pem')
server.socket = tls.wrap_socket(server.socket, server_side=True)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
configuration = {'rss_fallback': True, 'use_harvested': True, 'provider_state_dir': '/capture/provider',
                 'subreddits': [{'name': 'MachineLearning', 'limit': 25, 'ai_focused': True}]}
try:
    adapter = RedditAdapter(configuration)
    adapter.provider.listings_blocked()
    started = time.monotonic()
    write(ROOT / 'harvest-started.json', {'monotonic': started, 'utc': datetime.now(timezone.utc),
                                        'recovery_seconds': RECOVERY_SECONDS, 'socket_timeout': TIMEOUT})
    articles, error = [], None
    try:
        articles = adapter.harvest(24)
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc)}
    elapsed = time.monotonic() - started
    requests_before_reopen = request_count
    reopened, reopen_error = [], None
    if error is None:
        try:
            reopened = RedditAdapter(configuration).fetch(24)
        except Exception as exc:
            reopen_error = {'type': type(exc).__name__, 'message': str(exc)}
    with sqlite3.connect('/capture/provider/rss.db') as db:
        state = dict(db.execute('SELECT key, value FROM state'))
        feeds = [{'url': url, 'fetched_at': at, 'body_sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}
                 for url, at, body in db.execute('SELECT url, fetched_at, body FROM feeds')]
        candidates = [{'url': url, 'article': json.loads(article), 'published_at': published}
                      for url, article, published in db.execute('SELECT url, article, published_at FROM candidates')]
    write(ROOT / 'observation.json', {'condition': condition, 'elapsed_seconds': elapsed, 'error': error,
        'articles': [dataclasses.asdict(a) for a in articles], 'reopened_articles': [dataclasses.asdict(a) for a in reopened],
        'reopen_error': reopen_error, 'requests_before_reopen': requests_before_reopen, 'requests_after_reopen': request_count,
        'state': state, 'feeds': feeds, 'candidates': candidates})
finally:
    stopping.set()
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)
    if request_count and not finished.wait(timeout=3):
        raise RuntimeError('endpoint capture did not finish')
