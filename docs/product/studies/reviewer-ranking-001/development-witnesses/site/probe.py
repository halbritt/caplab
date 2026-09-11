"""Build and serve original site code; observe real HTTP and browser output."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, '/source')
from newsroom.model import Article
from newsroom.publication import PublicationStore
from newsroom.site import build_site

ROOT = Path('/capture')
store = PublicationStore(ROOT / 'publication.db')
article = Article('<script>fixture()</script> Local model release', 'https://example.invalid/research?a=1&b=2', 'A&B', 'github')
store.record_selection([SimpleNamespace(url=article.url, why='<img src=x onerror=fixture()>')], [article], '2026-09-08', 'main')
site = build_site(store, ROOT / 'public', 'https://newsroom.example')
(site / '.env').write_text('synthetic-private-fixture\n')
(site / 'leak.txt').symlink_to(ROOT / 'publication.db')
(site / 'escape.svg').symlink_to(ROOT / 'publication.db')
database_hash = hashlib.sha256((ROOT / 'publication.db').read_bytes()).hexdigest()
ignore_root = ROOT / 'ignore-check'
ignore_root.mkdir()
(ignore_root / '.gitignore').write_bytes(Path('/source/.gitignore').read_bytes())
subprocess.run(['/usr/bin/git','-c','init.templateDir=','-c','init.defaultBranch=main','init','--quiet',str(ignore_root)],check=True)
ignored = subprocess.run(['/usr/bin/git','-C',str(ignore_root),'-c','core.excludesFile=/dev/null',
    'check-ignore','--no-index','.playwright-mcp/probe.txt','newsroom/site.py'],capture_output=True)
if ignored.returncode not in (0,1):raise RuntimeError('ignore-rule check failed')
command = ['/usr/bin/python3','-B','-m','newsroom.site','--root',str(site),'--port','3913']
responses = []

def fetch(path, method='GET'):
    request = Request('http://127.0.0.1:3913'+path, data=b'fixture' if method=='POST' else None, method=method)
    try:
        response = urlopen(request, timeout=3)
    except HTTPError as error:
        response = error
    with response:
        body = response.read()
        item = {'path':path,'method':method,'status':response.status,'headers':dict(response.headers),
                'body_sha256':hashlib.sha256(body).hexdigest(),'body_bytes':len(body)}
        return item, body

with (ROOT / 'server.stdout').open('wb') as out, (ROOT / 'server.stderr').open('wb') as err:
    server = subprocess.Popen(command, stdout=out, stderr=err, env={'PATH':'/usr/bin:/bin','PYTHONPATH':'/source','PYTHONDONTWRITEBYTECODE':'1'})
    try:
        deadline = time.monotonic()+5
        while True:
            if server.poll() is not None:
                raise RuntimeError('original server exited before readiness')
            try:
                ready, _ = fetch('/')
                if ready['status']!=200:raise RuntimeError('original site unavailable')
                break
            except URLError:
                if time.monotonic()>=deadline:raise
                time.sleep(.05)
        for path in ('/','/about/','/style.css','/feed.xml','/icon.svg','/.env','/publication.db','/%2e%2e/publication.db','/leak.txt','/escape.svg','/drafts/'):
            item, body = fetch(path)
            responses.append(item)
            (ROOT / ('response-'+str(len(responses))+'.body')).write_bytes(body)
        item, body = fetch('/', 'POST')
        responses.append(item)
        (ROOT / 'response-12.body').write_bytes(body)
        browser = subprocess.run(['/usr/bin/node','/witness/browser.cjs'],capture_output=True,timeout=60)
        (ROOT / 'browser.stdout').write_bytes(browser.stdout)
        (ROOT / 'browser.stderr').write_bytes(browser.stderr)
        if browser.returncode:raise RuntimeError('browser failed')
        after = hashlib.sha256((ROOT / 'publication.db').read_bytes()).hexdigest()
        (ROOT / 'observation.json').write_text(json.dumps({'role':sys.argv[1],'server_command':command,
            'responses':responses,'database_before':database_hash,'database_after':after,
            'ignore_check':{'returncode':ignored.returncode,'paths':ignored.stdout.decode().splitlines()},
            'generation':str(site.resolve()),'stories':store.stories()},indent=2,sort_keys=True)+'\n')
    finally:
        server.terminate()
        server.wait(timeout=5)
        (ROOT / 'server-completion.json').write_text(json.dumps({'returncode':server.returncode})+'\n')
