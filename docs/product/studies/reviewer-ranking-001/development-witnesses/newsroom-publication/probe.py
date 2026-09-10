"""Run the real feed producer and original newsroom consumers in private custody."""
import dataclasses
from datetime import datetime, timedelta, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading

sys.path.insert(0, '/source')
from newsroom import cli, config, curate
from newsroom.model import Article
from newsroom.sources.rss import RssAdapter

CAPTURE = Path('/capture')
FEED = Path('/witness/feed.xml').read_bytes()
requests = []


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + '\n')


def command(name, argv):
    slot = CAPTURE / name
    slot.mkdir()
    write(slot / 'launch.json', {'argv': argv, 'started_at': datetime.now(timezone.utc), 'timeout_seconds': 15})
    process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    timed_out = False
    try:
        out, err = process.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        out, err = process.communicate(timeout=5)
    (slot / 'stdout').write_bytes(out)
    (slot / 'stderr').write_bytes(err)
    write(slot / 'completion.json', {'returncode': process.returncode, 'timed_out': timed_out,
                                    'finished_at': datetime.now(timezone.utc)})
    if process.returncode or timed_out:
        raise RuntimeError('fixture command failed: ' + name)
    return out.decode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        requests.append({'method': 'GET', 'path': self.path, 'headers': dict(self.headers)})
        if self.path != '/feed.xml':
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', 'application/rss+xml; charset=utf-8')
        self.send_header('Content-Length', str(len(FEED)))
        self.end_headers()
        self.wfile.write(FEED)

    def log_message(self, *args):
        pass


if datetime.now(timezone.utc).date().isoformat() != '2026-09-10':
    raise ValueError('execution date outside frozen fixture')
server = ThreadingHTTPServer(('127.0.0.1', 8765), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    command('add', ['blogwatcher', 'add', 'publication-witness', 'http://127.0.0.1:8765/',
                    '--feed-url', 'http://127.0.0.1:8765/feed.xml'])
    command('scan', ['blogwatcher', 'scan'])
    raw = command('articles-before', ['blogwatcher', 'articles'])
    adapter = RssAdapter({'mark_read': False, 'scan_timeout': 15, 'articles_timeout': 15})
    parsed = adapter._parse(raw)
    before = datetime.now(timezone.utc)
    fetched = adapter.fetch(24)
    after = datetime.now(timezone.utc)
    kept, dropped = cli._drop_stale(fetched, 24)
    rows = lambda articles: [dataclasses.asdict(article) for article in articles]
    write(CAPTURE / 'rss.json', {'before': before, 'after': after, 'parsed': rows(parsed), 'fetched': rows(fetched),
                               'pipeline_kept': rows(kept), 'pipeline_dropped': dropped})
    (CAPTURE / 'rss-curator-prompt.txt').write_text(curate._build_prompt(kept, top_n=5))
    os.environ['NEWSROOM_DATA_DIR'] = '/capture/newsroom-state'
    command('cli-fetch', ['/usr/bin/python3', '-I', '-B', '-c',
        'import sys; sys.path.insert(0,"/source"); from newsroom.cli import main; raise SystemExit(main(["fetch","--source","rss","--window","24"]))'])
    command('articles-after', ['blogwatcher', 'articles'])

    as_of = datetime.now(timezone.utc)
    instants = {'stale': as_of - timedelta(days=7), 'inside': as_of - timedelta(hours=1),
                'future': as_of + timedelta(days=7),
                'offset-inside': (as_of - timedelta(hours=1)).astimezone(timezone(timedelta(hours=-7)))}
    instant_rows = []
    for label, instant in instants.items():
        article = Article('AI timestamp ' + label, 'https://fixture.invalid/' + label, 'fixture', 'news', published_at=instant)
        start = datetime.now(timezone.utc)
        result, count = cli._drop_stale([article], 24)
        end = datetime.now(timezone.utc)
        instant_rows.append({'condition': label, 'published_at': instant, 'before': start, 'after': end,
                             'kept': bool(result), 'dropped': count, 'candidate_line': article.as_candidate_line(0)})
    write(CAPTURE / 'instants.json', instant_rows)

    instant = datetime(2026, 9, 10, 14, tzinfo=timezone.utc)
    equivalent = [Article('AI timestamp UTC', 'https://fixture.invalid/utc', 'fixture', 'news', published_at=instant),
                  Article('AI timestamp offset', 'https://fixture.invalid/offset', 'fixture', 'news',
                          published_at=instant.astimezone(timezone(timedelta(hours=-7))))]
    write(CAPTURE / 'timezone.json', [{'published_at': article.published_at, 'line': article.as_candidate_line(i)}
                                    for i, article in enumerate(equivalent)])
    (CAPTURE / 'timezone-curator-prompt.txt').write_text(curate._build_prompt(equivalent, top_n=2))

    paths = []
    for name, environment in [('default', {}), ('xdg', {'XDG_DATA_HOME': '~/.cache/publication-xdg'}),
                              ('explicit', {'NEWSROOM_DATA_DIR': '~/publication-history'})]:
        os.environ.pop('NEWSROOM_DATA_DIR', None)
        os.environ.pop('XDG_DATA_HOME', None)
        os.environ.update(environment)
        loaded = config.load_config('/source')
        paths.append({'condition': name, 'environment': environment, 'data_dir': str(loaded.data_dir),
                      'resolved': str(loaded.data_dir.resolve()), 'exists': loaded.data_dir.is_dir()})
    write(CAPTURE / 'paths.json', paths)
    loaded = []
    for module in list(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name and name.startswith('/source/'):
            loaded.append({'path': name, 'sha256': hashlib.sha256(Path(name).read_bytes()).hexdigest()})
    write(CAPTURE / 'loaded-source.json', sorted(loaded, key=lambda row: row['path']))
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    write(CAPTURE / 'http-requests.json', requests)
